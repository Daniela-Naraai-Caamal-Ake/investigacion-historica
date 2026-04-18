#!/usr/bin/env python3
"""
validar_citas.py
================
Herramienta integral de validación y ampliación de investigación usando
búsqueda web pública (sin API key).

Realiza tres operaciones complementarias:

1. **Validar citas**: Comprueba que las URLs del ``fuentes/catalogo_fuentes.md``
   responden con HTTP 200 y extrae un fragmento de contenido.

2. **Buscar fuentes faltantes**: Para los registros de ``datos/hopelchen/`` que
   carecen de campo de fuente, lanza búsquedas en Wikipedia, OpenLibrary y
   DuckDuckGo y propone fuentes candidatas.

3. **Ampliar nodos**: Lanza búsquedas temáticas orientadas a las preguntas
   prioritarias de ``datos/VACIOS.md`` y a los nodos con más vacíos
   (especialmente Nodo 009 — Resistencia Maya y Nodo 010 — Conocimiento y Cultura).

Uso:
    python tools/validar_citas.py                   # Todo
    python tools/validar_citas.py --modo validar    # Solo validar URLs
    python tools/validar_citas.py --modo fuentes    # Solo buscar fuentes
    python tools/validar_citas.py --modo ampliar    # Solo ampliar nodos
    python tools/validar_citas.py --nodo 009        # Solo nodo específico
    python tools/validar_citas.py --limite 10       # Limitar búsquedas

Salidas (en ``datos/investigacion/``):
    busqueda_validacion_YYYYMMDD.json  — Resultados completos en JSON
    busqueda_reporte_YYYYMMDD.md       — Reporte legible en Markdown

Dependencias:
    pip install requests beautifulsoup4
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

# ─── Dependencias ─────────────────────────────────────────────────────────────

try:
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False

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


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; investigacion-historica/1.0; "
        "+https://github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica)"
    )
}


def _get(url: str, params: dict | None = None, timeout: int = 20) -> "requests.Response | None":
    """GET con manejo de errores. Devuelve None si la petición falla."""
    for intento in (1, 2):
        try:
            resp = requests.get(
                url, params=params, headers=_HEADERS,
                timeout=timeout, allow_redirects=True,
            )
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            print(f"    ⚠  HTTP {e.response.status_code}: {url[:70]}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"    ⚠  Sin conexión: {url[:70]}")
            if intento == 1:
                time.sleep(1)
                continue
            return None
        except requests.exceptions.Timeout:
            print(f"    ⚠  Tiempo agotado: {url[:70]}")
            if intento == 1:
                time.sleep(1)
                continue
            return None
        except requests.exceptions.RequestException as e:
            print(f"    ⚠  Error ({type(e).__name__}): {url[:70]}")
            return None
    return None


# ─── Motores de búsqueda ──────────────────────────────────────────────────────

from urllib.parse import quote_plus  # noqa: E402


def _buscar_wikipedia(query: str, lang: str = "es") -> list[dict]:
    """Busca en Wikipedia vía API REST y devuelve hasta 5 candidatos."""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 5,
        "format": "json",
        "utf8": 1,
    }
    resp = _get(url, params=params)
    if resp is None:
        return []
    try:
        data = resp.json()
    except ValueError:
        return []

    resultados: list[dict] = []
    for item in data.get("query", {}).get("search", []):
        titulo = item.get("title", "")
        snippet = item.get("snippet", "")
        try:
            snippet = BeautifulSoup(snippet, "html.parser").get_text()
        except Exception:
            snippet = snippet.replace('<span class="searchmatch">', "").replace("</span>", "")
        url_art = f"https://{lang}.wikipedia.org/wiki/{quote_plus(titulo.replace(' ', '_'))}"
        resultados.append({
            "titulo": titulo,
            "extracto": snippet[:300],
            "url": url_art,
            "idioma": lang,
        })
    return resultados


def _buscar_openlibrary(query: str) -> list[dict]:
    """Busca en Open Library y devuelve hasta 5 obras."""
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": 5, "fields": "title,author_name,first_publish_year,key"}
    resp = _get(url, params=params)
    if resp is None:
        return []
    try:
        data = resp.json()
    except ValueError:
        return []

    resultados: list[dict] = []
    for doc in data.get("docs", [])[:5]:
        key = doc.get("key", "")
        resultados.append({
            "titulo": doc.get("title", ""),
            "autores": doc.get("author_name", []),
            "año_primera_publicacion": doc.get("first_publish_year", ""),
            "url_catalogo": f"https://openlibrary.org{key}" if key else "",
        })
    return resultados


def _buscar_duckduckgo(query: str) -> list[dict]:
    """Busca en DuckDuckGo Lite (HTML, sin clave) y devuelve hasta 5 resultados."""
    url = "https://lite.duckduckgo.com/lite/"
    params = {"q": query, "kl": "mx-es"}
    resp = _get(url, params=params)
    if resp is None:
        return []
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return []

    resultados: list[dict] = []
    for link in soup.select("a.result-link")[:5]:
        titulo = link.get_text(strip=True)
        href = link.get("href", "")
        snippet = ""
        parent_tr = link.find_parent("tr")
        if parent_tr:
            next_tr = parent_tr.find_next_sibling("tr")
            if next_tr:
                snippet_td = next_tr.find("td", class_="result-snippet")
                if snippet_td:
                    snippet = snippet_td.get_text(strip=True)[:300]
        if titulo or href:
            resultados.append({"titulo": titulo, "url": href, "snippet": snippet})
    return resultados


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
    patron_id = re.compile(r'^## (F[X]?\d+)', re.MULTILINE)
    patron_url = re.compile(r'(https?://[^\s>)\]"\'<]+)')

    resultados: list[dict] = []
    secciones = list(patron_id.finditer(texto))

    for i, match_id in enumerate(secciones):
        fuente_id = match_id.group(1)
        inicio = match_id.start()
        fin = secciones[i + 1].start() if i + 1 < len(secciones) else len(texto)
        fragmento = texto[inicio:fin]

        urls_vistas: set[str] = set()
        for url in patron_url.findall(fragmento):
            url = url.rstrip(".,;:)")
            if url in urls_vistas:
                continue
            urls_vistas.add(url)
            linea_ctx = next(
                (ln.strip() for ln in fragmento.splitlines() if url in ln), ""
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

def validar_urls_catalogo(limite: int | None = None) -> list[dict]:
    """
    Para cada URL del catálogo, hace una petición GET y verifica que responde.
    Extrae título y fragmento de contenido vía BeautifulSoup.
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

        resp = _get(url, timeout=25)
        if resp is None:
            resultado = {
                "fuente_id": fuente_id,
                "url": url,
                "contexto_catalogo": item["contexto"],
                "estado": "error_conexion",
                "extracto": "",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"     ⚠  Sin respuesta")
        else:
            content_type = resp.headers.get("content-type", "")
            if "pdf" in content_type:
                titulo = ""
                extracto = f"[PDF — {len(resp.content)} bytes]"
                estado = "ok"
            else:
                try:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    titulo = soup.title.string.strip() if soup.title and soup.title.string else ""
                    # Extraer texto principal eliminando scripts/styles
                    for tag in soup(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    extracto = _texto_breve(
                        soup.get_text(separator=" ", strip=True), 400
                    )
                    estado = "ok" if extracto else "sin_contenido"
                except Exception:
                    titulo = ""
                    extracto = ""
                    estado = "sin_contenido"

            icono = "✓" if estado == "ok" else "○"
            print(f"     {icono} {titulo[:60] or '(sin título)'}")

            resultado = {
                "fuente_id": fuente_id,
                "url": url,
                "contexto_catalogo": item["contexto"],
                "estado": estado,
                "estado_http": resp.status_code,
                "titulo_pagina": titulo,
                "extracto": extracto,
                "timestamp": datetime.now().isoformat(),
            }

        resultados.append(resultado)
        time.sleep(1)

    ok = sum(1 for r in resultados if r["estado"] == "ok")
    print(f"\n  ✅  Validación completada — {ok}/{len(resultados)} URLs accesibles")
    return resultados


# ─── Utilidad de búsqueda multi-motor ────────────────────────────────────────

def _buscar_con_motores(query: str) -> list[dict]:
    """
    Lanza búsquedas en Wikipedia (ES+EN), OpenLibrary y DuckDuckGo.
    Devuelve lista combinada con campo 'motor_busqueda' y 'query_utilizada'.
    """
    candidatas: list[dict] = []

    for motor, fn in [
        ("wikipedia_es", lambda q: _buscar_wikipedia(q, lang="es")),
        ("wikipedia_en", lambda q: _buscar_wikipedia(q, lang="en")),
        ("openlibrary",  _buscar_openlibrary),
        ("duckduckgo",   _buscar_duckduckgo),
    ]:
        for r in fn(query):
            r["motor_busqueda"] = motor
            r["query_utilizada"] = query
            candidatas.append(r)
        time.sleep(0.5)

    return candidatas


# ─── Modo 2: Buscar fuentes para registros sin cita ──────────────────────────

def buscar_fuentes_faltantes(
    solo_nodo: str | None = None,
    limite: int | None = None,
) -> list[dict]:
    """
    Para registros sin fuente, genera queries y lanza búsquedas web públicas.
    """
    print("\n📋  Modo 2 — Buscando fuentes para registros sin cita")

    busquedas_especificas: list[dict] = []
    if solo_nodo == "009" or solo_nodo is None:
        busquedas_especificas.extend(_BUSQUEDAS_NODO_009)
    if solo_nodo == "010" or solo_nodo is None:
        busquedas_especificas.extend(_BUSQUEDAS_NODO_010)

    registros_sin_fuente = extraer_registros_sin_fuente(solo_nodo)
    busquedas_auto: list[dict] = []
    ids_especificos = {b.get("registro_id") for b in busquedas_especificas}
    for reg in registros_sin_fuente:
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

        candidatas = _buscar_con_motores(query)
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

        time.sleep(1)

    encontradas = sum(r["total_candidatas"] for r in resultados)
    print(f"\n  ✅  Búsqueda fuentes completada — {encontradas} candidatas en {len(resultados)} búsquedas")
    return resultados


# ─── Modo 3: Ampliar nodos — preguntas urgentes ──────────────────────────────

def ampliar_nodos(
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

        hallazgos = _buscar_con_motores(query)
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

        time.sleep(1)

    total_hallazgos = sum(r.get("total_resultados", 0) for r in resultados)
    print(f"\n  ✅  Ampliación completada — {total_hallazgos} hallazgos en {len(resultados)} búsquedas")
    return resultados


# ─── Generación de reporte Markdown ──────────────────────────────────────────

def generar_reporte_md(resultado_final: dict) -> str:
    """Genera un reporte Markdown legible a partir del JSON de resultados."""
    fecha = resultado_final.get("fecha_consulta", HOY)
    lineas: list[str] = [
        "# Reporte de Búsqueda Web — Validación de Citas y Ampliación de Nodos",
        "",
        f"> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  ",
        f"> Fecha de ejecución: {fecha}  ",
        f"> Motores: Wikipedia (ES/EN), OpenLibrary, DuckDuckGo",
        "",
        "---",
        "",
        "## Resumen ejecutivo",
        "",
    ]

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
            "| Estado | Cantidad |",
            "|--------|----------|",
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
                url = c.get("url") or c.get("url_catalogo", "")
                desc = c.get("snippet") or c.get("extracto", "")
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
                url = h.get("url") or h.get("url_catalogo", "")
                desc = h.get("snippet") or h.get("extracto", "")
                lineas.append(f"- **{titulo}**")
                if url:
                    lineas.append(f"  - URL: <{url}>")
                if desc:
                    lineas.append(f"  - {desc[:150]}")
            lineas.append("")
        lineas.append("---")
        lineas.append("")

    lineas += [
        "## Nota metodológica",
        "",
        "Los resultados son candidatos que requieren verificación manual antes de",
        "incorporarse como fuentes definitivas al catálogo. Para cada hallazgo:",
        "",
        "1. Verificar que el contenido corresponde al tema buscado",
        "2. Comprobar la autoría y confiabilidad de la fuente",
        "3. Si es válida, agregarla al catálogo con el formato Chicago y asignarle ID `F###`",
        "4. Actualizar el registro en el nodo correspondiente con el campo `fuente` o `fuentes_candidatas`",
        "",
        f"*Generado por: `tools/validar_citas.py` — {fecha}*",
    ]

    return "\n".join(lineas)


# ─── Guardado de resultados ───────────────────────────────────────────────────

def guardar_resultados(datos: dict, reporte_md: str) -> tuple[Path, Path]:
    ruta_json = DATOS_INVESTIGACION / f"busqueda_validacion_{HOY}.json"
    ruta_md = DATOS_INVESTIGACION / f"busqueda_reporte_{HOY}.md"

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
            "usando Wikipedia, OpenLibrary y DuckDuckGo (sin API key)."
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

    if not _DEPS_OK:
        print(
            "\n❌  Dependencias faltantes. Instala con:\n"
            "     pip install requests beautifulsoup4\n"
        )
        return 1

    print(f"\n{'=' * 65}")
    print("   BÚSQUEDA WEB — Validación de Citas y Ampliación de Nodos")
    print(f"{'=' * 65}")
    print("   Motores: Wikipedia (ES/EN) · OpenLibrary · DuckDuckGo")

    modo = args.modo
    nodo = args.nodo
    limite = args.limite

    if nodo:
        print(f"    Nodo filtrado: {nodo}")
    if limite:
        print(f"    Límite por modo: {limite}")

    resultado_final: dict = {
        "herramienta": "validar_citas",
        "fecha_consulta": datetime.now().isoformat(),
        "motores": ["wikipedia_es", "wikipedia_en", "openlibrary", "duckduckgo"],
        "modo": modo,
        "nodo_filtro": nodo,
        "limite": limite,
    }

    validacion_urls: list[dict] = []
    fuentes_faltantes: list[dict] = []
    ampliacion_nodos: list[dict] = []

    if modo in ("validar", "todo"):
        validacion_urls = validar_urls_catalogo(limite if modo == "validar" else None)
        resultado_final["validacion_urls"] = validacion_urls

    if modo in ("fuentes", "todo"):
        fuentes_faltantes = buscar_fuentes_faltantes(
            nodo, limite if modo == "fuentes" else None
        )
        resultado_final["fuentes_faltantes"] = fuentes_faltantes

    if modo in ("ampliar", "todo"):
        ampliacion_nodos = ampliar_nodos(
            nodo, limite if modo == "ampliar" else None
        )
        resultado_final["ampliacion_nodos"] = ampliacion_nodos

    resumen: dict = {}
    if validacion_urls:
        ok = sum(1 for v in validacion_urls if v.get("estado") == "ok")
        resumen["URLs validadas"] = f"{ok}/{len(validacion_urls)} accesibles"
    if fuentes_faltantes:
        total_cand = sum(r.get("total_candidatas", 0) for r in fuentes_faltantes)
        resumen["Fuentes candidatas encontradas"] = str(total_cand)
        resumen["Registros sin fuente procesados"] = str(len(fuentes_faltantes))
    if ampliacion_nodos:
        total_h = sum(r.get("total_resultados", 0) for r in ampliacion_nodos)
        resumen["Hallazgos de ampliación"] = str(total_h)
        resumen["Búsquedas de ampliación realizadas"] = str(len(ampliacion_nodos))

    resultado_final["resumen"] = resumen

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
