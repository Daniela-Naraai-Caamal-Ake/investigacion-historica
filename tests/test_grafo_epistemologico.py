"""
Pruebas para tools/grafo_epistemologico.py
"""

from __future__ import annotations

import sys
import os
import unittest

# Añadir tools/ al path para importar el módulo directamente
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools"))

from grafo_epistemologico import (
    GrafoEpistemologico,
    PREFIJO_HIPOTESIS,
    PREFIJO_NODO,
    PREFIJO_REGISTRO,
    PREFIJO_FUENTE,
    PREFIJO_PREGUNTA,
    construir_grafo,
    generar_reporte,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _grafo_minimo() -> GrafoEpistemologico:
    """Grafo mínimo con hipótesis, un nodo, dos registros y dos fuentes."""
    g = GrafoEpistemologico()
    g.agregar_nodo(PREFIJO_HIPOTESIS, PREFIJO_HIPOTESIS, "Hipótesis")
    g.agregar_nodo("NODO:001", PREFIJO_NODO, "Nodo 001", {"nodo_id": "001"})
    g.agregar_nodo("REGISTRO:001-A", PREFIJO_REGISTRO, "Registro A",
                   {"registro_id": "001-A", "tags": ["tierra", "poder"]})
    g.agregar_nodo("REGISTRO:001-B", PREFIJO_REGISTRO, "Registro B sin hipótesis",
                   {"registro_id": "001-B", "tags": []})
    g.agregar_nodo("FUENTE:001-A:fuente", PREFIJO_FUENTE, "Fuente A")
    # Aristas
    g.agregar_arista("REGISTRO:001-A", "NODO:001", "pertenece_a")
    g.agregar_arista("REGISTRO:001-B", "NODO:001", "pertenece_a")
    g.agregar_arista("REGISTRO:001-A", PREFIJO_HIPOTESIS, "conecta_hipotesis")
    g.agregar_arista("REGISTRO:001-A", "FUENTE:001-A:fuente", "cita")
    return g


# ---------------------------------------------------------------------------
# Tests de GrafoEpistemologico
# ---------------------------------------------------------------------------

class TestGrafoBasico(unittest.TestCase):

    def setUp(self):
        self.g = _grafo_minimo()

    def test_nodos_agregados(self):
        self.assertIn(PREFIJO_HIPOTESIS, self.g.nodos)
        self.assertIn("NODO:001", self.g.nodos)
        self.assertIn("REGISTRO:001-A", self.g.nodos)
        self.assertIn("REGISTRO:001-B", self.g.nodos)

    def test_grado_salida(self):
        # Registro A tiene 3 aristas salientes
        self.assertEqual(self.g.grado_salida("REGISTRO:001-A"), 3)

    def test_grado_entrada(self):
        # NODO:001 recibe 2 aristas entrantes de los registros
        self.assertEqual(self.g.grado_entrada("NODO:001"), 2)

    def test_vecinos(self):
        vecinos = self.g.vecinos("REGISTRO:001-A")
        self.assertIn("NODO:001", vecinos)
        self.assertIn(PREFIJO_HIPOTESIS, vecinos)

    def test_arista_invalida_no_falla(self):
        """Agregar arista con nodo inexistente no debe lanzar excepción."""
        self.g.agregar_arista("NO_EXISTE", "NODO:001", "pertenece_a")
        # No debe haber aumentado el número de aristas
        aristas_antes = len(self.g.aristas)
        self.g.agregar_arista("NO_EXISTE_2", "TAMPOCO", "cita")
        self.assertEqual(len(self.g.aristas), aristas_antes)

    def test_nodo_no_duplicado_al_agregar_dos_veces(self):
        """Agregar el mismo nodo dos veces sobreescribe sin duplicar."""
        nodos_antes = len(self.g.nodos)
        self.g.agregar_nodo("NODO:001", PREFIJO_NODO, "Nuevo título")
        self.assertEqual(len(self.g.nodos), nodos_antes)


class TestConectividad(unittest.TestCase):

    def test_componentes_conexos_grafo_completo(self):
        """Un grafo donde todo está unido debe tener 1 componente."""
        g = _grafo_minimo()
        # Conectar registro B a la hipótesis y agregar fuente
        g.agregar_nodo("FUENTE:001-B:fuente", PREFIJO_FUENTE, "Fuente B")
        g.agregar_arista("REGISTRO:001-B", PREFIJO_HIPOTESIS, "conecta_hipotesis")
        g.agregar_arista("REGISTRO:001-B", "FUENTE:001-B:fuente", "cita")
        comps = g.componentes_conectados_no_dirigidos()
        self.assertEqual(len(comps), 1)

    def test_nodo_aislado_detectado(self):
        g = GrafoEpistemologico()
        g.agregar_nodo("A", PREFIJO_NODO, "Nodo A")
        g.agregar_nodo("B", PREFIJO_NODO, "Nodo B")
        g.agregar_nodo("C", PREFIJO_NODO, "Nodo C aislado")
        g.agregar_arista("A", "B", "continua_desde")
        aislados = g.nodos_aislados()
        self.assertIn("C", aislados)
        self.assertNotIn("A", aislados)
        self.assertNotIn("B", aislados)

    def test_alcanzables_desde(self):
        g = GrafoEpistemologico()
        for n in ["A", "B", "C", "D"]:
            g.agregar_nodo(n, PREFIJO_NODO, n)
        g.agregar_arista("A", "B", "continua_desde")
        g.agregar_arista("B", "C", "continua_desde")
        alcanzables = g.alcanzables_desde("A")
        self.assertIn("B", alcanzables)
        self.assertIn("C", alcanzables)
        self.assertNotIn("D", alcanzables)
        self.assertNotIn("A", alcanzables)

    def test_grafo_vacio_tiene_cero_componentes(self):
        g = GrafoEpistemologico()
        comps = g.componentes_conectados_no_dirigidos()
        self.assertEqual(len(comps), 0)


class TestAnalisisRobustez(unittest.TestCase):

    def setUp(self):
        self.g = _grafo_minimo()

    def test_registros_sin_hipotesis(self):
        analisis = self.g.analizar_robustez()
        sin_hip = analisis["registros_sin_hipotesis"]
        self.assertIn("REGISTRO:001-B", sin_hip)
        self.assertNotIn("REGISTRO:001-A", sin_hip)

    def test_registros_sin_fuente(self):
        analisis = self.g.analizar_robustez()
        sin_fuente = analisis["registros_sin_fuente"]
        self.assertIn("REGISTRO:001-B", sin_fuente)
        self.assertNotIn("REGISTRO:001-A", sin_fuente)

    def test_registros_sin_tags(self):
        analisis = self.g.analizar_robustez()
        sin_tags = analisis["registros_sin_tags"]
        self.assertIn("REGISTRO:001-B", sin_tags)
        self.assertNotIn("REGISTRO:001-A", sin_tags)

    def test_cobertura_hipotesis(self):
        analisis = self.g.analizar_robustez()
        # 1 de 2 registros tiene hipótesis → 50%
        self.assertEqual(analisis["metricas"]["cobertura_hipotesis_pct"], 50.0)

    def test_metricas_basicas(self):
        analisis = self.g.analizar_robustez()
        m = analisis["metricas"]
        self.assertEqual(m["total_registros"], 2)
        self.assertEqual(m["total_nodos_historicos"], 1)
        self.assertEqual(m["total_fuentes"], 1)

    def test_sin_registros(self):
        """Con cero registros, las coberturas deben ser 0 sin lanzar ZeroDivisionError."""
        g = GrafoEpistemologico()
        g.agregar_nodo(PREFIJO_HIPOTESIS, PREFIJO_HIPOTESIS, "Hipótesis")
        analisis = g.analizar_robustez()
        self.assertEqual(analisis["metricas"]["cobertura_hipotesis_pct"], 0)
        self.assertEqual(analisis["metricas"]["cobertura_fuente_pct"], 0)

    def test_preguntas_pendientes_detectadas(self):
        g = GrafoEpistemologico()
        g.agregar_nodo(PREFIJO_HIPOTESIS, PREFIJO_HIPOTESIS, "H")
        g.agregar_nodo("NODO:001", PREFIJO_NODO, "Nodo 001", {"nodo_id": "001"})
        g.agregar_nodo("PREGUNTA:P001-01", PREFIJO_PREGUNTA, "¿Pregunta abierta?",
                       {"pregunta_id": "P001-01", "estado": "PENDIENTE",
                        "prioridad": "Alta", "tipo": "Histórico"})
        g.agregar_nodo("PREGUNTA:P001-02", PREFIJO_PREGUNTA, "¿Respondida?",
                       {"pregunta_id": "P001-02", "estado": "RESPONDIDA",
                        "prioridad": "Media", "tipo": "Histórico"})
        g.agregar_arista("PREGUNTA:P001-01", "NODO:001", "pertenece_a")
        g.agregar_arista("PREGUNTA:P001-02", PREFIJO_HIPOTESIS, "responde_a")
        analisis = g.analizar_robustez()
        pendientes = analisis["preguntas_pendientes"]
        self.assertIn("PREGUNTA:P001-01", pendientes)
        self.assertNotIn("PREGUNTA:P001-02", pendientes)

    def test_nodo_historico_aislado(self):
        g = GrafoEpistemologico()
        g.agregar_nodo("NODO:001", PREFIJO_NODO, "Nodo 001", {"nodo_id": "001"})
        g.agregar_nodo("NODO:002", PREFIJO_NODO, "Nodo 002", {"nodo_id": "002"})
        # 002 está conectado con 001
        g.agregar_arista("NODO:002", "NODO:001", "continua_desde")
        # 001 no está conectado con ningún otro nodo histórico (solo recibe)
        analisis = g.analizar_robustez()
        # Nodo 001 tiene arista entrante de NODO:002, por eso no debe estar aislado
        self.assertNotIn("NODO:002", analisis["nodos_historicos_aislados"])

    def test_nodo_historico_sin_conexion_alguna(self):
        g = GrafoEpistemologico()
        g.agregar_nodo("NODO:001", PREFIJO_NODO, "Nodo 001", {"nodo_id": "001"})
        g.agregar_nodo("NODO:002", PREFIJO_NODO, "Nodo 002", {"nodo_id": "002"})
        # No hay aristas entre ellos
        analisis = g.analizar_robustez()
        self.assertIn("NODO:001", analisis["nodos_historicos_aislados"])
        self.assertIn("NODO:002", analisis["nodos_historicos_aislados"])


class TestExportarJson(unittest.TestCase):

    def test_estructura_json(self):
        g = _grafo_minimo()
        resultado = g.exportar_json()
        self.assertIn("nodos", resultado)
        self.assertIn("aristas", resultado)
        self.assertIsInstance(resultado["nodos"], list)
        self.assertIsInstance(resultado["aristas"], list)

    def test_nodos_json_tienen_campos_requeridos(self):
        g = _grafo_minimo()
        resultado = g.exportar_json()
        for nodo in resultado["nodos"]:
            self.assertIn("id", nodo)
            self.assertIn("tipo", nodo)
            self.assertIn("etiqueta", nodo)
            self.assertIn("grado_entrada", nodo)
            self.assertIn("grado_salida", nodo)

    def test_aristas_json_tienen_campos_requeridos(self):
        g = _grafo_minimo()
        resultado = g.exportar_json()
        for arista in resultado["aristas"]:
            self.assertIn("origen", arista)
            self.assertIn("destino", arista)
            self.assertIn("tipo", arista)


class TestConstruirGrafo(unittest.TestCase):
    """Pruebas de integración con los archivos reales del proyecto."""

    @classmethod
    def setUpClass(cls):
        cls.g = construir_grafo()
        cls.analisis = cls.g.analizar_robustez()

    def test_hipotesis_existe(self):
        self.assertIn(PREFIJO_HIPOTESIS, self.g.nodos)

    def test_diez_nodos_historicos(self):
        nodos_hist = [
            n for n, i in self.g.nodos.items() if i["tipo"] == PREFIJO_NODO
        ]
        self.assertEqual(len(nodos_hist), 10)

    def test_registros_existen(self):
        registros = [
            n for n, i in self.g.nodos.items() if i["tipo"] == PREFIJO_REGISTRO
        ]
        self.assertGreater(len(registros), 0)

    def test_preguntas_existen(self):
        preguntas = [
            n for n, i in self.g.nodos.items() if i["tipo"] == PREFIJO_PREGUNTA
        ]
        self.assertGreater(len(preguntas), 0)

    def test_cobertura_hipotesis_completa(self):
        self.assertEqual(
            self.analisis["metricas"]["cobertura_hipotesis_pct"], 100.0
        )

    def test_cobertura_fuente_completa(self):
        self.assertEqual(
            self.analisis["metricas"]["cobertura_fuente_pct"], 100.0
        )

    def test_no_hay_nodos_historicos_aislados(self):
        self.assertEqual(len(self.analisis["nodos_historicos_aislados"]), 0)

    def test_grafo_es_conexo(self):
        """El grafo principal debe tener pocos componentes."""
        comps = self.analisis["componentes"]
        # El componente principal debe contener todos los nodos históricos
        nodos_hist = {
            n for n, i in self.g.nodos.items() if i["tipo"] == PREFIJO_NODO
        }
        comp_principal = max(comps, key=len)
        for nh in nodos_hist:
            self.assertIn(
                nh, comp_principal,
                f"Nodo histórico {nh} no está en el componente principal",
            )

    def test_hay_aristas(self):
        self.assertGreater(len(self.g.aristas), 0)

    def test_exportar_json_serializable(self):
        import json as _json
        grafo_dict = self.g.exportar_json()
        # No debe lanzar excepción
        texto = _json.dumps(grafo_dict, ensure_ascii=False)
        self.assertGreater(len(texto), 0)


class TestGenerarReporte(unittest.TestCase):

    def test_reporte_contiene_secciones(self):
        g = _grafo_minimo()
        analisis = g.analizar_robustez()
        reporte = generar_reporte(g, analisis)
        self.assertIn("Métricas del grafo", reporte)
        self.assertIn("Componentes conexos", reporte)
        self.assertIn("Brechas epistemológicas", reporte)
        self.assertIn("Preguntas pendientes", reporte)

    def test_reporte_es_string(self):
        g = _grafo_minimo()
        analisis = g.analizar_robustez()
        reporte = generar_reporte(g, analisis)
        self.assertIsInstance(reporte, str)
        self.assertGreater(len(reporte), 0)

    def test_reporte_con_grafo_real(self):
        g = construir_grafo()
        analisis = g.analizar_robustez()
        reporte = generar_reporte(g, analisis)
        self.assertIn("100.0%", reporte)


if __name__ == "__main__":
    unittest.main()
