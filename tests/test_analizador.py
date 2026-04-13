"""
Pruebas para el módulo de utilidades y el analizador de datos históricos.
"""

import json
import os
import sys
import tempfile
import unittest

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utilidades import (
    buscar_en_elementos,
    cargar_json,
    contar_por_campo,
    filtrar_por_campo,
    formatear_tabla,
    guardar_json,
    listar_archivos_json,
    obtener_campo_principal,
    ordenar_por_fecha,
    parsear_fecha,
)


# ---------------------------------------------------------------------------
# Datos de prueba reutilizables
# ---------------------------------------------------------------------------

EVENTOS_PRUEBA = [
    {
        "id": 1,
        "titulo": "Independencia de México",
        "fecha": "1810-09-16",
        "categoria": "Independencia",
        "importancia": "alta",
        "personajes": ["Miguel Hidalgo", "Ignacio Allende"],
    },
    {
        "id": 2,
        "titulo": "Revolución Francesa",
        "fecha": "1789-07-14",
        "categoria": "Revolución",
        "importancia": "alta",
        "personajes": ["Robespierre", "Luis XVI"],
    },
    {
        "id": 3,
        "titulo": "Reforma Agraria",
        "fecha": "1915-01-06",
        "categoria": "Reforma",
        "importancia": "media",
        "personajes": ["Venustiano Carranza", "Emiliano Zapata"],
    },
]

COLECCION_PRUEBA = {
    "coleccion": "Eventos de Prueba",
    "descripcion": "Colección para pruebas unitarias",
    "version": "1.0",
    "eventos": EVENTOS_PRUEBA,
}


# ---------------------------------------------------------------------------
# Pruebas de cargar_json / guardar_json
# ---------------------------------------------------------------------------

class TestCargaGuardadoJSON(unittest.TestCase):

    def setUp(self):
        self.directorio_temp = tempfile.mkdtemp()

    def test_guardar_y_cargar_json(self):
        ruta = os.path.join(self.directorio_temp, "prueba.json")
        guardar_json(COLECCION_PRUEBA, ruta)
        datos = cargar_json(ruta)
        self.assertEqual(datos["coleccion"], "Eventos de Prueba")
        self.assertEqual(len(datos["eventos"]), 3)

    def test_cargar_json_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            cargar_json(os.path.join(self.directorio_temp, "inexistente.json"))

    def test_cargar_json_invalido(self):
        ruta = os.path.join(self.directorio_temp, "invalido.json")
        with open(ruta, "w") as f:
            f.write("esto no es JSON {")
        with self.assertRaises(json.JSONDecodeError):
            cargar_json(ruta)

    def test_guardar_crea_directorio(self):
        ruta = os.path.join(self.directorio_temp, "subdir", "nuevo.json")
        guardar_json({"clave": "valor"}, ruta)
        self.assertTrue(os.path.exists(ruta))


# ---------------------------------------------------------------------------
# Pruebas de listar_archivos_json
# ---------------------------------------------------------------------------

class TestListarArchivosJSON(unittest.TestCase):

    def setUp(self):
        self.directorio_temp = tempfile.mkdtemp()

    def test_lista_solo_json(self):
        for nombre in ["a.json", "b.json", "c.txt", "d.csv"]:
            open(os.path.join(self.directorio_temp, nombre), "w").close()
        archivos = listar_archivos_json(self.directorio_temp)
        nombres = [os.path.basename(a) for a in archivos]
        self.assertIn("a.json", nombres)
        self.assertIn("b.json", nombres)
        self.assertNotIn("c.txt", nombres)
        self.assertNotIn("d.csv", nombres)

    def test_directorio_inexistente(self):
        resultado = listar_archivos_json("/ruta/que/no/existe")
        self.assertEqual(resultado, [])

    def test_directorio_vacio(self):
        resultado = listar_archivos_json(self.directorio_temp)
        self.assertEqual(resultado, [])


# ---------------------------------------------------------------------------
# Pruebas de parsear_fecha
# ---------------------------------------------------------------------------

class TestParsearFecha(unittest.TestCase):

    def test_formato_iso(self):
        fecha = parsear_fecha("1810-09-16")
        self.assertIsNotNone(fecha)
        self.assertEqual(fecha.year, 1810)
        self.assertEqual(fecha.month, 9)
        self.assertEqual(fecha.day, 16)

    def test_solo_anio(self):
        fecha = parsear_fecha("1789")
        self.assertIsNotNone(fecha)
        self.assertEqual(fecha.year, 1789)

    def test_formato_invalido(self):
        fecha = parsear_fecha("no es una fecha")
        self.assertIsNone(fecha)

    def test_formato_slash(self):
        fecha = parsear_fecha("16/09/1810")
        self.assertIsNotNone(fecha)
        self.assertEqual(fecha.year, 1810)


# ---------------------------------------------------------------------------
# Pruebas de obtener_campo_principal
# ---------------------------------------------------------------------------

class TestObtenerCampoPrincipal(unittest.TestCase):

    def test_campo_eventos(self):
        campo, elementos = obtener_campo_principal(COLECCION_PRUEBA)
        self.assertEqual(campo, "eventos")
        self.assertEqual(len(elementos), 3)

    def test_campo_personajes(self):
        datos = {"personajes": [{"nombre": "Hidalgo"}]}
        campo, elementos = obtener_campo_principal(datos)
        self.assertEqual(campo, "personajes")

    def test_sin_campo_conocido_toma_primera_lista(self):
        datos = {"metadatos": "texto", "items": [{"a": 1}, {"a": 2}]}
        campo, elementos = obtener_campo_principal(datos)
        self.assertEqual(campo, "items")
        self.assertEqual(len(elementos), 2)

    def test_sin_listas(self):
        datos = {"nombre": "prueba", "version": "1.0"}
        campo, elementos = obtener_campo_principal(datos)
        self.assertIsNone(campo)
        self.assertEqual(elementos, [])


# ---------------------------------------------------------------------------
# Pruebas de contar_por_campo
# ---------------------------------------------------------------------------

class TestContarPorCampo(unittest.TestCase):

    def test_campo_simple(self):
        conteo = contar_por_campo(EVENTOS_PRUEBA, "importancia")
        self.assertEqual(conteo["alta"], 2)
        self.assertEqual(conteo["media"], 1)

    def test_campo_lista(self):
        conteo = contar_por_campo(EVENTOS_PRUEBA, "personajes")
        self.assertIn("Emiliano Zapata", conteo)
        self.assertEqual(conteo["Miguel Hidalgo"], 1)

    def test_campo_inexistente(self):
        conteo = contar_por_campo(EVENTOS_PRUEBA, "campo_inexistente")
        self.assertEqual(conteo, {})

    def test_orden_descendente(self):
        conteo = contar_por_campo(EVENTOS_PRUEBA, "importancia")
        valores = list(conteo.values())
        self.assertTrue(all(valores[i] >= valores[i + 1] for i in range(len(valores) - 1)))


# ---------------------------------------------------------------------------
# Pruebas de buscar_en_elementos
# ---------------------------------------------------------------------------

class TestBuscarEnElementos(unittest.TestCase):

    def test_buscar_termino_existente(self):
        resultados = buscar_en_elementos(EVENTOS_PRUEBA, "México")
        self.assertGreater(len(resultados), 0)

    def test_busca_insensible_mayusculas(self):
        resultados_min = buscar_en_elementos(EVENTOS_PRUEBA, "méxico")
        resultados_may = buscar_en_elementos(EVENTOS_PRUEBA, "MÉXICO")
        self.assertEqual(len(resultados_min), len(resultados_may))

    def test_buscar_en_lista(self):
        resultados = buscar_en_elementos(EVENTOS_PRUEBA, "Zapata")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["titulo"], "Reforma Agraria")

    def test_termino_inexistente(self):
        resultados = buscar_en_elementos(EVENTOS_PRUEBA, "TerminoQueNoExiste12345")
        self.assertEqual(resultados, [])


# ---------------------------------------------------------------------------
# Pruebas de filtrar_por_campo
# ---------------------------------------------------------------------------

class TestFiltrarPorCampo(unittest.TestCase):

    def test_filtrar_campo_simple(self):
        resultados = filtrar_por_campo(EVENTOS_PRUEBA, "importancia", "alta")
        self.assertEqual(len(resultados), 2)

    def test_filtrar_insensible_mayusculas(self):
        resultados = filtrar_por_campo(EVENTOS_PRUEBA, "importancia", "ALTA")
        self.assertEqual(len(resultados), 2)

    def test_filtrar_sin_resultados(self):
        resultados = filtrar_por_campo(EVENTOS_PRUEBA, "importancia", "baja")
        self.assertEqual(resultados, [])

    def test_filtrar_campo_inexistente(self):
        resultados = filtrar_por_campo(EVENTOS_PRUEBA, "campo_que_no_existe", "valor")
        self.assertEqual(resultados, [])


# ---------------------------------------------------------------------------
# Pruebas de ordenar_por_fecha
# ---------------------------------------------------------------------------

class TestOrdenarPorFecha(unittest.TestCase):

    def test_orden_cronologico(self):
        ordenados = ordenar_por_fecha(EVENTOS_PRUEBA, "fecha")
        anios = [int(e["fecha"][:4]) for e in ordenados]
        self.assertEqual(anios, sorted(anios))

    def test_elemento_sin_fecha_va_al_final(self):
        elementos = EVENTOS_PRUEBA + [{"titulo": "Sin fecha", "categoria": "Test"}]
        ordenados = ordenar_por_fecha(elementos, "fecha")
        self.assertEqual(ordenados[-1]["titulo"], "Sin fecha")


# ---------------------------------------------------------------------------
# Pruebas de formatear_tabla
# ---------------------------------------------------------------------------

class TestFormatearTabla(unittest.TestCase):

    def test_tabla_no_vacia(self):
        tabla = formatear_tabla(EVENTOS_PRUEBA, campos=["titulo", "categoria"])
        self.assertIn("titulo", tabla)
        self.assertIn("Independencia", tabla)

    def test_tabla_vacia(self):
        tabla = formatear_tabla([])
        self.assertIn("sin resultados", tabla)

    def test_truncar_texto_largo(self):
        elementos = [{"titulo": "A" * 100, "categoria": "Prueba"}]
        tabla = formatear_tabla(elementos, campos=["titulo", "categoria"], ancho_col=20)
        self.assertIn("...", tabla)

    def test_campos_automaticos(self):
        tabla = formatear_tabla(EVENTOS_PRUEBA)
        self.assertIn("titulo", tabla)
        self.assertIn("categoria", tabla)


# ---------------------------------------------------------------------------
# Pruebas de integración — análisis de archivos reales
# ---------------------------------------------------------------------------

class TestIntegracionArchivosReales(unittest.TestCase):

    def setUp(self):
        self.directorio_datos = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "datos"
        )

    def test_archivos_datos_existen(self):
        self.assertTrue(
            os.path.isdir(self.directorio_datos),
            "El directorio 'datos/' debe existir",
        )
        archivos = listar_archivos_json(self.directorio_datos)
        self.assertGreater(len(archivos), 0, "Debe haber al menos un archivo JSON en datos/")

    def test_archivos_son_json_validos(self):
        archivos = listar_archivos_json(self.directorio_datos)
        for ruta in archivos:
            with self.subTest(archivo=os.path.basename(ruta)):
                datos = cargar_json(ruta)
                self.assertIsInstance(datos, dict)

    def test_archivos_tienen_campo_principal(self):
        """Verifica que los archivos con datos tabulares retornen elementos válidos.

        Los archivos de estado/seguimiento (sin listas de dicts) pueden retornar
        (None, []) válidamente; sólo se valida que cuando hay campo principal,
        también haya al menos un elemento.
        """
        archivos = listar_archivos_json(self.directorio_datos)
        for ruta in archivos:
            with self.subTest(archivo=os.path.basename(ruta)):
                datos = cargar_json(ruta)
                campo, elementos = obtener_campo_principal(datos)
                if campo is not None:
                    self.assertGreater(
                        len(elementos), 0,
                        f"'{ruta}' tiene campo '{campo}' pero no contiene elementos",
                    )

    def test_archivos_canonicos_tienen_campo_principal(self):
        """Los archivos de datos canónicos siempre deben tener campo principal."""
        archivos_canonicos = [
            "eventos_historicos.json",
            "personajes_historicos.json",
            "fuentes_bibliograficas.json",
        ]
        for nombre in archivos_canonicos:
            ruta = os.path.join(self.directorio_datos, nombre)
            if not os.path.exists(ruta):
                continue
            with self.subTest(archivo=nombre):
                datos = cargar_json(ruta)
                campo, elementos = obtener_campo_principal(datos)
                self.assertIsNotNone(campo, f"'{nombre}' debe tener un campo de colección")
                self.assertGreater(len(elementos), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
