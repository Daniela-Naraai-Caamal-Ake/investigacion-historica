"""
Pruebas para tools/validar_citas.py
=====================================
Validan las funciones de análisis de datos locales (sin acceso a internet):
- _texto_breve
- _tiene_fuente
- extraer_urls_catalogo
- extraer_registros_sin_fuente
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

# Agregar tools/ al path para importar el módulo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools"))

import validar_citas as vc


# ─── _texto_breve ─────────────────────────────────────────────────────────────

class TestTextoBreve(unittest.TestCase):

    def test_texto_corto_sin_truncar(self):
        texto = "Hola mundo"
        resultado = vc._texto_breve(texto, max_chars=100)
        self.assertEqual(resultado, "Hola mundo")

    def test_texto_exactamente_en_limite_sin_truncar(self):
        texto = "A" * 500
        resultado = vc._texto_breve(texto, max_chars=500)
        self.assertEqual(resultado, texto)
        self.assertFalse(resultado.endswith("…"))

    def test_texto_largo_truncado_con_puntos(self):
        texto = "A" * 600
        resultado = vc._texto_breve(texto, max_chars=500)
        self.assertTrue(resultado.endswith("…"))
        self.assertLessEqual(len(resultado), 504)  # 500 chars + "…" (3 bytes UTF-8, 1 char)

    def test_texto_vacio(self):
        self.assertEqual(vc._texto_breve("", max_chars=100), "")

    def test_max_chars_personalizado(self):
        texto = "Hopelchén en Campeche"
        resultado = vc._texto_breve(texto, max_chars=10)
        self.assertTrue(resultado.endswith("…"))
        self.assertLessEqual(len(resultado), 14)


# ─── _tiene_fuente ────────────────────────────────────────────────────────────

class TestTieneFuente(unittest.TestCase):

    def test_registro_con_campo_fuente(self):
        registro = {"fuente": {"nombre": "INAH", "url": "https://inah.gob.mx"}}
        self.assertTrue(vc._tiene_fuente(registro))

    def test_registro_con_fuente_academica(self):
        registro = {"fuente_academica": "Smith, J. (2020). Historia."}
        self.assertTrue(vc._tiene_fuente(registro))

    def test_registro_con_fuente_primaria(self):
        registro = {"fuente_primaria": "AGI, Sevilla, México 3050"}
        self.assertTrue(vc._tiene_fuente(registro))

    def test_registro_con_fuente_secundaria(self):
        registro = {"fuente_secundaria": "Roys (1957)"}
        self.assertTrue(vc._tiene_fuente(registro))

    def test_registro_con_fuentes_lista(self):
        registro = {"fuentes": ["F001", "FX007"]}
        self.assertTrue(vc._tiene_fuente(registro))

    def test_registro_sin_fuente(self):
        registro = {
            "registro_id": "010-A",
            "subtitulo": "Sin fuente",
            "descripcion": "Descripción sin fuente",
        }
        self.assertFalse(vc._tiene_fuente(registro))

    def test_registro_con_fuente_vacia(self):
        # Campo presente pero vacío → no cuenta como fuente
        registro = {"fuente": "", "fuente_academica": None}
        self.assertFalse(vc._tiene_fuente(registro))

    def test_registro_con_campo_no_fuente(self):
        registro = {"titulo": "Texto", "descripcion": "Desc", "tags": ["maya"]}
        self.assertFalse(vc._tiene_fuente(registro))

    def test_registro_con_fuente_1(self):
        registro = {"fuente_1": "Alguna fuente"}
        self.assertTrue(vc._tiene_fuente(registro))


# ─── extraer_urls_catalogo ────────────────────────────────────────────────────

class TestExtraerUrlsCatalogo(unittest.TestCase):

    def _catalogo_temporal(self, contenido: str) -> Path:
        """Crea un archivo temporal de catálogo y parchea la constante."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        tmp.write(contenido)
        tmp.close()
        return Path(tmp.name)

    def tearDown(self):
        # Restaurar la constante original
        vc.FUENTES_CATALOGO = Path(__file__).resolve().parent.parent / "fuentes" / "catalogo_fuentes.md"

    def test_extrae_una_url_simple(self):
        catalogo = textwrap.dedent("""\
            ## F001 — Ejemplo

            | URL | https://example.com/recurso |
        """)
        path = self._catalogo_temporal(catalogo)
        vc.FUENTES_CATALOGO = path
        try:
            resultados = vc.extraer_urls_catalogo()
            self.assertEqual(len(resultados), 1)
            self.assertEqual(resultados[0]["fuente_id"], "F001")
            self.assertIn("example.com", resultados[0]["url"])
        finally:
            os.unlink(path)

    def test_extrae_multiples_fuentes(self):
        catalogo = textwrap.dedent("""\
            ## F001 — Primera fuente

            Más información en https://primera.org/recurso.

            ## FX002 — Segunda fuente

            Ver también https://segunda.com/pagina y https://tercera.net/doc.
        """)
        path = self._catalogo_temporal(catalogo)
        vc.FUENTES_CATALOGO = path
        try:
            resultados = vc.extraer_urls_catalogo()
            ids = [r["fuente_id"] for r in resultados]
            self.assertIn("F001", ids)
            self.assertIn("FX002", ids)
            fx_urls = [r["url"] for r in resultados if r["fuente_id"] == "FX002"]
            self.assertEqual(len(fx_urls), 2)
        finally:
            os.unlink(path)

    def test_no_duplica_urls_por_seccion(self):
        catalogo = textwrap.dedent("""\
            ## F001 — Con URL repetida

            Ver https://repetida.com/x y también https://repetida.com/x aquí.
        """)
        path = self._catalogo_temporal(catalogo)
        vc.FUENTES_CATALOGO = path
        try:
            resultados = vc.extraer_urls_catalogo()
            urls = [r["url"] for r in resultados]
            self.assertEqual(len(urls), len(set(urls)))
        finally:
            os.unlink(path)

    def test_catalogo_vacio_devuelve_lista_vacia(self):
        catalogo = "# Sin fuentes\n\nNada aquí.\n"
        path = self._catalogo_temporal(catalogo)
        vc.FUENTES_CATALOGO = path
        try:
            resultados = vc.extraer_urls_catalogo()
            self.assertEqual(resultados, [])
        finally:
            os.unlink(path)

    def test_archivo_inexistente_devuelve_lista_vacia(self):
        vc.FUENTES_CATALOGO = Path("/tmp/no_existe_catalogo_xyz.md")
        resultados = vc.extraer_urls_catalogo()
        self.assertEqual(resultados, [])


# ─── extraer_registros_sin_fuente ─────────────────────────────────────────────

class TestExtraerRegistrosSinFuente(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._orig_datos = vc.DATOS_HOPELCHEN
        vc.DATOS_HOPELCHEN = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        vc.DATOS_HOPELCHEN = self._orig_datos

    def _escribir_nodo(self, nombre: str, datos: dict) -> None:
        path = Path(self.tmpdir) / nombre
        path.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")

    def test_nodo_con_todas_fuentes_no_devuelve_registros(self):
        self._escribir_nodo("HOPELCHEN_NODO_T01_Test.json", {
            "nodo_id": "T01",
            "registros": [
                {"registro_id": "T01-A", "fuente": {"nombre": "INAH"}},
                {"registro_id": "T01-B", "fuente_academica": "Smith 2020"},
            ],
        })
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(resultado, [])

    def test_nodo_sin_fuentes_devuelve_registros(self):
        self._escribir_nodo("HOPELCHEN_NODO_T02_Test.json", {
            "nodo_id": "T02",
            "registros": [
                {"registro_id": "T02-A", "subtitulo": "Sin fuente", "descripcion": "X"},
                {"registro_id": "T02-B", "subtitulo": "También sin fuente"},
            ],
        })
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(len(resultado), 2)
        ids = {r["registro_id"] for r in resultado}
        self.assertIn("T02-A", ids)
        self.assertIn("T02-B", ids)

    def test_nodo_mixto_devuelve_solo_sin_fuente(self):
        self._escribir_nodo("HOPELCHEN_NODO_T03_Test.json", {
            "nodo_id": "T03",
            "registros": [
                {"registro_id": "T03-A", "fuente": {"nombre": "INAH"}},
                {"registro_id": "T03-B", "descripcion": "Sin fuente"},
            ],
        })
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["registro_id"], "T03-B")

    def test_json_malformado_se_omite(self):
        path = Path(self.tmpdir) / "HOPELCHEN_NODO_BAD_Test.json"
        path.write_text("{bad json", encoding="utf-8")
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(resultado, [])

    def test_nodo_sin_registros_no_falla(self):
        self._escribir_nodo("HOPELCHEN_NODO_T04_Test.json", {
            "nodo_id": "T04",
            "registros": [],
        })
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(resultado, [])

    def test_filtro_por_solo_nodo(self):
        self._escribir_nodo("HOPELCHEN_NODO_001_Test.json", {
            "nodo_id": "001",
            "registros": [{"registro_id": "001-A", "descripcion": "Sin fuente"}],
        })
        self._escribir_nodo("HOPELCHEN_NODO_002_Test.json", {
            "nodo_id": "002",
            "registros": [{"registro_id": "002-A", "descripcion": "Sin fuente"}],
        })
        resultado = vc.extraer_registros_sin_fuente(solo_nodo="001")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["nodo_id"], "001")

    def test_resultado_incluye_campos_esperados(self):
        self._escribir_nodo("HOPELCHEN_NODO_T05_Test.json", {
            "nodo_id": "T05",
            "registros": [{
                "registro_id": "T05-A",
                "subtitulo": "Un subtítulo",
                "fecha_evento": "1848",
                "lugar": "Hopelchén",
            }],
        })
        resultado = vc.extraer_registros_sin_fuente()
        self.assertEqual(len(resultado), 1)
        r = resultado[0]
        self.assertEqual(r["nodo_id"], "T05")
        self.assertEqual(r["registro_id"], "T05-A")
        self.assertEqual(r["subtitulo"], "Un subtítulo")
        self.assertEqual(r["fecha_evento"], "1848")
        self.assertEqual(r["lugar"], "Hopelchén")


if __name__ == "__main__":
    unittest.main()
