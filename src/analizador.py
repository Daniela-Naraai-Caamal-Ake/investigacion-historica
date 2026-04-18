#!/usr/bin/env python3
"""
Analizador de Datos Históricos en formato JSON, Markdown y PDF
===============================================================
Herramienta para cargar, explorar y analizar colecciones de datos históricos
almacenados en archivos JSON, Markdown y PDF.

Uso:
    python analizador.py                        # Analiza todos los archivos en datos/
    python analizador.py archivo.json           # Analiza un archivo específico
    python analizador.py --buscar "término"     # Busca un término en todos los datos
    python analizador.py --reporte              # Genera un reporte completo en reportes/
    python analizador.py --vacios               # Lista preguntas PENDIENTE por prioridad
    python analizador.py --cruzar "término"     # Cruza un término en todos los nodos con conexion_hipotesis
    python analizador.py --completitud          # Muestra % preguntas respondidas por nodo
    python analizador.py --fuentes-sin-usar     # Lista fuentes del catálogo no citadas en trabajo/
    python analizador.py --exportar-md out.md   # Exporta el análisis a un archivo Markdown
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

from utilidades import (
    agrupar_citas_por_categoria,
    buscar_en_elementos,
    cargar_json,
    cargar_markdown,
    contar_por_campo,
    detectar_duplicados,
    exportar_csv,
    extraer_citas_textos_contextos,
    extraer_texto_pdf,
    filtrar_por_campo,
    formatear_tabla,
    guardar_json,
    listar_archivos_json,
    listar_archivos_md,
    listar_archivos_pdf,
    normalizar_id_fuente,
    obtener_campo_principal,
    ordenar_por_fecha,
)

DIRECTORIO_DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")
DIRECTORIO_REPORTES = os.path.join(os.path.dirname(__file__), "..", "reportes")
DIRECTORIO_HOPELCHEN = os.path.join(DIRECTORIO_DATOS, "hopelchen")


# ---------------------------------------------------------------------------
# Análisis de un archivo individual
# ---------------------------------------------------------------------------

def analizar_archivo(ruta_archivo):
    """
    Carga y analiza el contenido de un archivo JSON histórico.

    Args:
        ruta_archivo (str): Ruta al archivo JSON.

    Returns:
        dict: Resumen del análisis con estadísticas y muestra de datos.
    """
    datos = cargar_json(ruta_archivo)
    nombre_archivo = os.path.basename(ruta_archivo)

    nombre_coleccion = datos.get("coleccion", nombre_archivo)
    descripcion = datos.get("descripcion", "Sin descripción")
    version = datos.get("version", "N/A")

    campo_principal, elementos = obtener_campo_principal(datos)

    resumen = {
        "archivo": nombre_archivo,
        "ruta": ruta_archivo,
        "coleccion": nombre_coleccion,
        "descripcion": descripcion,
        "version": version,
        "campo_principal": campo_principal,
        "total_registros": len(elementos),
        "campos_disponibles": list(elementos[0].keys()) if elementos else [],
        "estadisticas": {},
        "elementos": elementos,
    }

    if elementos:
        resumen["estadisticas"] = _calcular_estadisticas(elementos)

    return resumen


def analizar_markdown(ruta_archivo):
    """
    Carga y analiza el contenido de un archivo Markdown histórico.

    Args:
        ruta_archivo (str): Ruta al archivo Markdown.

    Returns:
        dict: Resumen del análisis con secciones y texto completo.
    """
    datos = cargar_markdown(ruta_archivo)
    nombre_archivo = os.path.basename(ruta_archivo)

    return {
        "archivo": nombre_archivo,
        "ruta": ruta_archivo,
        "tipo": "markdown",
        "coleccion": datos["titulo"],
        "descripcion": (
            f"Documento Markdown con {datos['total_secciones']} secciones "
            f"y {datos['total_palabras']} palabras"
        ),
        "version": "N/A",
        "campo_principal": "secciones",
        "total_registros": datos["total_secciones"],
        "campos_disponibles": ["nivel", "titulo", "contenido"],
        "estadisticas": {"total_palabras": datos["total_palabras"]},
        "elementos": datos["secciones"],
        "contenido_completo": datos["contenido_completo"],
    }


def analizar_pdf(ruta_archivo):
    """
    Carga y analiza el contenido de un archivo PDF histórico.

    Args:
        ruta_archivo (str): Ruta al archivo PDF.

    Returns:
        dict: Resumen del análisis con páginas y metadatos.
    """
    datos = extraer_texto_pdf(ruta_archivo)
    nombre_archivo = os.path.basename(ruta_archivo)
    titulo = datos["metadatos"].get("Title") or os.path.splitext(nombre_archivo)[0]

    return {
        "archivo": nombre_archivo,
        "ruta": ruta_archivo,
        "tipo": "pdf",
        "coleccion": titulo,
        "descripcion": f"Documento PDF con {datos['total_paginas']} páginas",
        "version": "N/A",
        "campo_principal": "páginas",
        "total_registros": datos["total_paginas"],
        "campos_disponibles": ["numero", "texto"],
        "estadisticas": {},
        "elementos": datos["paginas"],
        "contenido_completo": datos["contenido_completo"],
    }


def analizar_por_tipo(ruta_archivo):
    """
    Selecciona y ejecuta el analizador adecuado según la extensión del archivo.

    Args:
        ruta_archivo (str): Ruta al archivo a analizar.

    Returns:
        dict: Resumen del análisis.

    Raises:
        ValueError: Si la extensión del archivo no está soportada.
    """
    ext = os.path.splitext(ruta_archivo)[1].lower()
    if ext == ".json":
        return analizar_archivo(ruta_archivo)
    if ext == ".md":
        return analizar_markdown(ruta_archivo)
    if ext == ".pdf":
        return analizar_pdf(ruta_archivo)
    raise ValueError(f"Formato de archivo no soportado: '{ext}'")


def _calcular_estadisticas(elementos):
    """Calcula estadísticas básicas sobre una lista de elementos."""
    estadisticas = {}

    if not elementos:
        return estadisticas

    campos = list(elementos[0].keys())

    # Detectar campos de texto simples con variedad limitada (posibles categorías)
    campos_categoricos = ["categoria", "tipo", "importancia", "periodo", "idioma", "disponibilidad"]
    for campo in campos_categoricos:
        if campo in campos:
            estadisticas[f"distribucion_{campo}"] = contar_por_campo(elementos, campo)

    # Detectar campos de listas (ej: personajes, logros, temas)
    campos_lista = ["personajes", "logros", "temas", "ocupacion", "fuentes"]
    for campo in campos_lista:
        if campo in campos:
            conteo = contar_por_campo(elementos, campo)
            if conteo:
                estadisticas[f"frecuencia_{campo}"] = conteo

    # Detectar campos de fecha
    campos_fecha = [c for c in campos if "fecha" in c.lower()]
    if campos_fecha:
        estadisticas["campos_fecha"] = campos_fecha

    return estadisticas


# ---------------------------------------------------------------------------
# Impresión formateada de resultados
# ---------------------------------------------------------------------------

def imprimir_separador(caracter="=", longitud=70):
    print(caracter * longitud)


def imprimir_resumen_archivo(resumen):
    """Imprime en consola el resumen de análisis de un archivo."""
    imprimir_separador()
    print(f"📂 Archivo      : {resumen['archivo']}")
    tipo = resumen.get("tipo", "json")
    if tipo != "json":
        print(f"📄 Tipo         : {tipo.upper()}")
    print(f"📚 Colección    : {resumen['coleccion']}")
    print(f"📝 Descripción  : {resumen['descripcion']}")
    print(f"🔖 Versión      : {resumen['version']}")
    print(f"📋 Campo princ. : {resumen['campo_principal']}")
    print(f"📊 Total registros: {resumen['total_registros']}")

    if resumen["campos_disponibles"]:
        print(f"🔑 Campos       : {', '.join(resumen['campos_disponibles'])}")

    # Estadísticas
    if resumen["estadisticas"]:
        print()
        print("📈 Estadísticas:")
        for nombre_stat, valores in resumen["estadisticas"].items():
            if isinstance(valores, dict):
                print(f"   {nombre_stat}:")
                for val, count in list(valores.items())[:5]:
                    print(f"      - {val}: {count}")
                if len(valores) > 5:
                    print(f"      ... y {len(valores) - 5} más")
            elif isinstance(valores, list):
                print(f"   {nombre_stat}: {', '.join(valores)}")
            else:
                print(f"   {nombre_stat}: {valores}")

    # Muestra de datos
    if resumen["elementos"]:
        print()
        print("🔍 Muestra de datos (primeros 3 registros):")
        imprimir_separador("-")

        campos_muestra = _seleccionar_campos_muestra(resumen["campos_disponibles"])
        print(formatear_tabla(resumen["elementos"][:3], campos=campos_muestra))

    imprimir_separador()


def _seleccionar_campos_muestra(campos_disponibles):
    """Selecciona los campos más relevantes para mostrar en la muestra."""
    preferidos = ["titulo", "nombre", "fecha", "fecha_nacimiento", "categoria",
                  "tipo", "periodo", "importancia", "lugar", "numero", "texto"]
    seleccionados = [c for c in preferidos if c in campos_disponibles]
    # Completar con otros campos hasta llegar a 4
    for c in campos_disponibles:
        if c not in seleccionados and len(seleccionados) < 4:
            seleccionados.append(c)
    return seleccionados or campos_disponibles[:4]


# ---------------------------------------------------------------------------
# Generación de reportes
# ---------------------------------------------------------------------------

def generar_reporte(resumenes):
    """
    Genera un reporte en texto y JSON a partir de los resúmenes de análisis.

    Args:
        resumenes (list[dict]): Lista de resúmenes generados por analizar_archivo.

    Returns:
        str: Ruta al archivo de reporte de texto generado.
    """
    os.makedirs(DIRECTORIO_REPORTES, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Reporte JSON con todos los metadatos
    datos_reporte = {
        "fecha_generacion": datetime.now().isoformat(),
        "total_archivos_analizados": len(resumenes),
        "archivos": [
            {
                k: v for k, v in r.items() if k != "elementos"
            }
            for r in resumenes
        ],
    }
    ruta_json = os.path.join(DIRECTORIO_REPORTES, f"reporte_{timestamp}.json")
    guardar_json(datos_reporte, ruta_json)

    # Reporte de texto legible
    ruta_txt = os.path.join(DIRECTORIO_REPORTES, f"reporte_{timestamp}.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("   REPORTE DE INVESTIGACIÓN HISTÓRICA\n")
        f.write(f"   Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        total_registros = sum(r["total_registros"] for r in resumenes)
        f.write(f"Total de archivos analizados: {len(resumenes)}\n")
        f.write(f"Total de registros encontrados: {total_registros}\n\n")

        for resumen in resumenes:
            f.write("-" * 70 + "\n")
            f.write(f"Colección: {resumen['coleccion']}\n")
            f.write(f"Archivo  : {resumen['archivo']}\n")
            f.write(f"Registros: {resumen['total_registros']}\n")
            f.write(f"Campos   : {', '.join(resumen['campos_disponibles'])}\n")

            if resumen["estadisticas"]:
                f.write("Estadísticas:\n")
                for nombre_stat, valores in resumen["estadisticas"].items():
                    if isinstance(valores, dict):
                        f.write(f"  {nombre_stat}:\n")
                        for val, count in list(valores.items())[:10]:
                            f.write(f"    - {val}: {count}\n")
                    elif isinstance(valores, list):
                        f.write(f"  {nombre_stat}: {', '.join(valores)}\n")
                    else:
                        f.write(f"  {nombre_stat}: {valores}\n")
            f.write("\n")

        f.write("=" * 70 + "\n")
        f.write("FIN DEL REPORTE\n")

    print(f"\n✅ Reporte de texto generado: {ruta_txt}")
    print(f"✅ Reporte JSON  generado  : {ruta_json}")
    return ruta_txt


# ---------------------------------------------------------------------------
# Extracción y presentación de citas, textos y contextos
# ---------------------------------------------------------------------------

_ICONOS_TIPO = {"cita": "💬", "texto": "📄", "contexto": "🔎"}

_CABECERAS_TIPO = {
    "cita": "CITAS DIRECTAS",
    "texto": "TEXTOS COMPLETOS",
    "contexto": "CONTEXTOS",
}


def mostrar_citas_por_categoria(agrupado):
    """
    Imprime en consola las citas, textos y contextos agrupados por categoría.

    Args:
        agrupado (dict): Resultado de :func:`agrupar_citas_por_categoria`.
    """
    if not agrupado:
        print("  (No se encontraron citas, textos ni contextos con la longitud mínima.)")
        return

    total = sum(len(v) for v in agrupado.values())
    print(f"\n{'=' * 70}")
    print("   CITAS LARGAS, TEXTOS Y CONTEXTOS  —  ESTRUCTURADO POR CATEGORÍA")
    print(f"   Total de entradas extraídas: {total}")
    print(f"{'=' * 70}")

    for categoria, entradas in agrupado.items():
        print(f"\n{'─' * 70}")
        print(f"📂  {categoria}  ({len(entradas)} entrada(s))")
        print(f"{'─' * 70}")

        # Agrupar por tipo dentro de la categoría
        por_tipo = {}
        for e in entradas:
            por_tipo.setdefault(e["tipo"], []).append(e)

        for tipo in ("cita", "texto", "contexto"):
            if tipo not in por_tipo:
                continue
            icono = _ICONOS_TIPO[tipo]
            cabecera = _CABECERAS_TIPO[tipo]
            print(f"\n  {icono}  {cabecera}:")
            for entrada in por_tipo[tipo]:
                print(f"\n    [{entrada['subtipo']}]")
                # Mostrar texto con sangría
                for linea in entrada["texto"].splitlines():
                    print(f"      {linea}")
                if entrada["fuente"]:
                    print(f"\n      ↳ Fuente: {entrada['fuente']}")

    print(f"\n{'=' * 70}")


def guardar_citas_reporte(agrupado, ruta_base):
    """
    Guarda las citas agrupadas por categoría en archivos JSON y Markdown.

    Args:
        agrupado (dict): Resultado de :func:`agrupar_citas_por_categoria`.
        ruta_base (str): Ruta base (sin extensión) para los archivos de salida.

    Returns:
        tuple[str, str]: Rutas al archivo Markdown y al JSON generados.
    """
    ruta_json = ruta_base + "_citas.json"
    guardar_json(agrupado, ruta_json)

    ruta_md = ruta_base + "_citas.md"
    with open(ruta_md, "w", encoding="utf-8") as f:
        total = sum(len(v) for v in agrupado.values())
        f.write("# Citas Largas, Textos y Contextos por Categoría\n\n")
        f.write(f"Total de entradas: {total}\n\n")

        for categoria, entradas in agrupado.items():
            f.write(f"## {categoria}\n\n")

            por_tipo = {}
            for e in entradas:
                por_tipo.setdefault(e["tipo"], []).append(e)

            for tipo in ("cita", "texto", "contexto"):
                if tipo not in por_tipo:
                    continue
                f.write(f"### {_CABECERAS_TIPO[tipo]}\n\n")
                for entrada in por_tipo[tipo]:
                    f.write(f"**[{entrada['subtipo']}]**\n\n")
                    texto_md = entrada['texto'].replace('\n', '\n> ')
                    f.write(f"> {texto_md}\n\n")
                    if entrada["fuente"]:
                        f.write(f"*Fuente: {entrada['fuente']}*\n\n")

    return ruta_md, ruta_json


# ---------------------------------------------------------------------------
# Búsqueda global
# ---------------------------------------------------------------------------

def buscar_global(termino, resumenes):
    """
    Busca un término en todos los elementos de todas las colecciones.

    Args:
        termino (str): Término de búsqueda.
        resumenes (list[dict]): Lista de resúmenes ya cargados.
    """
    print(f"\n🔎 Buscando '{termino}' en todas las colecciones...\n")
    total_encontrados = 0

    for resumen in resumenes:
        resultados = buscar_en_elementos(resumen["elementos"], termino)
        if resultados:
            total_encontrados += len(resultados)
            print(f"📂 {resumen['coleccion']} — {len(resultados)} resultado(s):")
            campos_muestra = _seleccionar_campos_muestra(resumen["campos_disponibles"])
            print(formatear_tabla(resultados, campos=campos_muestra))
            print()

    if total_encontrados == 0:
        print(f"  No se encontraron resultados para '{termino}'.")
    else:
        print(f"✔ Total encontrado: {total_encontrados} registro(s).")


# ---------------------------------------------------------------------------
# Vacíos: preguntas PENDIENTE ordenadas por prioridad
# ---------------------------------------------------------------------------

_PRIORIDAD_NIVEL = {
    "urgente": 0,
    "urgente — alta": 0,
    "urgente - alta": 0,
    "alta": 1,
    "alta — central para la hipótesis": 1,
    "alta — situación activa": 1,
    "media-alta": 2,
    "media": 3,
    "media-baja": 4,
    "baja": 5,
}

_ICONO_ESTADO = {
    "pendiente": "🔴",
    "en proceso": "🟡",
    "respondida parcialmente": "🟠",
    "respondida": "🟢",
}


def _icono_estado(estado: str) -> str:
    estado_lower = estado.lower()
    for clave, icono in _ICONO_ESTADO.items():
        if estado_lower.startswith(clave):
            return icono
    return "⚪"


def _nivel_prioridad(prioridad: str) -> int:
    return _PRIORIDAD_NIVEL.get(prioridad.lower().strip(), 9)


def _extraer_preguntas_de_archivo(ruta: str) -> list[dict]:
    """Lee un HOPELCHEN_PREGUNTAS_*.json y devuelve la lista de preguntas."""
    try:
        datos = cargar_json(ruta)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    preguntas = []
    for clave in ("preguntas", "preguntas_urgentes", "preguntas_alta_prioridad"):
        val = datos.get(clave)
        if isinstance(val, list):
            preguntas.extend(v for v in val if isinstance(v, dict))
    nodo_origen = datos.get("nodo_origen", os.path.basename(ruta))
    for p in preguntas:
        p.setdefault("_nodo_origen", nodo_origen)
        p.setdefault("_archivo", os.path.basename(ruta))
    return preguntas


def mostrar_vacios() -> None:
    """
    Lista todas las preguntas cuyo estado comienza con PENDIENTE,
    ordenadas de mayor a menor prioridad.
    """
    import glob as _glob
    patron = os.path.join(DIRECTORIO_HOPELCHEN, "HOPELCHEN_PREGUNTAS_*.json")
    archivos = sorted(_glob.glob(patron))

    todas: list[dict] = []
    for archivo in archivos:
        todas.extend(_extraer_preguntas_de_archivo(archivo))

    # Filtrar solo PENDIENTE o EN PROCESO
    pendientes = [
        p for p in todas
        if not p.get("estado", "PENDIENTE").upper().startswith("RESPONDIDA")
    ]
    pendientes.sort(key=lambda p: _nivel_prioridad(p.get("prioridad", "media")))

    print(f"\n{'=' * 70}")
    print(f"   VACÍOS — PREGUNTAS SIN RESPONDER ({len(pendientes)} de {len(todas)})")
    print(f"{'=' * 70}")

    if not pendientes:
        print("  ✅ ¡No hay preguntas pendientes!")
        return

    nivel_actual = -1
    niveles_label = {0: "URGENTE", 1: "Alta", 2: "Media-Alta", 3: "Media", 4: "Media-Baja", 5: "Baja"}

    for p in pendientes:
        nivel = _nivel_prioridad(p.get("prioridad", "media"))
        if nivel != nivel_actual:
            nivel_actual = nivel
            label = niveles_label.get(nivel, f"Nivel {nivel}")
            print(f"\n{'─' * 70}")
            print(f"  📌 PRIORIDAD {label.upper()}")
            print(f"{'─' * 70}")

        pid = p.get("pregunta_id", "—")
        pregunta = p.get("pregunta", "—")
        estado = p.get("estado", "PENDIENTE")
        icono = _icono_estado(estado)
        nodo = p.get("_nodo_origen", "—")

        print(f"\n  [{pid}] {icono} {estado}")
        print(f"  Nodo: {nodo[:60]}")
        # Wrap pregunta
        palabras = pregunta.split()
        linea = "  ❓ "
        for palabra in palabras:
            if len(linea) + len(palabra) + 1 > 72:
                print(linea)
                linea = "     " + palabra + " "
            else:
                linea += palabra + " "
        if linea.strip():
            print(linea)

        fuentes = p.get("fuentes_a_consultar", [])
        if fuentes:
            print(f"  📚 Buscar en: {fuentes[0][:65]}")

    print(f"\n{'=' * 70}")
    print(f"  Total PENDIENTE/EN PROCESO: {len(pendientes)}")
    print(f"{'=' * 70}\n")


# ---------------------------------------------------------------------------
# Cruzar: busca término en registros de todos los nodos con conexion_hipotesis
# ---------------------------------------------------------------------------

def cruzar_termino(termino: str) -> None:
    """
    Busca ``termino`` (insensible a mayúsculas) en todos los registros de
    los archivos HOPELCHEN_NODO_*.json y muestra el registro_id, subtítulo
    y conexion_hipotesis de cada coincidencia.
    """
    import glob as _glob
    patron = os.path.join(DIRECTORIO_HOPELCHEN, "HOPELCHEN_NODO_*.json")
    archivos = sorted(_glob.glob(patron))
    termino_lower = termino.lower()

    print(f"\n{'=' * 70}")
    print(f"   CRUCE DE TÉRMINO: '{termino}'")
    print(f"{'=' * 70}")

    total_hits = 0
    nodos_con_hits: set[str] = set()

    for archivo in archivos:
        try:
            datos = cargar_json(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            continue

        nodo_id = datos.get("nodo_id", "?")
        nodo_titulo = datos.get("titulo", os.path.basename(archivo))[:55]
        registros = datos.get("registros", [])
        if not isinstance(registros, list):
            continue

        hits_nodo = []
        for reg in registros:
            if not isinstance(reg, dict):
                continue
            # Serializar registro completo a texto para buscar
            texto_reg = json.dumps(reg, ensure_ascii=False).lower()
            if termino_lower in texto_reg:
                hits_nodo.append(reg)

        if not hits_nodo:
            continue

        total_hits += len(hits_nodo)
        nodos_con_hits.add(nodo_id)

        print(f"\n{'─' * 70}")
        print(f"  📂 Nodo {nodo_id} — {nodo_titulo}")
        print(f"     {len(hits_nodo)} registro(s) con '{termino}':")

        for reg in hits_nodo:
            rid = reg.get("registro_id", "?")
            subtitulo = reg.get("subtitulo", reg.get("descripcion", "")[:60])
            conexion = reg.get("conexion_hipotesis", "")
            fecha = reg.get("fecha_evento", "—")
            lugar = reg.get("lugar", "—")[:40]

            print(f"\n    [{rid}] {subtitulo[:60]}")
            print(f"    📅 {fecha}  |  📍 {lugar}")
            if conexion:
                # Wrap conexion
                palabras = conexion.split()
                linea = "    → "
                for palabra in palabras:
                    if len(linea) + len(palabra) + 1 > 72:
                        print(linea)
                        linea = "      " + palabra + " "
                    else:
                        linea += palabra + " "
                if linea.strip():
                    print(linea)

    print(f"\n{'=' * 70}")
    if total_hits == 0:
        print(f"  Sin resultados para '{termino}' en registros de nodos.")
    else:
        print(f"  Total: {total_hits} registro(s) en {len(nodos_con_hits)} nodo(s).")
    print(f"{'=' * 70}\n")


# ---------------------------------------------------------------------------
# Completitud: % de preguntas resueltas por nodo
# ---------------------------------------------------------------------------

def mostrar_completitud() -> None:
    """
    Para cada nodo, muestra el porcentaje de preguntas respondidas vs.
    pendientes, cruzando HOPELCHEN_NODO_*.json con HOPELCHEN_PREGUNTAS_*.json.
    """
    import glob as _glob

    # Mapear nodo_id → archivo de preguntas
    patron_preguntas = os.path.join(DIRECTORIO_HOPELCHEN, "HOPELCHEN_PREGUNTAS_*.json")
    archivos_preguntas: dict[str, str] = {}
    for ruta in sorted(_glob.glob(patron_preguntas)):
        try:
            datos = cargar_json(ruta)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        nodo_ref = datos.get("nodo_referencia", datos.get("nodo_origen", ""))
        if nodo_ref:
            archivos_preguntas[str(nodo_ref)] = ruta
        # También mapear por número de archivo (ej: "001" de PREGUNTAS_001_...)
        nombre = os.path.basename(ruta)
        match_num = re.search(r'HOPELCHEN_PREGUNTAS_(\d+)', nombre)
        if match_num:
            archivos_preguntas[match_num.group(1)] = ruta

    patron_nodos = os.path.join(DIRECTORIO_HOPELCHEN, "HOPELCHEN_NODO_*.json")
    archivos_nodos = sorted(_glob.glob(patron_nodos))

    print(f"\n{'=' * 70}")
    print("   COMPLETITUD — PREGUNTAS POR NODO")
    print(f"{'=' * 70}")

    total_preguntas = 0
    total_respondidas = 0

    for ruta_nodo in archivos_nodos:
        try:
            nodo = cargar_json(ruta_nodo)
        except (FileNotFoundError, json.JSONDecodeError):
            continue

        nodo_id = nodo.get("nodo_id", "?")
        titulo = nodo.get("titulo", os.path.basename(ruta_nodo))[:55]

        # Buscar archivo de preguntas correspondiente
        ruta_preguntas = archivos_preguntas.get(nodo_id)
        if ruta_preguntas is None:
            # Intento por número de nodo en nombre del archivo
            nombre_nodo = os.path.basename(ruta_nodo)
            match_num = re.search(r'HOPELCHEN_NODO_(\d+)', nombre_nodo)
            if match_num:
                ruta_preguntas = archivos_preguntas.get(match_num.group(1))

        if ruta_preguntas is None:
            print(f"\n  📂 Nodo {nodo_id} — {titulo}")
            print("     ⚠ Sin archivo de preguntas asociado")
            continue

        preguntas = _extraer_preguntas_de_archivo(ruta_preguntas)
        n_total = len(preguntas)
        if n_total == 0:
            continue

        n_respondidas = sum(
            1 for p in preguntas
            if p.get("estado", "").upper().startswith("RESPONDIDA")
        )
        n_en_proceso = sum(
            1 for p in preguntas
            if p.get("estado", "").lower().startswith("en proceso")
        )
        n_pendientes = n_total - n_respondidas - n_en_proceso
        pct = round(n_respondidas / n_total * 100)

        total_preguntas += n_total
        total_respondidas += n_respondidas

        # Barra de progreso visual (20 chars)
        barra_llena = round(pct / 5)
        barra = "█" * barra_llena + "░" * (20 - barra_llena)

        print(f"\n  📂 Nodo {nodo_id} — {titulo}")
        print(f"     [{barra}] {pct:3d}%  "
              f"✅ {n_respondidas} resp.  🟡 {n_en_proceso} en proc.  🔴 {n_pendientes} pend.  "
              f"({n_total} total)")

    total_pct = round(total_respondidas / total_preguntas * 100) if total_preguntas else 0
    barra_llena = round(total_pct / 5)
    barra_total = "█" * barra_llena + "░" * (20 - barra_llena)

    print(f"\n{'─' * 70}")
    print(f"  TOTAL  [{barra_total}] {total_pct:3d}%  "
          f"({total_respondidas}/{total_preguntas} preguntas respondidas)")
    print(f"{'=' * 70}\n")


# ---------------------------------------------------------------------------
# Fuentes sin usar: IDs del catálogo que no aparecen en ningún nodo/trabajo
# ---------------------------------------------------------------------------

def mostrar_fuentes_sin_usar() -> None:
    """
    Detecta fuentes registradas en el catálogo (03_fuentes_bibliograficas.json)
    que no están citadas en ningún archivo de trabajo/ ni de datos/.
    """
    import glob as _glob

    # 1. Recopilar todos los F### del catálogo
    ruta_fuentes = os.path.join(
        os.path.dirname(__file__), "..", "datos", "curated",
        "03_fuentes_bibliograficas.json"
    )
    ruta_fuentes = os.path.normpath(ruta_fuentes)

    ids_catalogo: set[str] = set()
    if os.path.exists(ruta_fuentes):
        try:
            datos_fuentes = cargar_json(ruta_fuentes)
        except (FileNotFoundError, json.JSONDecodeError):
            datos_fuentes = {}

        def _colectar_ids(obj):
            if isinstance(obj, dict):
                fid = obj.get("id", "")
                if fid:
                    ids_catalogo.add(str(fid).upper())
                for v in obj.values():
                    _colectar_ids(v)
            elif isinstance(obj, list):
                for item in obj:
                    _colectar_ids(item)

        for key, val in datos_fuentes.items():
            if key == "META":
                continue
            _colectar_ids(val)
    else:
        print("  ⚠ No se encontró 03_fuentes_bibliograficas.json")

    if not ids_catalogo:
        print("  ⚠ No se encontraron IDs de fuentes en el catálogo.")
        return

    # 2. Buscar qué F### aparecen en archivos de trabajo/ y datos/
    directorio_trabajo = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "trabajo")
    )
    directorio_mapa = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "mapa")
    )

    ids_usados: dict[str, set[str]] = {}  # fid -> set de archivos donde aparece

    def _escanear_texto(texto, origen):
        for fid in normalizar_id_fuente(texto):
            ids_usados.setdefault(fid, set()).add(origen)

    for patron_dir in [directorio_trabajo, directorio_mapa, DIRECTORIO_DATOS]:
        for ext in (".md", ".json"):
            for ruta in _glob.glob(os.path.join(patron_dir, "**", f"*{ext}"),
                                    recursive=True):
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        _escanear_texto(f.read(), os.path.basename(ruta))
                except OSError:
                    pass

    # 3. Comparar
    sin_usar = sorted(ids_catalogo - set(ids_usados.keys()))
    usadas = sorted(ids_catalogo & set(ids_usados.keys()))

    print(f"\n{'=' * 70}")
    print(f"   FUENTES SIN USAR — {len(sin_usar)} de {len(ids_catalogo)} no citadas")
    print(f"{'=' * 70}")

    if sin_usar:
        print("\n  🔴 IDs registrados en el catálogo pero sin cita en trabajo/ ni datos/:\n")
        for fid in sin_usar:
            print(f"     • {fid}")
    else:
        print("\n  ✅ Todas las fuentes del catálogo están citadas al menos una vez.")

    if usadas:
        print(f"\n  ✅ {len(usadas)} fuente(s) con al menos una cita detectada.")

    print(f"\n{'=' * 70}\n")


# ---------------------------------------------------------------------------
# Exportar a Markdown
# ---------------------------------------------------------------------------

def exportar_resultados_md(resumenes, args, ruta_salida) -> str:
    """
    Exporta el análisis actual (resúmenes, búsqueda, completitud) a Markdown.

    Args:
        resumenes (list[dict]): Resúmenes de archivos ya analizados.
        args: Objeto de argumentos parseados (argparse.Namespace).
        ruta_salida (str): Ruta del archivo Markdown de salida.

    Returns:
        str: Ruta al archivo generado.
    """
    import io
    import contextlib

    lineas = [
        "# Exportación — Analizador de Investigación Histórica\n",
        f"\n> Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n",
        "---\n\n",
    ]

    # Resúmenes de archivos
    lineas.append("## Resumen de archivos\n\n")
    for r in resumenes:
        lineas.append(f"### {r['coleccion']}\n\n")
        lineas.append(f"| Campo | Valor |\n|---|---|\n")
        lineas.append(f"| **Archivo** | `{r['archivo']}` |\n")
        lineas.append(f"| **Total registros** | {r['total_registros']} |\n")
        campos_str = ", ".join(r["campos_disponibles"][:8])
        if len(r["campos_disponibles"]) > 8:
            campos_str += f"… (+{len(r['campos_disponibles']) - 8})"
        lineas.append(f"| **Campos** | {campos_str} |\n\n")

    # Resultados de búsqueda, si aplica
    if args.buscar:
        lineas.append(f"## Resultados de búsqueda: «{args.buscar}»\n\n")
        for r in resumenes:
            resultados = buscar_en_elementos(r["elementos"], args.buscar)
            if resultados:
                lineas.append(f"### {r['coleccion']} — {len(resultados)} resultado(s)\n\n")
                for elem in resultados:
                    lineas.append("```json\n")
                    lineas.append(json.dumps(elem, ensure_ascii=False, indent=2))
                    lineas.append("\n```\n\n")

    # Capturar salida de completitud y vacíos si se solicitó
    for bandera, funcion in [("completitud", mostrar_completitud), ("vacios", mostrar_vacios)]:
        if getattr(args, bandera, False):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                funcion()
            salida = buf.getvalue()
            titulo_seccion = "Completitud" if bandera == "completitud" else "Vacíos / Preguntas pendientes"
            lineas.append(f"## {titulo_seccion}\n\n```\n{salida}\n```\n\n")

    directorio = os.path.dirname(ruta_salida)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.writelines(lineas)

    return ruta_salida


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def construir_parser():
    parser = argparse.ArgumentParser(
        description="Analizador de datos históricos en formato JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "archivos",
        nargs="*",
        metavar="ARCHIVO",
        help="Uno o más archivos JSON a analizar (por defecto: todos en datos/)",
    )
    parser.add_argument(
        "--buscar", "-b",
        metavar="TÉRMINO",
        help="Busca un término en todos los registros cargados",
    )
    parser.add_argument(
        "--reporte", "-r",
        action="store_true",
        help="Genera un reporte completo en la carpeta reportes/",
    )
    parser.add_argument(
        "--ordenar-fecha", "-f",
        metavar="CAMPO",
        help="Nombre del campo de fecha para ordenar los registros cronológicamente",
    )
    parser.add_argument(
        "--filtrar", "-F",
        nargs=2,
        metavar=("CAMPO", "VALOR"),
        help="Filtra registros donde CAMPO == VALOR",
    )
    parser.add_argument(
        "--citas", "-c",
        action="store_true",
        help="Extrae citas largas, textos y contextos estructurados por categoría",
    )
    parser.add_argument(
        "--min-longitud",
        type=int,
        default=50,
        metavar="N",
        help="Longitud mínima en caracteres para incluir una cita o contexto (default: 50)",
    )
    parser.add_argument(
        "--vacios", "-v",
        action="store_true",
        help="Lista preguntas PENDIENTE o EN PROCESO ordenadas por prioridad",
    )
    parser.add_argument(
        "--cruzar", "-x",
        metavar="TÉRMINO",
        help="Busca un término en todos los registros de los nodos y muestra conexion_hipotesis",
    )
    parser.add_argument(
        "--completitud",
        action="store_true",
        help="Muestra el porcentaje de preguntas respondidas vs. pendientes por nodo",
    )
    parser.add_argument(
        "--fuentes-sin-usar",
        action="store_true",
        help="Lista fuentes del catálogo que no están citadas en ningún archivo de trabajo/",
    )
    parser.add_argument(
        "--exportar-md",
        metavar="RUTA",
        help="Exporta los resultados del análisis a un archivo Markdown en RUTA",
    )
    return parser


def main():
    parser = construir_parser()
    args = parser.parse_args()

    # Determinar archivos a procesar
    if args.archivos:
        rutas = args.archivos
    else:
        rutas_json = listar_archivos_json(DIRECTORIO_DATOS)
        rutas_md = listar_archivos_md(DIRECTORIO_DATOS)
        rutas_pdf = listar_archivos_pdf(DIRECTORIO_DATOS)
        rutas = sorted(rutas_json + rutas_md + rutas_pdf)
        if not rutas:
            print(f"⚠️  No se encontraron archivos en '{DIRECTORIO_DATOS}'.")
            print("   Coloca tus archivos JSON, MD o PDF en la carpeta 'datos/' o pásalos como argumento.")
            sys.exit(1)

    # Cargar y analizar todos los archivos
    resumenes = []
    print(f"\n{'=' * 70}")
    print("   ANALIZADOR DE INVESTIGACIÓN HISTÓRICA")
    print(f"{'=' * 70}")
    print(f"📁 Directorio de datos : {DIRECTORIO_DATOS}")
    print(f"📁 Directorio reportes : {DIRECTORIO_REPORTES}")
    n_json = sum(1 for r in rutas if r.lower().endswith(".json"))
    n_md = sum(1 for r in rutas if r.lower().endswith(".md"))
    n_pdf = sum(1 for r in rutas if r.lower().endswith(".pdf"))
    print(f"📄 Archivos a analizar : {len(rutas)} ({n_json} JSON, {n_md} MD, {n_pdf} PDF)")

    for ruta in rutas:
        try:
            resumen = analizar_por_tipo(ruta)
            resumenes.append(resumen)
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}")
        except json.JSONDecodeError as e:
            print(f"\n❌ Error al leer '{ruta}': JSON inválido — {e}")
        except ImportError as e:
            print(f"\n⚠️  {e}")
        except ValueError as e:
            print(f"\n⚠️  {e}")

    if not resumenes:
        print("\n❌ No se pudo analizar ningún archivo.")
        sys.exit(1)

    # Aplicar filtro si se especificó
    if args.filtrar:
        campo_filtro, valor_filtro = args.filtrar
        print(f"\n🔽 Aplicando filtro: {campo_filtro} = '{valor_filtro}'")
        for r in resumenes:
            r["elementos"] = filtrar_por_campo(r["elementos"], campo_filtro, valor_filtro)
            r["total_registros"] = len(r["elementos"])

    # Aplicar ordenamiento por fecha si se especificó
    if args.ordenar_fecha:
        print(f"\n📅 Ordenando por campo de fecha: '{args.ordenar_fecha}'")
        for r in resumenes:
            r["elementos"] = ordenar_por_fecha(r["elementos"], args.ordenar_fecha)

    # Mostrar resúmenes
    for resumen in resumenes:
        print()
        imprimir_resumen_archivo(resumen)

    # Búsqueda global
    if args.buscar:
        buscar_global(args.buscar, resumenes)

    # Extraer citas, textos y contextos
    if args.citas:
        todas_las_citas = []
        for resumen in resumenes:
            if not resumen.get("ruta", "").endswith(".json"):
                continue
            try:
                datos_brutos = cargar_json(resumen["ruta"])
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                print(f"\n⚠️  No se pudo recargar '{resumen['archivo']}' para extracción de citas: {exc}")
                continue
            if datos_brutos:
                citas = extraer_citas_textos_contextos(
                    datos_brutos,
                    categoria_default=resumen["coleccion"],
                    longitud_minima=args.min_longitud,
                )
                todas_las_citas.extend(citas)

        agrupado = agrupar_citas_por_categoria(todas_las_citas)
        mostrar_citas_por_categoria(agrupado)

        if args.reporte:
            os.makedirs(DIRECTORIO_REPORTES, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_base = os.path.join(DIRECTORIO_REPORTES, f"reporte_{timestamp}")
            ruta_md, ruta_json = guardar_citas_reporte(agrupado, ruta_base)
            print(f"\n✅ Reporte de citas Markdown: {ruta_md}")
            print(f"✅ Reporte de citas JSON    : {ruta_json}")

    # Generar reporte general
    if args.reporte and not args.citas:
        generar_reporte(resumenes)

    # Mostrar vacíos (preguntas pendientes)
    if args.vacios:
        mostrar_vacios()

    # Cruzar término en registros de nodos
    if args.cruzar:
        cruzar_termino(args.cruzar)

    # Completitud: preguntas respondidas por nodo
    if args.completitud:
        mostrar_completitud()

    # Fuentes sin usar en el catálogo
    if args.fuentes_sin_usar:
        mostrar_fuentes_sin_usar()

    # Exportar a Markdown
    if args.exportar_md:
        ruta_out = exportar_resultados_md(resumenes, args, args.exportar_md)
        print(f"\n✅ Resultados exportados a Markdown: {ruta_out}")

    if not any([args.vacios, args.cruzar, args.completitud,
                args.fuentes_sin_usar, args.exportar_md]):
        print("\n✔ Análisis completado.\n")


if __name__ == "__main__":
    main()
