"""
Pruebas para tools/verificar_sincronizacion.py y la extracción
genérica de preguntas de actualizar_vacios.py y grafo_epistemologico.py.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Añadir tools/ al path
TOOLS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")
sys.path.insert(0, TOOLS)

from verificar_sincronizacion import (
    cargar_todas_las_preguntas,
    extraer_preguntas_de_datos,
    leer_estados_vacios_md,
    verificar_resumen_vacios,
    verificar_vacios,
)
from actualizar_vacios import _extraer_preguntas as actualizar_extraer
from grafo_epistemologico import _extraer_preguntas_de_archivo as grafo_extraer


# ---------------------------------------------------------------------------
# Datos de prueba
# ---------------------------------------------------------------------------

DATOS_PREGUNTAS_SIMPLE = {
    "preguntas": [
        {"pregunta_id": "P001-01", "pregunta": "¿Pregunta A?", "estado": "RESPONDIDA"},
        {"pregunta_id": "P001-02", "pregunta": "¿Pregunta B?", "estado": "PENDIENTE"},
    ]
}

DATOS_PREGUNTAS_VARIANTE = {
    "preguntas_urgentes": [
        {"pregunta_id": "P003-01", "pregunta": "¿Urgente A?", "estado": "RESPONDIDA PARCIALMENTE"},
    ],
    "preguntas_urgentes_005": [
        {"pregunta_id": "P005-01", "pregunta": "¿Urgente 005?", "estado": "PENDIENTE"},
        {"pregunta_id": "P005-02", "pregunta": "¿Otra 005?", "estado": "PENDIENTE"},
    ],
    "preguntas_otra_lista": [
        # Esta lista NO tiene pregunta_id → debe ser ignorada
        {"nombre": "dato sin pregunta_id"},
    ],
    "otra_clave": [
        {"pregunta_id": "NO-DEBE-APARECER", "pregunta": "No empieza con preguntas"},
    ],
}

DATOS_SIN_PREGUNTAS = {
    "titulo": "Sin preguntas",
    "registros": [{"id": "001-A"}],
}


# ---------------------------------------------------------------------------
# Tests de extraer_preguntas_de_datos (verificar_sincronizacion)
# ---------------------------------------------------------------------------

class TestExtraerPreguntas(unittest.TestCase):

    def test_extrae_de_clave_preguntas(self):
        pregs = extraer_preguntas_de_datos(DATOS_PREGUNTAS_SIMPLE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertIn("P001-01", ids)
        self.assertIn("P001-02", ids)
        self.assertEqual(len(pregs), 2)

    def test_extrae_de_preguntas_urgentes(self):
        data = {"preguntas_urgentes": [
            {"pregunta_id": "P003-01", "pregunta": "?", "estado": "PENDIENTE"},
        ]}
        pregs = extraer_preguntas_de_datos(data)
        self.assertEqual(len(pregs), 1)
        self.assertEqual(pregs[0]["pregunta_id"], "P003-01")

    def test_extrae_de_clave_variante_005(self):
        """La clave preguntas_urgentes_005 debe ser descubierta automáticamente."""
        pregs = extraer_preguntas_de_datos(DATOS_PREGUNTAS_VARIANTE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertIn("P003-01", ids)
        self.assertIn("P005-01", ids)
        self.assertIn("P005-02", ids)

    def test_ignora_entradas_sin_pregunta_id(self):
        """Entradas sin pregunta_id no deben aparecer."""
        pregs = extraer_preguntas_de_datos(DATOS_PREGUNTAS_VARIANTE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertNotIn("NO-DEBE-APARECER", ids)

    def test_deduplicacion(self):
        """Misma pregunta_id en dos claves no debe duplicarse."""
        data = {
            "preguntas": [
                {"pregunta_id": "P001-01", "estado": "PENDIENTE"},
            ],
            "preguntas_urgentes": [
                {"pregunta_id": "P001-01", "estado": "RESPONDIDA"},  # duplicada
            ],
        }
        pregs = extraer_preguntas_de_datos(data)
        self.assertEqual(len(pregs), 1)
        # La primera aparición (preguntas) debe prevalecer
        self.assertEqual(pregs[0]["estado"], "PENDIENTE")

    def test_datos_sin_preguntas(self):
        pregs = extraer_preguntas_de_datos(DATOS_SIN_PREGUNTAS)
        self.assertEqual(pregs, [])

    def test_datos_vacio(self):
        pregs = extraer_preguntas_de_datos({})
        self.assertEqual(pregs, [])


# ---------------------------------------------------------------------------
# Tests de _extraer_preguntas en actualizar_vacios (misma lógica)
# ---------------------------------------------------------------------------

class TestActualizarExtraer(unittest.TestCase):

    def test_extrae_clave_urgentes_005(self):
        """actualizar_vacios._extraer_preguntas debe encontrar preguntas_urgentes_005."""
        pregs = actualizar_extraer(DATOS_PREGUNTAS_VARIANTE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertIn("P005-01", ids)
        self.assertIn("P005-02", ids)

    def test_extrae_clave_preguntas_simple(self):
        pregs = actualizar_extraer(DATOS_PREGUNTAS_SIMPLE)
        self.assertEqual(len(pregs), 2)

    def test_no_incluye_sin_pregunta_id(self):
        pregs = actualizar_extraer(DATOS_PREGUNTAS_VARIANTE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertNotIn("NO-DEBE-APARECER", ids)


# ---------------------------------------------------------------------------
# Tests de _extraer_preguntas_de_archivo en grafo_epistemologico
# ---------------------------------------------------------------------------

class TestGrafoExtraer(unittest.TestCase):

    def test_extrae_clave_urgentes_005(self):
        """grafo_epistemologico._extraer_preguntas_de_archivo debe encontrar preguntas_urgentes_005."""
        pregs = grafo_extraer(DATOS_PREGUNTAS_VARIANTE)
        ids = [p["pregunta_id"] for p in pregs]
        self.assertIn("P005-01", ids)
        self.assertIn("P005-02", ids)

    def test_extrae_clave_preguntas_simple(self):
        pregs = grafo_extraer(DATOS_PREGUNTAS_SIMPLE)
        self.assertEqual(len(pregs), 2)


# ---------------------------------------------------------------------------
# Tests de leer_estados_vacios_md
# ---------------------------------------------------------------------------

VACIOS_MD_EJEMPLO = """\
# VACÍOS

## Resumen estadístico

| Estado | Cantidad |
|--------|----------|
| 🔴 PENDIENTE | 2 |
| 🟠 RESPONDIDA PARCIALMENTE | 1 |
| 🟢 RESPONDIDA | 0 |

## Preguntas

| ID | Pregunta | Nodo | Dónde buscar | Estado |
|----|----------|------|--------------|--------|
| **P001-01** | ¿Pregunta A? | 001 | — | 🟢 RESPONDIDA |
| **P001-02** | ¿Pregunta B? | 001 | — | 🔴 PENDIENTE |
| **P003-01** | ¿Urgente A? | 003 | — | 🟠 RESPONDIDA PARCIALMENTE |
"""


class TestLeerEstadosVaciosMd(unittest.TestCase):

    def _write_vacios(self, contenido: str) -> Path:
        tmp = Path(tempfile.mktemp(suffix=".md"))
        tmp.write_text(contenido, encoding="utf-8")
        return tmp

    def test_parsea_estados(self):
        tmp = self._write_vacios(VACIOS_MD_EJEMPLO)
        try:
            with patch("verificar_sincronizacion.VACIOS_PATH", tmp):
                estados = leer_estados_vacios_md()
            self.assertEqual(estados.get("P001-01"), "RESPONDIDA")
            self.assertEqual(estados.get("P001-02"), "PENDIENTE")
            self.assertEqual(estados.get("P003-01"), "RESPONDIDA PARCIALMENTE")
        finally:
            tmp.unlink(missing_ok=True)

    def test_archivo_inexistente(self):
        with patch("verificar_sincronizacion.VACIOS_PATH", Path("/no/existe.md")):
            estados = leer_estados_vacios_md()
        self.assertEqual(estados, {})


# ---------------------------------------------------------------------------
# Tests de verificar_vacios
# ---------------------------------------------------------------------------

class TestVerificarVacios(unittest.TestCase):

    def _preguntas_json(self, items: list[tuple[str, str]]) -> dict[str, dict]:
        return {
            pid: {
                "estado": estado,
                "prioridad": "Media",
                "pregunta": f"¿{pid}?",
                "archivo": "test.json",
            }
            for pid, estado in items
        }

    def test_sin_inconsistencias(self):
        preguntas = self._preguntas_json([("P001-01", "RESPONDIDA"), ("P001-02", "PENDIENTE")])
        estados_md = {"P001-01": "RESPONDIDA", "P001-02": "PENDIENTE"}
        incs = verificar_vacios(preguntas, estados_md)
        self.assertEqual(incs, [])

    def test_estado_diferente(self):
        preguntas = self._preguntas_json([("P001-01", "RESPONDIDA")])
        estados_md = {"P001-01": "PENDIENTE"}
        incs = verificar_vacios(preguntas, estados_md)
        self.assertEqual(len(incs), 1)
        self.assertEqual(incs[0]["tipo"], "estado_diferente")
        self.assertEqual(incs[0]["pregunta_id"], "P001-01")

    def test_ausente_en_md(self):
        preguntas = self._preguntas_json([("P001-01", "RESPONDIDA"), ("P001-02", "PENDIENTE")])
        estados_md = {"P001-01": "RESPONDIDA"}  # P001-02 ausente
        incs = verificar_vacios(preguntas, estados_md)
        tipos = {i["tipo"] for i in incs}
        self.assertIn("ausente_en_md", tipos)
        ausentes = [i["pregunta_id"] for i in incs if i["tipo"] == "ausente_en_md"]
        self.assertIn("P001-02", ausentes)

    def test_fantasma_en_md(self):
        preguntas = self._preguntas_json([("P001-01", "RESPONDIDA")])
        estados_md = {"P001-01": "RESPONDIDA", "P099-99": "PENDIENTE"}  # P099-99 fantasma
        incs = verificar_vacios(preguntas, estados_md)
        tipos = {i["tipo"] for i in incs}
        self.assertIn("fantasma_en_md", tipos)

    def test_comparacion_insensible_a_mayusculas(self):
        preguntas = self._preguntas_json([("P001-01", "respondida")])
        estados_md = {"P001-01": "RESPONDIDA"}
        incs = verificar_vacios(preguntas, estados_md)
        self.assertEqual(incs, [])

    def test_vacios_vacios(self):
        incs = verificar_vacios({}, {})
        self.assertEqual(incs, [])


# ---------------------------------------------------------------------------
# Tests de integración con los archivos reales del proyecto
# ---------------------------------------------------------------------------

class TestIntegracionReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.preguntas = cargar_todas_las_preguntas()

    def test_carga_74_preguntas(self):
        """Deben cargarse 74 preguntas (incluye las 6 del nodo 005)."""
        self.assertEqual(len(self.preguntas), 74)

    def test_preguntas_005_incluidas(self):
        """Las preguntas P005-01..P005-06 deben estar en el resultado."""
        for i in range(1, 7):
            pid = f"P005-0{i}"
            self.assertIn(pid, self.preguntas, f"{pid} no fue cargada")

    def test_preguntas_005_tienen_estado(self):
        """Las P005 deben tener estado explícito (PENDIENTE)."""
        for i in range(1, 7):
            pid = f"P005-0{i}"
            estado = self.preguntas.get(pid, {}).get("estado", "")
            self.assertTrue(
                estado,
                f"{pid} no tiene campo 'estado'",
            )

    def test_vacios_md_sincronizado(self):
        """VACIOS.md debe estar sincronizado con los JSON (0 discrepancias)."""
        estados_md = leer_estados_vacios_md()
        incs = verificar_vacios(self.preguntas, estados_md)
        diferencias = [i for i in incs if i["tipo"] == "estado_diferente"]
        self.assertEqual(
            diferencias, [],
            f"Hay {len(diferencias)} estados diferentes entre JSON y VACIOS.md: "
            + ", ".join(i["pregunta_id"] for i in diferencias),
        )

    def test_resumen_vacios_md_correcto(self):
        """El resumen estadístico de VACIOS.md debe coincidir con los JSON."""
        inconsistencias = verificar_resumen_vacios(self.preguntas)
        self.assertEqual(
            inconsistencias, [],
            f"Resumen de VACIOS.md desactualizado: {inconsistencias}",
        )


if __name__ == "__main__":
    unittest.main()
