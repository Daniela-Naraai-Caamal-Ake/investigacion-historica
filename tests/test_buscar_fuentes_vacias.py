"""
Pruebas para tools/buscar_fuentes_vacias.py
============================================
Validan la detección de registros sin fuente y la construcción de consultas
de búsqueda, sin necesidad de acceso a internet.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Agregar tools/ al path para importar el módulo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools"))

import buscar_fuentes_vacias as bfv


# ─── Datos de prueba ──────────────────────────────────────────────────────────

_NODO_CON_FUENTE = {
    "nodo_id": "T01",
    "titulo": "Nodo de prueba con fuente",
    "rango_temporal": "2000–2026",
    "registros": [
        {
            "registro_id": "T01-A",
            "subtitulo": "Registro con fuente explícita",
            "descripcion": "Este registro tiene fuente.",
            "fuente": {
                "nombre": "Wikipedia",
                "url": "https://es.wikipedia.org",
            },
        },
        {
            "registro_id": "T01-B",
            "subtitulo": "Registro con fuente_academica",
            "descripcion": "Este registro tiene fuente académica.",
            "fuente_academica": "Smith, J. (2020). Historia. Revista X.",
        },
    ],
}

_NODO_SIN_FUENTE = {
    "nodo_id": "T02",
    "titulo": "Nodo de prueba sin fuente",
    "rango_temporal": "1900–1950",
    "registros": [
        {
            "registro_id": "T02-A",
            "subtitulo": "Economía chiclera en Los Chenes",
            "descripcion": "La industria chiclera dominó la economía de Los Chenes.",
            "lugar": "Hopelchén, Campeche",
            "fecha_evento": "1900–1950",
            "tags": ["chicle", "economía", "Los Chenes"],
            "conexion_hipotesis": "Control económico colonial.",
        },
    ],
}

_NODO_SINTETICO_SIN_FUENTE = {
    "nodo_id": "T03",
    "titulo": "Nodo de síntesis",
    "rango_temporal": "1500–2026",
    "registros": [
        {
            "registro_id": "T03-A",
            "subtitulo": "CRUCE TRANSVERSAL: Patrón de resistencia maya",
            "descripcion": (
                "Al cruzar los registros de los Nodos 001-009, emerge un patrón "
                "de resistencia maya con cinco formas documentadas."
            ),
            "lugar": "Los Chenes, Hopelchén, Campeche",
            "fecha_evento": "1669 — 2026",
            "tipo_dato": "Análisis transversal de síntesis",
        },
    ],
}

_NODO_FUENTES_LISTA = {
    "nodo_id": "T04",
    "titulo": "Nodo con fuentes en lista",
    "rango_temporal": "2000–2026",
    "registros": [
        {
            "registro_id": "T04-A",
            "subtitulo": "Registro con fuentes en lista",
            "descripcion": "Este registro tiene campo fuentes.",
            "fuentes": [{"nombre": "Fuente 1", "url": "https://example.com"}],
        },
    ],
}

_NODO_FUENTE_VACIA = {
    "nodo_id": "T05",
    "titulo": "Nodo con fuente vacía",
    "rango_temporal": "2000–2026",
    "registros": [
        {
            "registro_id": "T05-A",
            "subtitulo": "Registro con fuente vacía",
            "descripcion": "Este registro tiene fuente vacía (string vacío).",
            "fuente": "",
        },
        {
            "registro_id": "T05-B",
            "subtitulo": "Registro con fuente None",
            "descripcion": "Este registro tiene fuente None.",
            "fuente": None,
        },
    ],
}


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestTieneFuente(unittest.TestCase):
    """Pruebas para la función _tiene_fuente."""

    def test_fuente_dict(self):
        reg = {"registro_id": "x", "fuente": {"nombre": "Wikipedia"}}
        self.assertTrue(bfv._tiene_fuente(reg))

    def test_fuente_string(self):
        reg = {"registro_id": "x", "fuente": "Smith, J. (2020)."}
        self.assertTrue(bfv._tiene_fuente(reg))

    def test_fuente_lista(self):
        reg = {"registro_id": "x", "fuentes": [{"nombre": "Algo"}]}
        self.assertTrue(bfv._tiene_fuente(reg))

    def test_fuente_academica(self):
        reg = {"registro_id": "x", "fuente_academica": "Jones 2010"}
        self.assertTrue(bfv._tiene_fuente(reg))

    def test_fuente_primaria(self):
        reg = {"registro_id": "x", "fuente_primaria": "AGN Ramo Indios"}
        self.assertTrue(bfv._tiene_fuente(reg))

    def test_sin_fuente(self):
        reg = {"registro_id": "x", "subtitulo": "Sin fuente"}
        self.assertFalse(bfv._tiene_fuente(reg))

    def test_fuente_string_vacio(self):
        reg = {"registro_id": "x", "fuente": ""}
        self.assertFalse(bfv._tiene_fuente(reg))

    def test_fuente_string_solo_espacios(self):
        reg = {"registro_id": "x", "fuente": "   "}
        self.assertFalse(bfv._tiene_fuente(reg))

    def test_fuente_none(self):
        reg = {"registro_id": "x", "fuente": None}
        self.assertFalse(bfv._tiene_fuente(reg))

    def test_fuente_lista_vacia(self):
        reg = {"registro_id": "x", "fuentes": []}
        self.assertFalse(bfv._tiene_fuente(reg))

    def test_fuente_dict_vacio(self):
        reg = {"registro_id": "x", "fuente": {}}
        self.assertFalse(bfv._tiene_fuente(reg))


class TestDetectarRegistrosSinFuente(unittest.TestCase):
    """Pruebas para detectar_registros_sin_fuente usando archivos temporales."""

    def _escribir_nodo(self, tmp_dir: Path, nombre: str, data: dict) -> Path:
        ruta = tmp_dir / nombre
        ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return ruta

    def test_detecta_registro_sin_fuente(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_T02_Test.json", _NODO_SIN_FUENTE)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente()

        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["registro"]["registro_id"], "T02-A")

    def test_no_detecta_registro_con_fuente(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_T01_Test.json", _NODO_CON_FUENTE)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente()

        self.assertEqual(len(resultados), 0)

    def test_detecta_fuente_lista(self):
        """Un registro con 'fuentes' en lista no debe aparecer como sin fuente."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_T04_Test.json", _NODO_FUENTES_LISTA)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente()

        self.assertEqual(len(resultados), 0)

    def test_detecta_fuente_vacia_como_sin_fuente(self):
        """Un campo fuente con string vacío o None debe detectarse como sin fuente."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_T05_Test.json", _NODO_FUENTE_VACIA)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente()

        self.assertEqual(len(resultados), 2)

    def test_filtro_nodo(self):
        """El filtro --nodo debe restringir la búsqueda al nodo indicado."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_004_Test.json", _NODO_SIN_FUENTE)
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_006_Test.json", _NODO_SIN_FUENTE)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente(filtro_nodo="004")

        # Solo debe retornar el nodo 004
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["archivo"], "HOPELCHEN_NODO_004_Test.json")

    def test_json_invalido_no_falla(self):
        """Un JSON inválido en el directorio no debe detener la detección."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "HOPELCHEN_NODO_BAD_Test.json").write_text(
                "{ invalid json }", encoding="utf-8"
            )
            self._escribir_nodo(tmp_path, "HOPELCHEN_NODO_T02_Valid.json", _NODO_SIN_FUENTE)

            with patch.object(bfv, "DATOS_HOPELCHEN", tmp_path):
                resultados = bfv.detectar_registros_sin_fuente()

        # Debe encontrar el registro válido a pesar del JSON roto
        self.assertEqual(len(resultados), 1)


class TestTerminosClave(unittest.TestCase):
    """Pruebas para _terminos_clave."""

    def test_elimina_prefijo_cruce(self):
        texto = "CRUCE DE DATOS: Apellidos del poder en Hopelchén"
        resultado = bfv._terminos_clave(texto)
        self.assertNotIn("CRUCE", resultado.upper())
        self.assertIn("Apellidos", resultado)

    def test_elimina_prefijo_analisis(self):
        texto = "ANÁLISIS TRANSVERSAL. Al cruzar los registros de los Nodos 001-009, emerge un patrón de resistencia maya"
        resultado = bfv._terminos_clave(texto)
        self.assertNotIn("cruzar", resultado.lower())
        self.assertNotIn("nodos", resultado.lower())

    def test_respeta_max_palabras(self):
        texto = "Presidentes municipales de Hopelchén identificados desde 1959"
        resultado = bfv._terminos_clave(texto, max_palabras=3)
        self.assertLessEqual(len(resultado.split()), 3)

    def test_texto_simple_sin_prefijo(self):
        texto = "economía chiclera Los Chenes monopolio"
        resultado = bfv._terminos_clave(texto)
        self.assertIn("chiclera", resultado)


class TestConstruirConsultas(unittest.TestCase):
    """Pruebas para _construir_consultas."""

    def _entrada(self, reg: dict) -> dict:
        return {
            "archivo": "HOPELCHEN_NODO_T02_Test.json",
            "nodo_id": "T02",
            "titulo_nodo": "Nodo de prueba",
            "registro": reg,
        }

    def test_genera_consulta_wikipedia_es(self):
        entrada = self._entrada(_NODO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        motores = [c["motor"] for c in consultas]
        self.assertIn("wikipedia_es", motores)

    def test_genera_consulta_duckduckgo(self):
        entrada = self._entrada(_NODO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        motores = [c["motor"] for c in consultas]
        self.assertIn("duckduckgo", motores)

    def test_genera_consulta_openlibrary_con_tags(self):
        """Si el registro tiene tags, debe haber una consulta a OpenLibrary."""
        entrada = self._entrada(_NODO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        motores = [c["motor"] for c in consultas]
        self.assertIn("openlibrary", motores)

    def test_genera_wikipedia_en_para_chicle(self):
        """Registros con 'chicle' deben generar búsqueda en Wikipedia EN."""
        entrada = self._entrada(_NODO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        motores = [c["motor"] for c in consultas]
        self.assertIn("wikipedia_en", motores)

    def test_sintetico_no_usa_prefijo_en_query(self):
        """Registros de síntesis no deben incluir 'CRUCE' en las queries."""
        entrada = self._entrada(_NODO_SINTETICO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        for c in consultas:
            self.assertNotIn("CRUCE", c["query"].upper(),
                             f"Query contiene CRUCE: {c['query']}")

    def test_registro_con_fuentes_no_consultadas(self):
        """Registros con 'fuentes_identificadas_no_consultadas' generan búsquedas en OpenLibrary."""
        reg = {
            "registro_id": "007-H",
            "subtitulo": "Bibliografía de Schüren (2013)",
            "descripcion": "Fuentes no consultadas.",
            "lugar": "Los Chenes, Campeche",
            "fecha_evento": "1923 — 2013",
            "fuentes_identificadas_no_consultadas": [
                {"autor": "Schuller, Rodolfo", "año": "1923",
                 "titulo": "Diario de viaje por Campeche"},
            ],
        }
        entrada = self._entrada(reg)
        consultas = bfv._construir_consultas(entrada)
        ol_queries = [c["query"] for c in consultas if c["motor"] == "openlibrary"]
        self.assertTrue(
            any("Schuller" in q for q in ol_queries),
            f"Ninguna query de OpenLibrary menciona 'Schuller': {ol_queries}",
        )

    def test_todas_las_consultas_tienen_campos_requeridos(self):
        """Todas las consultas deben tener 'motor', 'query' y 'descripcion'."""
        entrada = self._entrada(_NODO_SIN_FUENTE["registros"][0])
        consultas = bfv._construir_consultas(entrada)
        for c in consultas:
            self.assertIn("motor", c)
            self.assertIn("query", c)
            self.assertIn("descripcion", c)
            self.assertTrue(c["query"].strip(), f"Query vacía: {c}")


class TestProcesarRegistroModoSeco(unittest.TestCase):
    """Pruebas para procesar_registro en modo seco (sin búsquedas reales)."""

    def _entrada(self) -> dict:
        return {
            "archivo": "HOPELCHEN_NODO_T02_Test.json",
            "nodo_id": "T02",
            "titulo_nodo": "Nodo de prueba",
            "registro": _NODO_SIN_FUENTE["registros"][0],
        }

    def test_modo_seco_no_ejecuta_busquedas(self):
        entrada = self._entrada()
        resultado = bfv.procesar_registro(entrada, modo_seco=True)
        for b in resultado["busquedas"]:
            self.assertEqual(b["estado"], "no_ejecutado (modo_seco)")
            self.assertEqual(b["resultados"], [])

    def test_resultado_tiene_campos_requeridos(self):
        entrada = self._entrada()
        resultado = bfv.procesar_registro(entrada, modo_seco=True)
        self.assertIn("registro_id", resultado)
        self.assertIn("archivo", resultado)
        self.assertIn("nodo_id", resultado)
        self.assertIn("busquedas", resultado)
        self.assertIn("fuentes_candidatas", resultado)
        self.assertIn("total_candidatas", resultado)
        self.assertIn("nota", resultado)

    def test_fuentes_candidatas_vacio_en_modo_seco(self):
        entrada = self._entrada()
        resultado = bfv.procesar_registro(entrada, modo_seco=True)
        # En modo seco no hay búsquedas reales → no hay candidatas
        self.assertEqual(resultado["fuentes_candidatas"], [])
        self.assertEqual(resultado["total_candidatas"], 0)


class TestGuardarReporte(unittest.TestCase):
    """Pruebas para la generación del reporte JSON."""

    def test_reporte_se_crea(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(bfv, "DATOS_INVESTIGACION", Path(tmp)):
                with patch.object(bfv, "ROOT", Path(tmp).parent):
                    resultados = [
                        {
                            "registro_id": "T02-A",
                            "archivo": "HOPELCHEN_NODO_T02_Test.json",
                            "nodo_id": "T02",
                            "subtitulo": "Prueba",
                            "busquedas": [],
                            "fuentes_candidatas": [],
                            "total_candidatas": 0,
                            "nota": "Prueba",
                        }
                    ]
                    ruta = bfv.guardar_reporte(resultados, registros_detectados=1)

            # La aserción debe hacerse ANTES de salir del TemporaryDirectory
            self.assertTrue(ruta.exists())
            with open(ruta, encoding="utf-8") as f:
                data = json.load(f)

        self.assertEqual(data["resumen"]["registros_sin_fuente_detectados"], 1)
        self.assertEqual(len(data["resultados"]), 1)
        self.assertIn("nota_metodologica", data)


class TestIntegracionArchivoReal(unittest.TestCase):
    """
    Prueba de integración: detecta los registros sin fuente en los archivos
    reales del repositorio. No realiza búsquedas web.
    """

    def test_detecta_registros_conocidos_sin_fuente(self):
        """Los 6 registros sin fuente conocidos deben ser detectados."""
        entradas = bfv.detectar_registros_sin_fuente()
        ids_encontrados = {e["registro"]["registro_id"] for e in entradas}
        ids_esperados = {"004-C", "006-A", "006-G", "007-H", "009-G", "010-G"}
        self.assertEqual(
            ids_encontrados, ids_esperados,
            f"IDs sin fuente encontrados: {ids_encontrados}\n"
            f"IDs sin fuente esperados: {ids_esperados}",
        )

    def test_metadatos_de_entrada(self):
        """Cada entrada debe tener los campos requeridos."""
        entradas = bfv.detectar_registros_sin_fuente()
        for e in entradas:
            self.assertIn("archivo", e)
            self.assertIn("nodo_id", e)
            self.assertIn("titulo_nodo", e)
            self.assertIn("registro", e)
            self.assertIsInstance(e["registro"], dict)


class TestBuscarFirecrawl(unittest.TestCase):
    """Pruebas para _buscar_firecrawl con FirecrawlApp simulado."""

    def _hacer_doc(self, titulo: str, url: str, descripcion: str = "") -> MagicMock:
        """Crea un objeto documento simulado de Firecrawl."""
        doc = MagicMock()
        doc.model_dump.return_value = {
            "url": url,
            "markdown": f"# {titulo}\n\nContenido de ejemplo.",
            "metadata": {
                "title": titulo,
                "description": descripcion,
            },
        }
        return doc

    def test_retorna_lista_vacia_sin_sdk(self):
        """Si firecrawl-py no está instalado, retorna lista vacía."""
        with patch.object(bfv, "_FIRECRAWL_OK", False):
            resultado = bfv._buscar_firecrawl("Hopelchén historia", api_key="fc-test")
        self.assertEqual(resultado, [])

    def test_retorna_resultados_con_sdk(self):
        """Con SDK simulado, debe retornar resultados correctamente."""
        mock_resp = MagicMock()
        mock_resp.data = [
            self._hacer_doc(
                "Historia de Hopelchén",
                "https://es.wikipedia.org/wiki/Hopelch%C3%A9n",
                "Municipio de Campeche, México.",
            ),
            self._hacer_doc(
                "Los Chenes — Región arqueológica",
                "https://example.com/chenes",
            ),
        ]
        mock_app = MagicMock()
        mock_app.search.return_value = mock_resp

        with patch.object(bfv, "_FIRECRAWL_OK", True):
            with patch.object(bfv, "_FirecrawlApp", return_value=mock_app):
                resultado = bfv._buscar_firecrawl("Hopelchén historia", api_key="fc-test")

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]["titulo"], "Historia de Hopelchén")
        self.assertEqual(
            resultado[0]["url"],
            "https://es.wikipedia.org/wiki/Hopelch%C3%A9n",
        )
        self.assertIn("descripcion", resultado[0])
        self.assertIn("extracto", resultado[0])

    def test_retorna_lista_vacia_en_error(self):
        """Si la API lanza excepción, retorna lista vacía sin propagar el error."""
        mock_app = MagicMock()
        mock_app.search.side_effect = Exception("connection refused")

        with patch.object(bfv, "_FIRECRAWL_OK", True):
            with patch.object(bfv, "_FirecrawlApp", return_value=mock_app):
                resultado = bfv._buscar_firecrawl("query", api_key="fc-test")

        self.assertEqual(resultado, [])

    def test_ejecutar_consulta_firecrawl_sin_clave(self):
        """Si no hay clave API, ejecutar_consulta debe marcar estado 'sin_clave_api'."""
        consulta = {
            "motor": "firecrawl",
            "query": "Hopelchén resistencia maya",
            "descripcion": "Test sin clave",
        }
        with patch.object(bfv, "_FIRECRAWL_API_KEY", None):
            resultado = bfv.ejecutar_consulta(consulta)

        self.assertEqual(resultado["estado"], "sin_clave_api")
        self.assertEqual(resultado["resultados"], [])

    def test_ejecutar_consulta_firecrawl_con_clave(self):
        """Con clave y SDK simulado, ejecutar_consulta debe retornar resultados."""
        mock_resp = MagicMock()
        mock_resp.data = [
            self._hacer_doc("Resultado Firecrawl", "https://example.com/fc"),
        ]
        mock_app = MagicMock()
        mock_app.search.return_value = mock_resp

        consulta = {
            "motor": "firecrawl",
            "query": "Hopelchén historia",
            "descripcion": "Test con clave",
        }
        with patch.object(bfv, "_FIRECRAWL_OK", True):
            with patch.object(bfv, "_FIRECRAWL_API_KEY", "fc-test-key"):
                with patch.object(bfv, "_FirecrawlApp", return_value=mock_app):
                    resultado = bfv.ejecutar_consulta(consulta)

        self.assertEqual(resultado["estado"], "ok")
        self.assertEqual(resultado["total_resultados"], 1)

    def test_construir_consultas_incluye_firecrawl_con_clave(self):
        """Con clave y SDK disponibles, _construir_consultas debe incluir motor firecrawl."""
        entrada = {
            "archivo": "HOPELCHEN_NODO_T02_Test.json",
            "nodo_id": "T02",
            "titulo_nodo": "Nodo de prueba",
            "registro": _NODO_SIN_FUENTE["registros"][0],
        }
        with patch.object(bfv, "_FIRECRAWL_API_KEY", "fc-test-key"):
            with patch.object(bfv, "_FIRECRAWL_OK", True):
                consultas = bfv._construir_consultas(entrada)

        motores = [c["motor"] for c in consultas]
        self.assertIn("firecrawl", motores)

    def test_construir_consultas_omite_firecrawl_sin_clave(self):
        """Sin clave API, _construir_consultas no debe incluir motor firecrawl."""
        entrada = {
            "archivo": "HOPELCHEN_NODO_T02_Test.json",
            "nodo_id": "T02",
            "titulo_nodo": "Nodo de prueba",
            "registro": _NODO_SIN_FUENTE["registros"][0],
        }
        with patch.object(bfv, "_FIRECRAWL_API_KEY", None):
            consultas = bfv._construir_consultas(entrada)

        motores = [c["motor"] for c in consultas]
        self.assertNotIn("firecrawl", motores)


if __name__ == "__main__":
    unittest.main()
