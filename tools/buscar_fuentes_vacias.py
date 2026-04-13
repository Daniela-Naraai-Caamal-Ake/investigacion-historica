#!/usr/bin/env python3
"""
buscar_fuentes_vacias.py
========================
Detecta automáticamente los registros en los archivos HOPELCHEN_NODO_*.json
que carecen de campo de fuente, rastrea su contexto y realiza búsquedas web
en fuentes académicas y de referencia públicas para encontrar fuentes candidatas
que respalden cada registro.

Uso:
    python tools/buscar_fuentes_vacias.py            # Busca en todos los registros sin fuente
    python tools/buscar_fuentes_vacias.py --parchear # También agrega fuentes_candidatas al JSON
    python tools/buscar_fuentes_vacias.py --seco     # Solo detecta vacíos, sin búsqueda web
    python tools/buscar_fuentes_vacias.py --nodo 004 # Solo procesa el nodo especificado

Fuentes consultadas:
    Wikipedia  — API REST pública en español e inglés (sin clave)
    OpenLibrary — Catálogo abierto de libros (Open Library / Internet Archive)
    DuckDuckGo  — Búsqueda web general (HTML lite, sin clave)

Salidas:
    datos/investigacion/fuentes_vacias_YYYYMMDD.json
        Reporte completo con los registros detectados, las consultas realizadas
        y las fuentes candidatas encontradas.

    Cuando se usa --parchear:
        Agrega el campo ``fuentes_candidatas`` a cada registro sin fuente
        directamente en el archivo NODO correspondiente (no sobreescribe fuentes
        existentes).

Dependencias:
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
DATOS_INVESTIGACION = ROOT / "datos" / "investigacion"
DATOS_INVESTIGACION.mkdir(parents=True, exist_ok=True)

HOY = datetime.now().strftime("%Y%m%d")

# ─── Importar dependencias opcionales ────────────────────────────────────────

try:
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False


def _verificar_dependencias() -> None:
    if not _DEPS_OK:
        print(
            "\n❌  Dependencias faltantes. Instala con:\n"
            "     pip install requests beautifulsoup4\n"
        )
        sys.exit(1)


# ─── Campos de fuente reconocidos (igual que validar_datos.py) ─────────────

CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica", "fuente_primaria",
    "fuente_secundaria", "fuentes",
]


def _tiene_fuente(registro: dict) -> bool:
    """Devuelve True si el registro tiene al menos un campo de fuente con valor."""
    for campo in CAMPOS_FUENTE:
        val = registro.get(campo)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return True
        if isinstance(val, (dict, list)) and val:
            return True
    return False


# ─── Detección de registros sin fuente ────────────────────────────────────────

def detectar_registros_sin_fuente(filtro_nodo: str | None = None) -> list[dict]:
    """
    Recorre todos los HOPELCHEN_NODO_*.json y devuelve una lista de registros
    que no tienen campo de fuente.

    Cada elemento de la lista es un dict con:
        archivo, nodo_id, titulo_nodo, registro  (el objeto completo del registro)
    """
    encontrados: list[dict] = []

    patron = f"HOPELCHEN_NODO_{filtro_nodo}*.json" if filtro_nodo else "HOPELCHEN_NODO_*.json"
    for path in sorted(DATOS_HOPELCHEN.glob(patron)):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  ⚠  No se pudo leer {path.name}: {exc}")
            continue

        nodo_id = data.get("nodo_id", path.stem)
        titulo_nodo = data.get("titulo", "")

        for reg in data.get("registros", []):
            if not isinstance(reg, dict):
                continue
            if not _tiene_fuente(reg):
                encontrados.append({
                    "archivo": path.name,
                    "nodo_id": nodo_id,
                    "titulo_nodo": titulo_nodo,
                    "registro": reg,
                })

    return encontrados


# ─── Construcción de consultas de búsqueda ────────────────────────────────────

_STOPWORDS_ES = frozenset({
    "para", "como", "desde", "hasta", "entre", "sobre", "bajo", "ante",
    "tras", "según", "pero", "sino", "este", "esta", "estos", "estas",
    "cual", "cuyo", "cuya", "toda", "todo", "todos", "todas",
    "cruce", "datos", "transversal", "análisis", "síntesis",
    "emerge", "patrón", "registros", "nodos", "cruzar",
})

_PREFIJOS_SINTETICOS = ("CRUCE", "ANÁLISIS", "SÍNTESIS", "MAPA DE")

# Patrón que aparece en descripciones de síntesis: "Al cruzar los registros..."
import re as _re
_RE_INTRO_SINTETICA = _re.compile(
    r"^(al\s+cruzar\s+los\s+registros\s+de\s+los\s+nodos\s+[\d\-,]+[,.]?\s*"
    r"|análisis\s+de\s+síntesis\.\s*"
    r"|análisis\s+transversal\.\s*)",
    _re.IGNORECASE,
)


def _terminos_clave(texto: str, max_palabras: int = 6) -> str:
    """
    Extrae hasta ``max_palabras`` palabras significativas de ``texto``,
    descartando stopwords y prefijos de registros sintéticos.
    """
    # Quitar prefijo tipo "CRUCE DE DATOS: " o "ANÁLISIS TRANSVERSAL. "
    for pref in _PREFIJOS_SINTETICOS:
        if texto.upper().startswith(pref):
            # Saltar hasta el primer separador (: o .)
            for sep in (":", "."):
                idx = texto.find(sep)
                if idx != -1 and idx < 60:
                    texto = texto[idx + 1:].strip()
                    break

    # Quitar intro formulaica "Al cruzar los registros de los Nodos 001-009, ..."
    texto = _RE_INTRO_SINTETICA.sub("", texto).strip()

    palabras = [
        w.strip(".,;:()[]¿?¡!\"'")
        for w in texto.split()
        if len(w) > 3 and w.lower().strip(".,;:()[]¿?¡!\"'") not in _STOPWORDS_ES
    ]
    return " ".join(palabras[:max_palabras])


def _construir_consultas(registro: dict) -> list[dict]:
    """
    A partir del contenido de un registro, genera una lista de consultas
    de búsqueda orientadas a encontrar fuentes académicas o bibliográficas.

    Cada consulta es un dict con: ``motor``, ``query``, ``descripcion``.
    """
    reg = registro["registro"]
    consultas: list[dict] = []

    subtitulo = reg.get("subtitulo", "")
    descripcion = reg.get("descripcion", "")
    lugar = reg.get("lugar", "")
    fecha = reg.get("fecha_evento", "")
    tags = reg.get("tags", [])
    tipo_dato = reg.get("tipo_dato", "")
    es_sintetico = (
        "CRUCE" in subtitulo.upper()
        or "TRANSVERSAL" in tipo_dato.upper()
        or "SÍNTESIS" in subtitulo.upper()
    )

    # ── Término principal ────────────────────────────────────────────────────
    # Para síntesis: extraer términos del subtítulo limpiando prefijos
    # Para registros normales: primeras palabras significativas
    if es_sintetico:
        # Usar descripción en lugar del subtítulo, que es más informativo
        termino_principal = _terminos_clave(descripcion, max_palabras=7)
        if not termino_principal:
            termino_principal = _terminos_clave(subtitulo, max_palabras=6)
    else:
        termino_principal = _terminos_clave(subtitulo, max_palabras=6)

    # Añadir contexto geográfico si no está ya incluido
    lugar_corto = lugar.split(",")[0].strip() if lugar else ""
    if lugar_corto and lugar_corto not in termino_principal:
        termino_principal_geo = f"{termino_principal} {lugar_corto}".strip()
    else:
        termino_principal_geo = termino_principal

    # ── Consultas Wikipedia ──────────────────────────────────────────────────
    consultas.append({
        "motor": "wikipedia_es",
        "query": termino_principal_geo,
        "descripcion": f"Wikipedia (es) — {subtitulo[:60]}",
    })

    # En inglés si el tema tiene proyección internacional
    terminos_ingles_flag = {"chicle", "chewing gum", "maya", "menonita", "mennonite",
                            "transgénica", "soya", "resistencia", "colonial"}
    texto_completo = (subtitulo + " " + descripcion).lower()
    if any(t in texto_completo for t in terminos_ingles_flag):
        # Traducir manualmente algunos términos comunes para búsqueda en EN
        q_en = (termino_principal_geo
                .replace("economía chiclera", "chicle industry")
                .replace("resistencia maya", "Maya resistance")
                .replace("conocimiento maya", "Maya knowledge")
                .replace("poder político", "political power"))
        consultas.append({
            "motor": "wikipedia_en",
            "query": q_en,
            "descripcion": f"Wikipedia (en) — {subtitulo[:60]}",
        })

    # ── Consultas OpenLibrary ────────────────────────────────────────────────
    if tags:
        ol_terms = [lugar_corto] if lugar_corto else []
        ol_terms.extend(str(t) for t in tags[:2])
        consultas.append({
            "motor": "openlibrary",
            "query": " ".join(ol_terms),
            "descripcion": f"OpenLibrary — {subtitulo[:60]}",
        })
    elif lugar_corto:
        consultas.append({
            "motor": "openlibrary",
            "query": f"{lugar_corto} historia",
            "descripcion": f"OpenLibrary — {lugar_corto} historia",
        })

    # Si hay autores explícitos en el registro (registro bibliográfico 007-H)
    fuentes_no_consultadas = reg.get("fuentes_identificadas_no_consultadas", [])
    for fuente_ref in fuentes_no_consultadas[:3]:
        autor = fuente_ref.get("autor", "")
        año = str(fuente_ref.get("año", ""))
        titulo_obra = fuente_ref.get("titulo", "")
        if autor:
            q = " ".join(p for p in [autor, año, titulo_obra] if p).strip()
            consultas.append({
                "motor": "openlibrary",
                "query": q,
                "descripcion": f"OpenLibrary — obra de {autor} ({año})",
            })

    # ── Consulta DuckDuckGo ──────────────────────────────────────────────────
    ddg_terms = [termino_principal]
    if lugar_corto and lugar_corto not in termino_principal:
        ddg_terms.append(lugar_corto)
    # Añadir período histórico si es corto y preciso
    if fecha and not es_sintetico:
        inicio = fecha.split("—")[0].split("–")[0].strip()[:4]
        if inicio.isdigit():
            ddg_terms.append(inicio)

    consultas.append({
        "motor": "duckduckgo",
        "query": " ".join(ddg_terms),
        "descripcion": f"DuckDuckGo — {subtitulo[:60]}",
    })

    return consultas


# ─── Motores de búsqueda ──────────────────────────────────────────────────────

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; investigacion-historica/1.0; "
        "+https://github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica)"
    )
}


def _get(url: str, params: dict | None = None, timeout: int = 20) -> "requests.Response | None":
    """GET con manejo de errores. Devuelve None si la petición falla."""
    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.exceptions.HTTPError as e:
        print(f"    ⚠  HTTP {e.response.status_code}: {url[:70]}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"    ⚠  Sin conexión: {url[:70]}")
        return None
    except requests.exceptions.Timeout:
        print(f"    ⚠  Tiempo agotado: {url[:70]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    ⚠  Error ({type(e).__name__}): {url[:70]}")
        return None


def _buscar_wikipedia(query: str, lang: str = "es") -> list[dict]:
    """
    Busca en Wikipedia usando la API de búsqueda pública y devuelve
    hasta 5 artículos candidatos con título, extracto y URL.
    """
    # Paso 1: buscar títulos que coinciden con la query
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    params_search = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 5,
        "format": "json",
        "utf8": 1,
    }
    resp = _get(search_url, params=params_search)
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
        # Limpiar etiquetas HTML del snippet
        try:
            from bs4 import BeautifulSoup as _BS
            snippet = _BS(snippet, "html.parser").get_text()
        except Exception:
            snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "")

        url_articulo = f"https://{lang}.wikipedia.org/wiki/{quote_plus(titulo.replace(' ', '_'))}"
        resultados.append({
            "titulo": titulo,
            "extracto": snippet[:300],
            "url": url_articulo,
            "idioma": lang,
        })

    return resultados


def _buscar_openlibrary(query: str) -> list[dict]:
    """
    Busca en Open Library (openlibrary.org) y devuelve hasta 5 obras
    con título, autores, año y URL de catálogo.
    """
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
        titulo = doc.get("title", "")
        autores = doc.get("author_name", [])
        año = doc.get("first_publish_year", "")
        key = doc.get("key", "")
        url_obra = f"https://openlibrary.org{key}" if key else ""
        resultados.append({
            "titulo": titulo,
            "autores": autores,
            "año_primera_publicacion": año,
            "url_catalogo": url_obra,
        })

    return resultados


def _buscar_duckduckgo(query: str) -> list[dict]:
    """
    Busca en DuckDuckGo Lite (HTML) y extrae hasta 5 resultados con título
    y URL. DuckDuckGo Lite no requiere JavaScript ni API key.
    """
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

    # DuckDuckGo Lite usa <a class="result-link"> para los enlaces de resultados
    for link in soup.select("a.result-link")[:5]:
        titulo = link.get_text(strip=True)
        href = link.get("href", "")
        # Los snippets están en el siguiente <td> de tipo result-snippet
        snippet = ""
        parent_tr = link.find_parent("tr")
        if parent_tr:
            # El snippet está en la siguiente fila de la tabla
            next_tr = parent_tr.find_next_sibling("tr")
            if next_tr:
                snippet_td = next_tr.find("td", class_="result-snippet")
                if snippet_td:
                    snippet = snippet_td.get_text(strip=True)[:300]

        if titulo or href:
            resultados.append({
                "titulo": titulo,
                "url": href,
                "snippet": snippet,
            })

    return resultados


# ─── Ejecución de consultas ───────────────────────────────────────────────────

def ejecutar_consulta(consulta: dict) -> dict:
    """
    Ejecuta una consulta de búsqueda y devuelve los resultados.

    Returns dict con: motor, query, descripcion, estado, resultados, timestamp
    """
    motor = consulta["motor"]
    query = consulta["query"]

    print(f"    🔎  [{motor}] {query[:70]}…")

    resultados: list[dict] = []
    estado = "ok"

    try:
        if motor == "wikipedia_es":
            resultados = _buscar_wikipedia(query, lang="es")
        elif motor == "wikipedia_en":
            resultados = _buscar_wikipedia(query, lang="en")
        elif motor == "openlibrary":
            resultados = _buscar_openlibrary(query)
        elif motor == "duckduckgo":
            resultados = _buscar_duckduckgo(query)
        else:
            estado = "motor_desconocido"
    except Exception as exc:
        estado = f"error: {exc}"
        resultados = []

    n = len(resultados)
    icono = "✓" if n > 0 else "○"
    print(f"       {icono}  {n} resultado(s)")
    time.sleep(1)  # Respetar los servidores

    return {
        "motor": motor,
        "query": query,
        "descripcion": consulta.get("descripcion", ""),
        "estado": estado,
        "total_resultados": n,
        "resultados": resultados,
        "timestamp": datetime.now().isoformat(),
    }


# ─── Procesamiento de un registro sin fuente ─────────────────────────────────

def procesar_registro(entrada: dict, modo_seco: bool = False) -> dict:
    """
    Para un registro sin fuente, construye consultas, las ejecuta (si no es
    modo seco) y devuelve el resultado consolidado.
    """
    reg = entrada["registro"]
    rid = reg.get("registro_id", "?")
    subtitulo = reg.get("subtitulo", "")

    print(f"\n  📄  Registro {rid} — {subtitulo[:70]}")
    print(f"      Archivo: {entrada['archivo']}")

    consultas = _construir_consultas(entrada)
    print(f"      Consultas generadas: {len(consultas)}")

    if modo_seco:
        busquedas_ejecutadas = []
        for c in consultas:
            busquedas_ejecutadas.append({
                "motor": c["motor"],
                "query": c["query"],
                "descripcion": c.get("descripcion", ""),
                "estado": "no_ejecutado (modo_seco)",
                "total_resultados": 0,
                "resultados": [],
            })
    else:
        busquedas_ejecutadas = [ejecutar_consulta(c) for c in consultas]

    # Consolidar fuentes candidatas (todas con al menos un resultado)
    fuentes_candidatas: list[dict] = []
    for busqueda in busquedas_ejecutadas:
        for resultado in busqueda.get("resultados", []):
            candidata: dict = {
                "motor_busqueda": busqueda["motor"],
                "query_utilizada": busqueda["query"],
            }
            candidata.update(resultado)
            fuentes_candidatas.append(candidata)

    return {
        "registro_id": rid,
        "archivo": entrada["archivo"],
        "nodo_id": entrada["nodo_id"],
        "subtitulo": subtitulo,
        "busquedas": busquedas_ejecutadas,
        "fuentes_candidatas": fuentes_candidatas,
        "total_candidatas": len(fuentes_candidatas),
        "nota": (
            "Estas son fuentes CANDIDATAS encontradas automáticamente. "
            "Deben ser verificadas manualmente antes de agregarlas como "
            "fuentes definitivas del registro."
        ),
    }


# ─── Parchear registros en los JSON de nodo ──────────────────────────────────

def parchear_registro(entrada: dict, fuentes_candidatas: list[dict]) -> bool:
    """
    Agrega el campo ``fuentes_candidatas`` al registro correspondiente
    dentro de su archivo NODO_*.json. No sobreescribe fuentes existentes.

    Devuelve True si el archivo fue modificado.
    """
    archivo = DATOS_HOPELCHEN / entrada["archivo"]
    rid = entrada["registro"]["registro_id"]

    try:
        with open(archivo, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  ⚠  No se pudo leer {archivo.name} para parchear: {exc}")
        return False

    modificado = False
    for reg in data.get("registros", []):
        if reg.get("registro_id") == rid:
            if not reg.get("fuentes_candidatas"):
                reg["fuentes_candidatas"] = fuentes_candidatas
                reg["nota_busqueda_automatica"] = (
                    f"Fuentes candidatas generadas automáticamente el {HOY} "
                    "por tools/buscar_fuentes_vacias.py. Verificar manualmente."
                )
                modificado = True
            else:
                print(f"    ℹ  {rid} ya tiene 'fuentes_candidatas'; no se sobreescribe.")
            break

    if modificado:
        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"    ✅  {archivo.name} parcheado — {rid} actualizado")
        except OSError as exc:
            print(f"  ⚠  No se pudo escribir {archivo.name}: {exc}")
            return False

    return modificado


# ─── Guardar reporte ──────────────────────────────────────────────────────────

def guardar_reporte(resultados: list[dict], registros_detectados: int) -> Path:
    """Guarda el reporte completo en datos/investigacion/."""
    ruta = DATOS_INVESTIGACION / f"fuentes_vacias_{HOY}.json"

    reporte = {
        "herramienta": "buscar_fuentes_vacias.py",
        "fecha_ejecucion": datetime.now().isoformat(),
        "repositorio": "Hopelchén: 2000 años de historia",
        "resumen": {
            "registros_sin_fuente_detectados": registros_detectados,
            "registros_procesados": len(resultados),
            "total_candidatas_encontradas": sum(
                r.get("total_candidatas", 0) for r in resultados
            ),
        },
        "resultados": resultados,
        "nota_metodologica": (
            "Este reporte fue generado automáticamente buscando en Wikipedia (ES/EN), "
            "Open Library y DuckDuckGo. Las fuentes candidatas deben verificarse "
            "manualmente antes de incorporarlas al repositorio. "
            "Los registros de tipo 'CRUCE TRANSVERSAL' son síntesis analíticas "
            "que pueden no tener una única fuente externa directa."
        ),
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"\n  💾  Reporte guardado: {ruta.relative_to(ROOT)}")
    return ruta


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Detecta registros sin fuente en los nodos históricos y realiza "
            "búsquedas web automáticas para encontrar fuentes candidatas."
        )
    )
    parser.add_argument(
        "--parchear",
        action="store_true",
        help=(
            "Agrega el campo 'fuentes_candidatas' directamente en los archivos "
            "NODO_*.json para cada registro sin fuente (no sobreescribe si ya existe)."
        ),
    )
    parser.add_argument(
        "--seco",
        action="store_true",
        help=(
            "Solo detecta y lista los registros sin fuente con las consultas "
            "que se realizarían, sin ejecutar búsquedas web."
        ),
    )
    parser.add_argument(
        "--nodo",
        metavar="ID",
        help="Procesa únicamente el nodo con el ID especificado (ej: 004, 006).",
    )
    args = parser.parse_args()

    if not args.seco:
        _verificar_dependencias()

    print(f"\n{'=' * 65}")
    print("   BÚSQUEDA DE FUENTES — Registros sin fuente")
    print("   Hopelchén: 2000 años de historia")
    print(f"{'=' * 65}")
    print(f"📁 Directorio: {DATOS_HOPELCHEN}\n")

    # ── Paso 1: Detectar registros sin fuente ────────────────────────────────
    print("── Paso 1: Detectando registros sin campo de fuente…")
    entradas = detectar_registros_sin_fuente(filtro_nodo=args.nodo)

    if not entradas:
        print("\n✅  Todos los registros tienen fuente. No hay nada que buscar.")
        return 0

    print(f"\n⚠  {len(entradas)} registro(s) sin fuente detectado(s):\n")
    for e in entradas:
        rid = e["registro"].get("registro_id", "?")
        subtitulo = e["registro"].get("subtitulo", "")[:60]
        print(f"   • {e['archivo']} → {rid}: {subtitulo}")

    if args.seco:
        print(f"\n{'─' * 65}")
        print("── Modo seco: listando consultas que se realizarían…")
        for entrada in entradas:
            reg = entrada["registro"]
            rid = reg.get("registro_id", "?")
            consultas = _construir_consultas(entrada)
            print(f"\n  📄  {rid} — {reg.get('subtitulo','')[:60]}")
            for c in consultas:
                print(f"      [{c['motor']}] {c['query']}")
        return 0

    # ── Paso 2: Ejecutar búsquedas web ──────────────────────────────────────
    print(f"\n{'─' * 65}")
    print("── Paso 2: Ejecutando búsquedas web…")
    resultados: list[dict] = []

    for entrada in entradas:
        resultado = procesar_registro(entrada, modo_seco=False)
        resultados.append(resultado)

        # Parchear inmediatamente si se solicitó
        if args.parchear and resultado["fuentes_candidatas"]:
            parchear_registro(entrada, resultado["fuentes_candidatas"])

    # ── Paso 3: Guardar reporte ──────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print("── Paso 3: Guardando reporte…")
    ruta_reporte = guardar_reporte(resultados, len(entradas))

    # ── Resumen final ────────────────────────────────────────────────────────
    total_candidatas = sum(r.get("total_candidatas", 0) for r in resultados)

    print(f"\n{'=' * 65}")
    print("   RESUMEN")
    print(f"{'=' * 65}")
    print(f"  📋 Registros sin fuente procesados : {len(entradas)}")
    print(f"  🔍 Fuentes candidatas encontradas  : {total_candidatas}")
    print(f"  💾 Reporte                         : {ruta_reporte.relative_to(ROOT)}")
    if args.parchear:
        print("  ✏️  Los registros fueron parcheados con 'fuentes_candidatas'.")
    else:
        print("  ℹ️  Ejecuta con --parchear para agregar candidatas a los JSON.")
    print(f"{'=' * 65}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
