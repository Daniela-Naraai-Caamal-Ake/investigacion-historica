#!/usr/bin/env python3
"""
validar_citas_firecrawl.py
==========================
Herramienta integral de validación y ampliación de investigación mediante Firecrawl.

Realiza tres operaciones complementarias:

1. **Validar citas**: Usa Firecrawl `scrape` para comprobar que las URLs del
   ``fuentes/catalogo_fuentes.md`` responden y extraer un extracto de contenido
   que confirme o cuestione la cita documentada.

2. **Buscar fuentes faltantes**: Para los registros de ``datos/hopelchen/`` que
   carecen de campo de fuente, ejecuta búsquedas Firecrawl y propone candidatas.

3. **Ampliar nodos**: Lanza búsquedas temáticas orientadas a las preguntas
   prioritarias de ``datos/VACIOS.md`` y a los nodos con más vacíos
   (especialmente Nodo 009 — Resistencia Maya y Nodo 010 — Conocimiento y Cultura).

Uso:
    python tools/validar_citas_firecrawl.py                   # Todo
    python tools/validar_citas_firecrawl.py --modo validar    # Solo validar URLs
    python tools/validar_citas_firecrawl.py --modo fuentes    # Solo buscar fuentes
    python tools/validar_citas_firecrawl.py --modo ampliar    # Solo ampliar nodos
    python tools/validar_citas_firecrawl.py --nodo 009        # Solo nodo específico
    python tools/validar_citas_firecrawl.py --limite 10       # Limitar búsquedas

Configuración de Firecrawl:
    Crea un archivo ``.env`` en la raíz del proyecto con:
        FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    o exporta la variable de entorno FIRECRAWL_API_KEY.
    Obtén una clave gratuita en https://www.firecrawl.dev

Salidas (en ``datos/investigacion/``):
    firecrawl_validacion_YYYYMMDD.json  — Resultados completos en JSON
    firecrawl_reporte_YYYYMMDD.md       — Reporte legible en Markdown

Dependencias:
    pip install firecrawl-py requests beautifulsoup4
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
DATOS_INVESTIGACION = ROOT / "datos" / "investigacion"
FUENTES_CATALOGO = ROOT / "fuentes" / "catalogo_fuentes.md"
VACIOS_MD = ROOT / "datos" / "VACIOS.md"

DATOS_INVESTIGACION.mkdir(parents=True, exist_ok=True)

HOY = datetime.now().strftime("%Y%m%d")

# ─── Dependencias opcionales ──────────────────────────────────────────────────

try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore
    _FIRECRAWL_OK = True
except ImportError:
    _FIRECRAWL_OK = False

# Clave Firecrawl: variable de entorno → archivo .env
_FIRECRAWL_API_KEY: str | None = os.environ.get("FIRECRAWL_API_KEY")
if not _FIRECRAWL_API_KEY:
    _dotenv_path = ROOT / ".env"
    if _dotenv_path.exists():
        for _line in _dotenv_path.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line.startswith("FIRECRAWL_API_KEY=") and not _line.startswith("#"):
                _FIRECRAWL_API_KEY = _line.split("=", 1)[1].strip().strip('"').strip("'")
                break

# ─── Campos de fuente reconocidos ─────────────────────────────────────────────

CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica",
    "fuente_primaria", "fuente_secundaria", "fuentes",
]

# ─── Búsquedas de ampliación por nodo ─────────────────────────────────────────

# Nodo 009 — Resistencia y Agencia Maya
_BUSQUEDAS_NODO_009: list[dict] = [
    {
        "query": "bataboob mayas Hopelchén 1669 resistencia poder local siglo XVII",
        "registro_id": "009-A",
        "descripcion": "Bataboob de Hopelchén 1669 — documentación de resistencia post-conquista",
        "fuentes_sugeridas": ["AGN Ramo Inquisición", "Archivo Obispado de Yucatán"],
    },
    {
        "query": "Juan de Dios May ataque Hopelchén 1848 guerra castas",
        "registro_id": "009-B",
        "descripcion": "Juan de Dios May — liderazgo maya en la Guerra de Castas",
        "fuentes_sugeridas": ["Baqueiro Preve", "AGEY"],
    },
    {
        "query": "Chan Santa Cruz Estado maya independiente 1850 1901 Campeche Yucatán",
        "registro_id": "009-C",
        "descripcion": "Estado maya Chan Santa Cruz y su impacto en Los Chenes",
        "fuentes_sugeridas": ["Rodríguez Piña 1990", "INAH"],
    },
    {
        "query": "meliponicultura abeja Xunan Kab Hopelchén Los Chenes tradición maya continuidad",
        "registro_id": "009-E",
        "descripcion": "Meliponicultura como continuidad cultural maya en Hopelchén",
        "fuentes_sugeridas": ["Goldman Prize", "UNAM"],
    },
    {
        "query": "Leydy Pech Maya Ka'an organización apicultores soya transgénica amparo Campeche 2017",
        "registro_id": "009-F",
        "descripcion": "Leydy Pech y la organización Maya Ka'an — victoria jurídica contra soya transgénica",
        "fuentes_sugeridas": ["Goldman Prize", "SCJN AR 441/2015"],
    },
    {
        "query": "patrón resistencia maya Hopelchén Los Chenes 500 años autonomía territorio",
        "registro_id": "009-G",
        "descripcion": "Cruce transversal: patrón de resistencia maya en 500 años",
        "fuentes_sugeridas": ["Pool Castellanos 2025", "Taracena Arriola 2019"],
    },
]

# Nodo 010 — Conocimiento y Cultura Maya
_BUSQUEDAS_NODO_010: list[dict] = [
    {
        "query": "Santa Rosa Xtampak astronomía arquitectura alineamientos mayas Los Chenes",
        "registro_id": "010-A",
        "descripcion": "Astronomía y arquitectura maya en Los Chenes — Santa Rosa Xtampak",
        "fuentes_sugeridas": ["INAH zonas arqueológicas", "IAI Berlín Maler"],
    },
    {
        "query": "Estela 2 Santa Rosa Xtampak escritura jeroglífica Los Chenes inscripción",
        "registro_id": "010-B",
        "descripcion": "Escritura jeroglífica en Los Chenes — Estela 2",
        "fuentes_sugeridas": ["INAH", "IAI Berlín"],
    },
    {
        "query": "auto de fe Maní 1562 libros mayas destrucción Diego de Landa Yucatán",
        "registro_id": "010-C",
        "descripcion": "Auto de fe de Maní 1562 — destrucción del conocimiento maya",
        "fuentes_sugeridas": ["Landa Relación de las Cosas de Yucatán", "AGI"],
    },
    {
        "query": "lengua maya yucateca Hopelchén hablantes supervivencia lingüística siglo XXI",
        "registro_id": "010-F",
        "descripcion": "Supervivencia lingüística del maya yucateca en Hopelchén",
        "fuentes_sugeridas": ["INEGI censo lingüístico", "INALI"],
    },
    {
        "query": "control conocimiento maya Los Chenes colonización destrucción continuidad cultura",
        "registro_id": "010-G",
        "descripcion": "Cruce transversal: control del conocimiento maya en Los Chenes",
        "fuentes_sugeridas": ["Taracena Arriola 2019", "Pool Castellanos 2025"],
    },
]

# Preguntas urgentes de VACIOS.md — búsquedas dirigidas
_BUSQUEDAS_VACIOS_URGENTES: list[dict] = [
    {
        "query": "congregación Hopelchén 1621 documento colonial fundación pueblo Yucatán AGI",
        "pregunta_id": "P002-01",
        "descripcion": "Documento colonial que funda Hopelchén como pueblo de congregación en 1621",
        "nodo": "002",
    },
    {
        "query": "Pedro Advíncula Lara hacienda Holcatzin Santa Rita Hopelchén Porfiriato título propiedad",
        "pregunta_id": "P003-01",
        "descripcion": "Adquisición de haciendas por Pedro Advíncula Lara — título de propiedad",
        "nodo": "003",
    },
    {
        "query": "hacendados Hopelchén lucha antiagraria posrevolución Campeche 1920 1940",
        "pregunta_id": "P004-01",
        "descripcion": "Hacendados de Hopelchén en la lucha antiagraria post-Revolución",
        "nodo": "004",
    },
    {
        "query": "genealogía Aranda Calderón Baranda alcalde Hopelchén poder político Campeche familia",
        "pregunta_id": "P006-01",
        "descripcion": "Conexión genealógica Aranda-Baranda en el poder político de Hopelchén",
        "nodo": "006",
    },
    {
        "query": "Julio Sansores presidente municipal Hopelchén Layda Sansores San Román gobernadora Campeche parentesco",
        "pregunta_id": "P006-09",
        "descripcion": "Parentesco entre Julio Sansores (alcalde Hopelchén) y Layda Sansores (gobernadora)",
        "nodo": "006",
    },
    {
        "query": "Emilio Lara Calderón alcalde Hopelchén 2021 Pedro Advíncula Lara hacendado porfiriano genealogía",
        "pregunta_id": "P006-07",
        "descripcion": "Continuidad genealógica Lara: hacendado porfiriano → alcalde 2021",
        "nodo": "006",
    },
    {
        "query": "INEGI archivo histórico censo población Hopelchén Campeche 1900 1910 1921 1930 1940",
        "pregunta_id": "P008-01",
        "descripcion": "Datos censales históricos de Hopelchén 1900-1940",
        "nodo": "008",
    },
    {
        "query": "Pacheco Blanco 1928 Peña 1942 Los Chenes economía Campeche historia",
        "pregunta_id": "P007-01",
        "descripcion": "Obras de Pacheco Blanco y Peña sobre economía de Los Chenes",
        "nodo": "007",
    },
]

# Búsquedas adicionales para ampliar nodos existentes (001-008)
_BUSQUEDAS_AMPLIACION_GENERAL: list[dict] = [
    {
        "query": "Hopelchén arqueología prehispánica zona arqueológica Los Chenes hallazgos recientes",
        "nodo": "001",
        "descripcion": "Hallazgos arqueológicos recientes en Los Chenes / Hopelchén",
    },
    {
        "query": "encomienda Los Chenes siglo XVI Yucatán tributación maya franciscanos evangelización",
        "nodo": "002",
        "descripcion": "Encomiendas y evangelización franciscana en Los Chenes, siglo XVI",
    },
    {
        "query": "haciendas azucareras Campeche siglo XIX luneros deuda servil colonialismo",
        "nodo": "003",
        "descripcion": "Sistema de haciendas azucareras y deuda servil en Campeche, siglo XIX",
    },
    {
        "query": "menonitas Hopelchén Campeche llegada 1987 tierra deforestación biodiversidad",
        "nodo": "005",
        "descripcion": "Llegada de menonitas a Hopelchén 1987 e impacto en la tierra",
    },
    {
        "query": "presidentes municipales Hopelchén Campeche 1987 2000 historia política local",
        "nodo": "006",
        "descripcion": "Presidentes municipales de Hopelchén 1987-2000",
    },
    {
        "query": "demografía municipio Hopelchén Campeche población maya 2020 censo INEGI",
        "nodo": "008",
        "descripcion": "Datos demográficos actuales de Hopelchén — Censo INEGI 2020",
    },
]


# ─── Utilidades ───────────────────────────────────────────────────────────────

def _texto_breve(texto: str, max_chars: int = 500) -> str:
    if len(texto) > max_chars:
        return texto[:max_chars].rstrip() + "…"
    return texto


def _tiene_fuente(registro: dict) -> bool:
    return any(bool(registro.get(c)) for c in CAMPOS_FUENTE)


def _mensaje_error_firecrawl(exc: Exception) -> str:
    """Devuelve un mensaje legible para errores de la API de Firecrawl.

    firecrawl-py ≥ 4.x puede lanzar ``AttributeError`` cuando no hay red
    disponible porque su manejador de errores asume que siempre existe un
    objeto ``response``.  Esta función detecta ese caso y devuelve un
    mensaje claro en lugar del traza interna confusa.
    """
    causa = exc.__context__ or exc.__cause__
    if isinstance(causa, OSError) or isinstance(exc, AttributeError):
        return "Sin conexión a la API de Firecrawl — verifica el acceso a la red y la FIRECRAWL_API_KEY."
    return str(exc)

# ─── Extracción de URLs del catálogo ─────────────────────────────────────────

def extraer_urls_catalogo() -> list[dict]:
    """
    Extrae todas las URLs completas del archivo fuentes/catalogo_fuentes.md.
    Devuelve lista de dicts con ``fuente_id``, ``url`` y ``contexto``.
    """
    if not FUENTES_CATALOGO.exists():
        print(f"  ⚠  No se encontró {FUENTES_CATALOGO}")
        return []

    texto = FUENTES_CATALOGO.read_text(encoding="utf-8")
    # Detectar sección de fuente activa (## FX001, ## F001, etc.)
    patron_id = re.compile(r'^## (F[X]?\d+)', re.MULTILINE)
    patron_url = re.compile(r'(https?://[^\s>)\]"\'<]+)')

    resultados: list[dict] = []
    secciones = list(patron_id.finditer(texto))

    for i, match_id in enumerate(secciones):
        fuente_id = match_id.group(1)
        inicio = match_id.start()
        fin = secciones[i + 1].start() if i + 1 < len(secciones) else len(texto)
        fragmento = texto[inicio:fin]

        urls_en_seccion = patron_url.findall(fragmento)
        # Deduplicar preservando orden
        urls_vistas: set[str] = set()
        for url in urls_en_seccion:
            # Limpiar puntuación final accidental
            url = url.rstrip(".,;:)")
            if url in urls_vistas:
                continue
            urls_vistas.add(url)
            # Obtener línea de contexto
            linea_ctx = next(
                (ln.strip() for ln in fragmento.splitlines() if url in ln),
                "",
            )
            resultados.append({
                "fuente_id": fuente_id,
                "url": url,
                "contexto": _texto_breve(linea_ctx, 150),
            })

    return resultados


# ─── Extracción de registros sin fuente ───────────────────────────────────────

def extraer_registros_sin_fuente(solo_nodo: str | None = None) -> list[dict]:
    """
    Lee todos los HOPELCHEN_NODO_*.json y devuelve los registros sin campo de fuente.
    Si ``solo_nodo`` se especifica (ej. '009'), filtra por ese nodo.
    """
    registros: list[dict] = []

    patron = f"HOPELCHEN_NODO_{solo_nodo}*.json" if solo_nodo else "HOPELCHEN_NODO_*.json"
    for path in sorted(DATOS_HOPELCHEN.glob(patron)):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  ⚠  No se pudo leer {path.name}: {exc}")
            continue

        nodo_id = data.get("nodo_id", path.stem)
        for reg in data.get("registros", []):
            if not isinstance(reg, dict):
                continue
            if not _tiene_fuente(reg):
                registros.append({
                    "nodo_id": nodo_id,
                    "archivo": path.name,
                    "registro_id": reg.get("registro_id", ""),
                    "subtitulo": reg.get("subtitulo", "")[:100],
                    "fecha_evento": reg.get("fecha_evento", ""),
                    "lugar": reg.get("lugar", ""),
                })

    return registros


# ─── Modo 1: Validar URLs del catálogo ───────────────────────────────────────

def validar_urls_catalogo(app: Any, limite: int | None = None) -> list[dict]:
    """
    Para cada URL del catálogo, llama a Firecrawl `scrape` y verifica que responde.
    Devuelve lista de resultados con estado y extracto de contenido.
    """
    print("\n📋  Modo 1 — Validando URLs del catálogo de fuentes")

    urls_catalogo = extraer_urls_catalogo()
    if limite:
        urls_catalogo = urls_catalogo[:limite]

    print(f"    URLs a validar: {len(urls_catalogo)}")

    resultados: list[dict] = []

    for item in urls_catalogo:
        fuente_id = item["fuente_id"]
        url = item["url"]
        print(f"  → [{fuente_id}] {url[:70]}…")

        try:
            resp = app.scrape(
                url,
                formats=["markdown"],
                only_main_content=True,
                timeout=30000,
            )
            if hasattr(resp, "model_dump"):
                resp_dict = resp.model_dump()
            elif hasattr(resp, "__dict__"):
                resp_dict = resp.__dict__
            else:
                resp_dict = dict(resp) if isinstance(resp, dict) else {}

            markdown = resp_dict.get("markdown") or ""
            metadata = resp_dict.get("metadata") or {}
            titulo = (
                metadata.get("title", "")
                or metadata.get("og:title", "")
                if isinstance(metadata, dict) else ""
            )
            estado_http = metadata.get("statusCode", 200) if isinstance(metadata, dict) else 200
            extracto = _texto_breve(markdown, 400)

            resultado = {
                "fuente_id": fuente_id,
                "url": url,
                "contexto_catalogo": item["contexto"],
                "estado": "ok" if extracto else "sin_contenido",
                "estado_http": estado_http,
                "titulo_pagina": titulo,
                "extracto": extracto,
                "timestamp": datetime.now().isoformat(),
            }
            icono = "✓" if extracto else "○"
            print(f"     {icono} {titulo[:60] or '(sin título)'}")

        except Exception as exc:
            msg = _mensaje_error_firecrawl(exc)
            resultado = {
                "fuente_id": fuente_id,
                "url": url,
                "contexto_catalogo": item["contexto"],
                "estado": f"error: {msg}",
                "extracto": "",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"     ⚠  {msg}")

        resultados.append(resultado)
        time.sleep(1.5)  # Respetar límites de la API

    ok = sum(1 for r in resultados if r["estado"] == "ok")
    print(f"\n  ✅  Validación completada — {ok}/{len(resultados)} URLs accesibles")
    return resultados


# ─── Modo 2: Buscar fuentes para registros sin cita ──────────────────────────

def buscar_fuentes_faltantes(
    app: Any,
    solo_nodo: str | None = None,
    limite: int | None = None,
) -> list[dict]:
    """
    Para registros sin fuente, genera una query de búsqueda y lanza Firecrawl.
    """
    print("\n📋  Modo 2 — Buscando fuentes para registros sin cita")

    # Combinar búsquedas específicas con registros detectados automáticamente
    busquedas_especificas: list[dict] = []
    if solo_nodo == "009" or solo_nodo is None:
        busquedas_especificas.extend(_BUSQUEDAS_NODO_009)
    if solo_nodo == "010" or solo_nodo is None:
        busquedas_especificas.extend(_BUSQUEDAS_NODO_010)

    # Registros sin fuente detectados automáticamente
    registros_sin_fuente = extraer_registros_sin_fuente(solo_nodo)
    busquedas_auto: list[dict] = []
    for reg in registros_sin_fuente:
        # Evitar duplicar si ya hay una búsqueda específica para ese registro_id
        ids_especificos = {b.get("registro_id") for b in busquedas_especificas}
        if reg["registro_id"] in ids_especificos:
            continue
        partes = [reg["subtitulo"][:60]]
        if reg["lugar"]:
            lugar = reg["lugar"].split(",")[0].strip()
            if lugar.lower() not in reg["subtitulo"].lower():
                partes.append(lugar)
        fecha = reg.get("fecha_evento", "")
        año = fecha.split("—")[0].strip()[:4] if fecha else ""
        if año.isdigit():
            partes.append(año)
        query = " ".join(p for p in partes if p)
        if query:
            busquedas_auto.append({
                "query": query,
                "registro_id": reg["registro_id"],
                "nodo": reg["nodo_id"],
                "descripcion": f"Auto-generado: {reg['subtitulo'][:70]}",
            })

    todas_busquedas = busquedas_especificas + busquedas_auto
    if limite:
        todas_busquedas = todas_busquedas[:limite]

    print(f"    Búsquedas: {len(todas_busquedas)} "
          f"({len(busquedas_especificas)} específicas + {len(busquedas_auto)} auto)")

    resultados: list[dict] = []

    for item in todas_busquedas:
        query = item["query"]
        registro_id = item.get("registro_id", "")
        descripcion = item.get("descripcion", query[:70])
        print(f"\n  → [{registro_id}] {descripcion[:65]}")
        print(f"    Query: {query[:80]}")

        try:
            resp = app.search(query, limit=5)
            docs = getattr(resp, "web", None) or getattr(resp, "data", None)
            if docs is None:
                docs = resp if isinstance(resp, list) else []

            candidatas: list[dict] = []
            for doc in docs:
                if hasattr(doc, "model_dump"):
                    d = doc.model_dump()
                elif hasattr(doc, "__dict__"):
                    d = doc.__dict__
                else:
                    d = dict(doc) if isinstance(doc, dict) else {}
                meta = d.get("metadata") or {}
                titulo = d.get("title") or (meta.get("title", "") or meta.get("og:title", "")) if isinstance(meta, dict) else d.get("title", "")
                url = d.get("url", "")
                desc = d.get("description") or ((meta.get("description", "") or meta.get("og:description", "")) if isinstance(meta, dict) else "")
                extracto = _texto_breve(d.get("markdown") or "", 300)
                if titulo or url:
                    candidatas.append({
                        "titulo": titulo,
                        "url": url,
                        "descripcion": _texto_breve(desc, 200),
                        "extracto": extracto,
                    })

            n = len(candidatas)
            icono = "✓" if n > 0 else "○"
            print(f"     {icono} {n} candidata(s)")

            resultados.append({
                "registro_id": registro_id,
                "nodo": item.get("nodo", ""),
                "descripcion": descripcion,
                "query": query,
                "fuentes_sugeridas_manual": item.get("fuentes_sugeridas", []),
                "estado": "ok",
                "total_candidatas": n,
                "fuentes_candidatas": candidatas,
                "timestamp": datetime.now().isoformat(),
            })

        except Exception as exc:
            msg = _mensaje_error_firecrawl(exc)
            print(f"     ⚠  {msg}")
            resultados.append({
                "registro_id": registro_id,
                "nodo": item.get("nodo", ""),
                "descripcion": descripcion,
                "query": query,
                "estado": f"error: {msg}",
                "total_candidatas": 0,
                "fuentes_candidatas": [],
                "timestamp": datetime.now().isoformat(),
            })

        time.sleep(1)

    encontradas = sum(r["total_candidatas"] for r in resultados if isinstance(r.get("total_candidatas"), int))
    print(f"\n  ✅  Búsqueda fuentes completada — {encontradas} candidatas en {len(resultados)} búsquedas")
    return resultados


# ─── Modo 3: Ampliar nodos — preguntas urgentes ──────────────────────────────

def ampliar_nodos(
    app: Any,
    solo_nodo: str | None = None,
    limite: int | None = None,
) -> list[dict]:
    """
    Ejecuta búsquedas dirigidas a las preguntas urgentes de VACIOS.md y a la
    ampliación general de todos los nodos.
    """
    print("\n📋  Modo 3 — Ampliando nodos con búsquedas temáticas")

    urgentes = _BUSQUEDAS_VACIOS_URGENTES
    generales = _BUSQUEDAS_AMPLIACION_GENERAL

    if solo_nodo:
        urgentes = [b for b in urgentes if b.get("nodo") == solo_nodo]
        generales = [b for b in generales if b.get("nodo") == solo_nodo]

    todas = urgentes + generales
    if limite:
        todas = todas[:limite]

    print(f"    Búsquedas: {len(todas)} "
          f"({len(urgentes)} urgentes + {len(generales)} generales)")

    resultados: list[dict] = []

    for item in todas:
        query = item["query"]
        descripcion = item.get("descripcion", query[:70])
        pregunta_id = item.get("pregunta_id", "")
        nodo = item.get("nodo", "")
        etiqueta = f"[{pregunta_id or nodo}]" if (pregunta_id or nodo) else ""
        print(f"\n  → {etiqueta} {descripcion[:65]}")
        print(f"    Query: {query[:80]}")

        try:
            resp = app.search(query, limit=5)
            docs = getattr(resp, "web", None) or getattr(resp, "data", None)
            if docs is None:
                docs = resp if isinstance(resp, list) else []

            hallazgos: list[dict] = []
            for doc in docs:
                if hasattr(doc, "model_dump"):
                    d = doc.model_dump()
                elif hasattr(doc, "__dict__"):
                    d = doc.__dict__
                else:
                    d = dict(doc) if isinstance(doc, dict) else {}
                meta = d.get("metadata") or {}
                titulo = d.get("title") or (meta.get("title", "") or meta.get("og:title", "")) if isinstance(meta, dict) else d.get("title", "")
                url = d.get("url", "")
                desc = d.get("description") or ((meta.get("description", "") or meta.get("og:description", "")) if isinstance(meta, dict) else "")
                extracto = _texto_breve(d.get("markdown") or "", 400)
                if titulo or url:
                    hallazgos.append({
                        "titulo": titulo,
                        "url": url,
                        "descripcion": _texto_breve(desc, 200),
                        "extracto": extracto,
                    })

            n = len(hallazgos)
            icono = "✓" if n > 0 else "○"
            print(f"     {icono} {n} resultado(s)")

            resultados.append({
                "pregunta_id": pregunta_id,
                "nodo": nodo,
                "descripcion": descripcion,
                "query": query,
                "estado": "ok",
                "total_resultados": n,
                "hallazgos": hallazgos,
                "timestamp": datetime.now().isoformat(),
            })

        except Exception as exc:
            msg = _mensaje_error_firecrawl(exc)
            print(f"     ⚠  {msg}")
            resultados.append({
                "pregunta_id": pregunta_id,
                "nodo": nodo,
                "descripcion": descripcion,
                "query": query,
                "estado": f"error: {msg}",
                "total_resultados": 0,
                "hallazgos": [],
                "timestamp": datetime.now().isoformat(),
            })

        time.sleep(1)

    total_hallazgos = sum(r.get("total_resultados", 0) for r in resultados)
    print(f"\n  ✅  Ampliación completada — {total_hallazgos} hallazgos en {len(resultados)} búsquedas")
    return resultados


# ─── Generación de reporte Markdown ──────────────────────────────────────────

def generar_reporte_md(resultado_final: dict) -> str:
    """Genera un reporte Markdown legible a partir del JSON de resultados."""
    fecha = resultado_final.get("fecha_consulta", HOY)
    lineas: list[str] = [
        "# Reporte Firecrawl — Validación de Citas y Ampliación de Nodos",
        "",
        f"> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  ",
        f"> Fecha de ejecución: {fecha}  ",
        f"> API: {resultado_final.get('api', 'Firecrawl')}",
        "",
        "---",
        "",
        "## Resumen ejecutivo",
        "",
    ]

    # Resumen
    resumen = resultado_final.get("resumen", {})
    for clave, valor in resumen.items():
        lineas.append(f"- **{clave}**: {valor}")
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # Sección 1: Validación de URLs
    validaciones = resultado_final.get("validacion_urls", [])
    if validaciones:
        ok = [v for v in validaciones if v.get("estado") == "ok"]
        sin_contenido = [v for v in validaciones if v.get("estado") == "sin_contenido"]
        errores = [v for v in validaciones if v.get("estado", "").startswith("error")]
        lineas += [
            "## 1. Validación de URLs del Catálogo de Fuentes",
            "",
            f"| Estado | Cantidad |",
            f"|--------|----------|",
            f"| ✅ Accesible con contenido | {len(ok)} |",
            f"| ⚠ Accesible sin contenido | {len(sin_contenido)} |",
            f"| ❌ Error de acceso | {len(errores)} |",
            f"| **Total** | **{len(validaciones)}** |",
            "",
        ]
        if errores:
            lineas.append("### URLs con error de acceso")
            lineas.append("")
            for v in errores:
                lineas.append(f"- **[{v['fuente_id']}]** `{v['url']}`")
                lineas.append(f"  - Error: `{v['estado']}`")
            lineas.append("")
        if ok:
            lineas.append("### URLs validadas con extracto de contenido")
            lineas.append("")
            for v in ok[:10]:  # Mostrar primeras 10
                lineas.append(f"#### [{v['fuente_id']}] {v.get('titulo_pagina', '')[:60] or v['url'][:60]}")
                lineas.append("")
                lineas.append(f"> URL: `{v['url']}`")
                if v.get("extracto"):
                    lineas.append(f"> ")
                    lineas.append(f"> {v['extracto'][:300]}")
                lineas.append("")
        lineas.append("---")
        lineas.append("")

    # Sección 2: Fuentes faltantes
    fuentes = resultado_final.get("fuentes_faltantes", [])
    if fuentes:
        lineas += [
            "## 2. Fuentes Candidatas para Registros sin Cita",
            "",
        ]
        for item in fuentes:
            if not item.get("fuentes_candidatas"):
                continue
            lineas.append(f"### [{item.get('registro_id', '?')}] — {item.get('descripcion', '')[:80]}")
            lineas.append("")
            lineas.append(f"*Query utilizada:* `{item['query'][:100]}`")
            lineas.append("")
            for c in item["fuentes_candidatas"][:3]:
                titulo = c.get("titulo", "Sin título")
                url = c.get("url", "")
                desc = c.get("descripcion", "")
                lineas.append(f"- **{titulo}**")
                if url:
                    lineas.append(f"  - URL: <{url}>")
                if desc:
                    lineas.append(f"  - {desc[:150]}")
            lineas.append("")
        lineas.append("---")
        lineas.append("")

    # Sección 3: Ampliación de nodos
    ampliacion = resultado_final.get("ampliacion_nodos", [])
    if ampliacion:
        lineas += [
            "## 3. Hallazgos para Ampliación de Nodos",
            "",
        ]
        for item in ampliacion:
            if not item.get("hallazgos"):
                continue
            pid = item.get("pregunta_id", "")
            nodo = item.get("nodo", "")
            etiqueta = f"[{pid}]" if pid else f"[Nodo {nodo}]"
            lineas.append(f"### {etiqueta} — {item.get('descripcion', '')[:80]}")
            lineas.append("")
            lineas.append(f"*Query:* `{item['query'][:100]}`")
            lineas.append("")
            for h in item["hallazgos"][:3]:
                titulo = h.get("titulo", "Sin título")
                url = h.get("url", "")
                desc = h.get("descripcion", "")
                extracto = h.get("extracto", "")
                lineas.append(f"- **{titulo}**")
                if url:
                    lineas.append(f"  - URL: <{url}>")
                if desc:
                    lineas.append(f"  - {desc[:150]}")
                if extracto:
                    lineas.append(f"  - *Extracto:* {extracto[:200]}")
            lineas.append("")
        lineas.append("---")
        lineas.append("")

    # Nota metodológica
    lineas += [
        "## Nota metodológica",
        "",
        "Los resultados de Firecrawl son candidatos que requieren verificación manual antes de",
        "incorporarse como fuentes definitivas al catálogo. Para cada hallazgo:",
        "",
        "1. Verificar que el contenido corresponde al tema buscado",
        "2. Comprobar la autoría y confiabilidad de la fuente",
        "3. Si es válida, agregarla al catálogo con el formato Chicago y asignarle ID `F###`",
        "4. Actualizar el registro en el nodo correspondiente con el campo `fuente` o `fuentes_candidatas`",
        "",
        f"*Generado por: `tools/validar_citas_firecrawl.py` — {fecha}*",
    ]

    return "\n".join(lineas)


# ─── Guardado de resultados ───────────────────────────────────────────────────

def guardar_resultados(datos: dict, reporte_md: str) -> tuple[Path, Path]:
    ruta_json = DATOS_INVESTIGACION / f"firecrawl_validacion_{HOY}.json"
    ruta_md = DATOS_INVESTIGACION / f"firecrawl_reporte_{HOY}.md"

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    ruta_md.write_text(reporte_md, encoding="utf-8")

    print(f"\n  💾 JSON guardado:    {ruta_json.relative_to(ROOT)}")
    print(f"  💾 Reporte Markdown: {ruta_md.relative_to(ROOT)}")
    return ruta_json, ruta_md


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida citas, busca fuentes faltantes y amplía nodos "
            "usando la API de Firecrawl."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--modo", "-m",
        choices=["validar", "fuentes", "ampliar", "todo"],
        default="todo",
        help=(
            "Modo de operación: "
            "'validar' = validar URLs del catálogo, "
            "'fuentes' = buscar fuentes para registros sin cita, "
            "'ampliar' = búsquedas para ampliar nodos, "
            "'todo' = los tres modos (predeterminado)"
        ),
    )
    parser.add_argument(
        "--nodo", "-n",
        metavar="NODO",
        help="Filtrar por nodo específico (ej. '009', '010')",
    )
    parser.add_argument(
        "--limite", "-l",
        type=int,
        metavar="N",
        help="Limitar el número de búsquedas por modo",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 65}")
    print("   VALIDACIÓN DE CITAS + AMPLIACIÓN DE NODOS — Firecrawl")
    print(f"{'=' * 65}")

    # Verificar dependencias
    if not _FIRECRAWL_OK:
        print(
            "\n❌  firecrawl-py no está instalado.\n"
            "     Instala con:  pip install firecrawl-py\n"
        )
        return 1

    if not _FIRECRAWL_API_KEY:
        print(
            "\n❌  No se encontró FIRECRAWL_API_KEY.\n"
            "     Opciones:\n"
            "       1. Crea un archivo .env en la raíz con:\n"
            "             FIRECRAWL_API_KEY=fc-xxxx\n"
            "       2. Exporta la variable:\n"
            "             export FIRECRAWL_API_KEY=fc-xxxx\n"
            "     Obtén una clave gratuita en https://www.firecrawl.dev\n"
        )
        return 1

    # Inicializar cliente
    try:
        app = _FirecrawlApp(api_key=_FIRECRAWL_API_KEY)
        print(f"\n  ✅  Cliente Firecrawl inicializado")
    except Exception as exc:
        print(f"\n❌  Error al inicializar Firecrawl: {exc}\n")
        return 1

    modo = args.modo
    nodo = args.nodo
    limite = args.limite

    if nodo:
        print(f"    Nodo filtrado: {nodo}")
    if limite:
        print(f"    Límite por modo: {limite}")

    # Ejecutar modos
    resultado_final: dict = {
        "herramienta": "validar_citas_firecrawl",
        "fecha_consulta": datetime.now().isoformat(),
        "api": "Firecrawl",
        "modo": modo,
        "nodo_filtro": nodo,
        "limite": limite,
    }

    validacion_urls: list[dict] = []
    fuentes_faltantes: list[dict] = []
    ampliacion_nodos: list[dict] = []

    if modo in ("validar", "todo"):
        validacion_urls = validar_urls_catalogo(app, limite if modo == "validar" else None)
        resultado_final["validacion_urls"] = validacion_urls

    if modo in ("fuentes", "todo"):
        fuentes_faltantes = buscar_fuentes_faltantes(
            app, nodo, limite if modo == "fuentes" else None
        )
        resultado_final["fuentes_faltantes"] = fuentes_faltantes

    if modo in ("ampliar", "todo"):
        ampliacion_nodos = ampliar_nodos(
            app, nodo, limite if modo == "ampliar" else None
        )
        resultado_final["ampliacion_nodos"] = ampliacion_nodos

    # Resumen
    resumen: dict = {}
    if validacion_urls:
        ok = sum(1 for v in validacion_urls if v.get("estado") == "ok")
        resumen["URLs validadas"] = f"{ok}/{len(validacion_urls)} accesibles"
    if fuentes_faltantes:
        total_cand = sum(
            r.get("total_candidatas", 0) for r in fuentes_faltantes
            if isinstance(r.get("total_candidatas"), int)
        )
        resumen["Fuentes candidatas encontradas"] = str(total_cand)
        resumen["Registros sin fuente procesados"] = str(len(fuentes_faltantes))
    if ampliacion_nodos:
        total_h = sum(r.get("total_resultados", 0) for r in ampliacion_nodos)
        resumen["Hallazgos de ampliación"] = str(total_h)
        resumen["Búsquedas de ampliación realizadas"] = str(len(ampliacion_nodos))

    resultado_final["resumen"] = resumen

    # Guardar
    reporte_md = generar_reporte_md(resultado_final)
    guardar_resultados(resultado_final, reporte_md)

    print(f"\n{'=' * 65}")
    print("  ✅  Proceso completado")
    for k, v in resumen.items():
        print(f"      {k}: {v}")
    print(f"{'=' * 65}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
