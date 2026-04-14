#!/usr/bin/env python3
"""
rastrear_fuentes.py
===================
Herramienta de búsqueda automatizada en fuentes digitales públicas relevantes
para el proyecto *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia.

Uso:
    python tools/rastrear_fuentes.py               # Ejecuta todos los módulos
    python tools/rastrear_fuentes.py --modulo pares
    python tools/rastrear_fuentes.py --modulo agn
    python tools/rastrear_fuentes.py --modulo scjn
    python tools/rastrear_fuentes.py --modulo poe_campeche
    python tools/rastrear_fuentes.py --modulo familysearch --guia

Módulos disponibles:
    pares         — PARES (Portal de Archivos Españoles / AGI Sevilla)
    agn           — Catálogo digital del AGN México
    scjn          — Buscador de jurisprudencia SCJN (caso soya transgénica)
    poe_campeche  — Periódico Oficial del Estado de Campeche (presidentes municipales)
    familysearch  — Guía de búsqueda en FamilySearch (registros coloniales)

Notas éticas y técnicas:
    - Todos los módulos acceden únicamente a recursos de acceso público.
    - Las búsquedas son de solo lectura (GET).
    - Los resultados crudos se guardan en datos/investigacion/.
    - Para archivos que requieren trámite presencial (Registro Civil, RAN),
      el módulo genera la solicitud de acceso en formato de texto.

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

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
DATOS_INVESTIGACION = ROOT / "datos" / "investigacion"
DATOS_INVESTIGACION.mkdir(parents=True, exist_ok=True)

# Fecha de hoy en formato YYYYMMDD para nombres de archivo
HOY = datetime.now().strftime("%Y%m%d")

# ─── Importar dependencias opcionales ────────────────────────────────────────

try:
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False



def _verificar_dependencias() -> None:
    if not _REQUESTS_OK:
        print(
            "\n❌  Dependencias faltantes. Instala con:\n"
            "     pip install requests beautifulsoup4\n"
        )
        sys.exit(1)


# ─── Utilidades comunes ───────────────────────────────────────────────────────

def guardar_resultados(nombre_modulo: str, datos: Any) -> Path:
    """Guarda los resultados en datos/investigacion/ con timestamp."""
    ruta = DATOS_INVESTIGACION / f"{nombre_modulo}_resultados_{HOY}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  💾 Resultados guardados: {ruta.relative_to(ROOT)}")
    return ruta


def _get_pagina(url: str, params: dict | None = None,
                headers: dict | None = None, timeout: int = 20) -> requests.Response | None:
    """Realiza una petición GET con manejo básico de errores."""
    _headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; investigacion-historica/1.0; "
            "+https://github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica)"
        )
    }
    if headers:
        _headers.update(headers)
    try:
        resp = requests.get(url, params=params, headers=_headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠  HTTP {e.response.status_code} en {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  ⚠  No se pudo conectar a {url}")
        return None
    except requests.exceptions.Timeout:
        print(f"  ⚠  Tiempo de espera agotado para {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ⚠  Error de conexión: {e}")
        return None


def _texto_breve(texto: str, max_chars: int = 200) -> str:
    if len(texto) > max_chars:
        return texto[:max_chars].rstrip() + "…"
    return texto


# ─── Módulo PARES (Portal de Archivos Españoles / AGI Sevilla) ────────────────

_PARES_BASE = "https://pares.mcu.es/ParesBusquedas20/catalogo/search"

_PARES_TERMINOS = [
    "Hopelchén",
    "Hopelchen",
    "Los Chenes",
    "congregación Yucatán 1621",
    "encomienda Chenes",
]

_PARES_PREGUNTAS_RELACIONADAS = ["P001-02", "P002-01"]


def modulo_pares() -> None:
    """Busca documentos en PARES (AGI Sevilla) con términos del repositorio."""
    print("\n🔍  Módulo PARES — Portal de Archivos Españoles")
    print(f"    URL base: {_PARES_BASE}")

    resultados_totales: list[dict] = []

    for termino in _PARES_TERMINOS:
        print(f"  → Buscando: '{termino}'…")
        params = {
            "nm": termino,
            "rows": "10",
            "start": "0",
            "json": "true",
        }
        resp = _get_pagina(_PARES_BASE, params=params)
        if resp is None:
            # Registrar el intento aunque falle
            resultados_totales.append({
                "termino": termino,
                "estado": "error_conexion",
                "url": resp.url if resp else _PARES_BASE,
                "resultados": [],
            })
            continue

        # PARES puede devolver HTML o JSON según el parámetro
        registros: list[dict] = []
        content_type = resp.headers.get("content-type", "")
        if "json" in content_type:
            try:
                data = resp.json()
                # Estructura típica de PARES API
                docs = (
                    data.get("response", {}).get("docs", [])
                    or data.get("results", [])
                    or []
                )
                for doc in docs[:5]:
                    registros.append({
                        "id": doc.get("id", ""),
                        "titulo": doc.get("descripcion", doc.get("title", "")),
                        "fecha": doc.get("fecha", ""),
                        "archivo": doc.get("archivo", ""),
                        "url_documento": f"https://pares.mcu.es/ParesBusquedas20/catalogo/show/{doc.get('id', '')}",
                    })
            except (ValueError, KeyError):
                pass
        else:
            # Parsear HTML si no es JSON
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select(".resultado-item, .item-resultado, li.result")[:5]:
                titulo_el = item.select_one("a, h3, .titulo")
                titulo = titulo_el.get_text(strip=True) if titulo_el else "(sin título)"
                url_el = item.select_one("a[href]")
                url_doc = url_el["href"] if url_el else ""
                registros.append({"titulo": titulo, "url_documento": url_doc})

        n = len(registros)
        print(f"     ✓ {n} resultado(s)")
        resultados_totales.append({
            "termino": termino,
            "estado": "ok",
            "total_resultados": n,
            "url_busqueda": resp.url,
            "resultados": registros,
        })
        time.sleep(1)  # Respetar el servidor

    resultado_final = {
        "modulo": "pares",
        "fecha_consulta": datetime.now().isoformat(),
        "url_base": _PARES_BASE,
        "preguntas_relacionadas": _PARES_PREGUNTAS_RELACIONADAS,
        "terminos_buscados": _PARES_TERMINOS,
        "busquedas": resultados_totales,
        "nota_metodologica": (
            "PARES es el portal de acceso público al Archivo General de Indias (AGI) en Sevilla. "
            "Las búsquedas con 'Hopelchén' y 'Los Chenes' pueden revelar documentos de encomiendas, "
            "visitas pastorales y congregaciones del siglo XVII que confirmen o amplíen la fundación de 1621."
        ),
    }
    guardar_resultados("pares", resultado_final)
    print(f"  ✅  Módulo PARES completado — {len(resultados_totales)} búsquedas realizadas")


# ─── Módulo AGN México ────────────────────────────────────────────────────────

_AGN_BASE = "https://www.agn.gob.mx/buscar/"

_AGN_TERMINOS = [
    "Hopelchén",
    "Los Chenes Yucatán",
    "congregación 1621 Campeche",
    "Ramo Indios Chenes",
]

_AGN_PREGUNTAS_RELACIONADAS = ["P002-01", "P001-02", "P004-01"]


def modulo_agn() -> None:
    """Busca en el catálogo digital del AGN México."""
    print("\n🔍  Módulo AGN México — Archivo General de la Nación")
    print(f"    URL base: {_AGN_BASE}")

    resultados_totales: list[dict] = []

    for termino in _AGN_TERMINOS:
        print(f"  → Buscando: '{termino}'…")
        params = {"q": termino}
        resp = _get_pagina(_AGN_BASE, params=params)
        if resp is None:
            resultados_totales.append({
                "termino": termino,
                "estado": "error_conexion",
                "resultados": [],
            })
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        registros: list[dict] = []

        # El AGN tiene distintos selectores según la versión del portal
        for item in soup.select(".resultado, .search-result, article.result, .item")[:5]:
            titulo_el = item.select_one("h2, h3, a.titulo, .titulo")
            desc_el = item.select_one("p, .descripcion, .abstract")
            link_el = item.select_one("a[href]")
            titulo = titulo_el.get_text(strip=True) if titulo_el else "(sin título)"
            desc = _texto_breve(desc_el.get_text(strip=True)) if desc_el else ""
            href = link_el["href"] if link_el else ""
            if not href.startswith("http") and href:
                href = "https://www.agn.gob.mx" + href
            registros.append({"titulo": titulo, "descripcion": desc, "url": href})

        n = len(registros)
        print(f"     ✓ {n} resultado(s)")
        resultados_totales.append({
            "termino": termino,
            "estado": "ok",
            "total_resultados": n,
            "url_busqueda": resp.url,
            "resultados": registros,
        })
        time.sleep(1)

    resultado_final = {
        "modulo": "agn",
        "fecha_consulta": datetime.now().isoformat(),
        "url_base": _AGN_BASE,
        "preguntas_relacionadas": _AGN_PREGUNTAS_RELACIONADAS,
        "terminos_buscados": _AGN_TERMINOS,
        "busquedas": resultados_totales,
        "nota_metodologica": (
            "El AGN México tiene el Ramo Indios, Congregaciones y Mercedes que pueden contener "
            "documentos sobre la fundación de Hopelchén como pueblo de congregación (1621) y "
            "las dotaciones ejidales del siglo XX."
        ),
    }
    guardar_resultados("agn", resultado_final)
    print(f"  ✅  Módulo AGN completado — {len(resultados_totales)} búsquedas realizadas")


# ─── Módulo SCJN ─────────────────────────────────────────────────────────────

_SCJN_BASE = "https://sjf2.scjn.gob.mx/busqueda-principal-tesis"
_SCJN_AMPARO = "https://www.scjn.gob.mx/pleno/secretaria-general-de-acuerdos/proyectos-de-sentencias-del-pleno"
_SCJN_EXPEDIENTE = "Amparo en Revisión 441/2015"

_SCJN_PREGUNTAS_RELACIONADAS = ["P005-02", "P005-03"]


def modulo_scjn() -> None:
    """Busca la sentencia del Amparo en Revisión 441/2015 (soya transgénica)."""
    print("\n🔍  Módulo SCJN — Suprema Corte de Justicia de la Nación")
    print(f"    Expediente: {_SCJN_EXPEDIENTE}")

    urls_directas = [
        "https://www.scjn.gob.mx/derechos-humanos/sites/default/files/sentencias-emblematicas/sentencia/2020-01/AR-441-2015-191125.pdf",
        "https://sjf2.scjn.gob.mx/busqueda-principal-tesis?q=441%2F2015+soya+transg%C3%A9nica",
    ]

    resultados: list[dict] = []

    for url in urls_directas:
        print(f"  → Probando: {url[:70]}…")
        resp = _get_pagina(url)
        if resp is None:
            resultados.append({"url": url, "estado": "error_conexion"})
            continue

        content_type = resp.headers.get("content-type", "")
        if "pdf" in content_type:
            # Guardar PDF si se obtuvo
            pdf_path = DATOS_INVESTIGACION / f"SCJN_AR441_2015_{HOY}.pdf"
            pdf_path.write_bytes(resp.content)
            resultados.append({
                "url": url,
                "estado": "pdf_descargado",
                "ruta_local": str(pdf_path.relative_to(ROOT)),
                "tamaño_bytes": len(resp.content),
            })
            print(f"     ✓ PDF descargado: {pdf_path.name} ({len(resp.content)//1024} KB)")
        else:
            soup = BeautifulSoup(resp.text, "html.parser")
            texto_pagina = _texto_breve(soup.get_text(separator=" ", strip=True), 500)
            resultados.append({
                "url": url,
                "estado": "html_obtenido",
                "preview_texto": texto_pagina,
            })
            print(f"     ✓ HTML obtenido — {len(resp.text)} caracteres")
        time.sleep(1)

    # También buscar por texto libre en SJF
    print("  → Búsqueda en SJF2 (jurisprudencia)…")
    params = {"q": "soya transgénica mayas Hopelchén", "rows": "5"}
    resp_sjf = _get_pagina(_SCJN_BASE, params=params)
    if resp_sjf:
        soup = BeautifulSoup(resp_sjf.text, "html.parser")
        tesis = []
        for item in soup.select("a.titulo-tesis, .tesis-item, h3 a")[:5]:
            tesis.append({"titulo": item.get_text(strip=True), "url": item.get("href", "")})
        resultados.append({
            "url": resp_sjf.url,
            "estado": "sjf2_buscado",
            "tesis_encontradas": tesis,
        })
        print(f"     ✓ {len(tesis)} tesis encontradas en SJF2")

    resultado_final = {
        "modulo": "scjn",
        "fecha_consulta": datetime.now().isoformat(),
        "expediente": _SCJN_EXPEDIENTE,
        "preguntas_relacionadas": _SCJN_PREGUNTAS_RELACIONADAS,
        "nota": "Buscar la sentencia completa del AR 441/2015: Primera Sala, noviembre 2015. Ministro ponente: Arturo Zaldívar Lelo de Larrea. Tema: consulta previa, libre e informada a comunidades indígenas para siembra de soya transgénica en Campeche.",
        "resultados": resultados,
    }
    guardar_resultados("scjn", resultado_final)
    print(f"  ✅  Módulo SCJN completado")


# ─── Módulo Periódico Oficial de Campeche ─────────────────────────────────────

_POE_BASE = "http://periodicooficial.campeche.gob.mx"

_POE_PREGUNTAS_RELACIONADAS = ["P006-08", "P006-02", "P002-01"]

_POE_PERIODOS_BUSQUEDA = [
    {"descripcion": "Tomas de protesta presidentes municipales Hopelchén 1987-1993", "termino": "Hopelchén 1987"},
    {"descripcion": "Tomas de protesta presidentes municipales Hopelchén 1970-1980", "termino": "Hopelchén presidente municipal"},
    {"descripcion": "Fundación pueblo congregación Chenes siglo XVII", "termino": "congregación Chenes"},
    {"descripcion": "Reforma ejidal Hopelchén 1927-1940", "termino": "ejido Hopelchén dotación"},
]


def modulo_poe_campeche() -> None:
    """Busca en el Periódico Oficial del Estado de Campeche."""
    print("\n🔍  Módulo Periódico Oficial del Estado de Campeche (POE)")
    print(f"    URL base: {_POE_BASE}")

    resultados_totales: list[dict] = []

    for busqueda in _POE_PERIODOS_BUSQUEDA:
        termino = busqueda["termino"]
        descripcion = busqueda["descripcion"]
        print(f"  → Buscando: '{termino}'…")

        resp = _get_pagina(f"{_POE_BASE}/sipoec/public/busqueda", params={"q": termino})
        if resp is None:
            # Intentar con parámetros alternativos
            resp = _get_pagina(_POE_BASE, params={"buscar": termino, "tipo": "texto"})

        if resp is None:
            resultados_totales.append({
                "descripcion": descripcion,
                "termino": termino,
                "estado": "error_conexion",
                "nota": "El POE puede requerir sesión o tiene protección anti-bot. Busca manualmente en http://periodicooficial.campeche.gob.mx",
            })
            print(f"     ⚠  Sin conexión — anota búsqueda manual para: {descripcion}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        registros: list[dict] = []
        for item in soup.select("a[href*='.pdf'], .resultado-periodico, .item-boletin")[:5]:
            titulo = item.get_text(strip=True)[:120]
            href = item.get("href", "")
            if not href.startswith("http") and href:
                href = _POE_BASE + "/" + href.lstrip("/")
            if titulo or href:
                registros.append({"titulo": titulo, "url": href})

        n = len(registros)
        print(f"     ✓ {n} resultado(s)")
        resultados_totales.append({
            "descripcion": descripcion,
            "termino": termino,
            "estado": "ok",
            "total_resultados": n,
            "url_busqueda": resp.url,
            "resultados": registros,
        })
        time.sleep(1.5)

    # Generar solicitud de acceso manual para lo que no se pudo automatizar
    solicitud_manual = _generar_solicitud_poe()

    resultado_final = {
        "modulo": "poe_campeche",
        "fecha_consulta": datetime.now().isoformat(),
        "url_base": _POE_BASE,
        "preguntas_relacionadas": _POE_PREGUNTAS_RELACIONADAS,
        "busquedas": resultados_totales,
        "solicitud_acceso_manual": solicitud_manual,
        "nota_metodologica": (
            "El Periódico Oficial del Estado de Campeche tiene archivo digital desde 1857. "
            "Las tomas de protesta de presidentes municipales se publican en el POE. "
            "Buscar específicamente: 'Hopelchén' + años 1984-1993 para desbloquear P006-08."
        ),
    }
    guardar_resultados("poe_campeche", resultado_final)
    print(f"  ✅  Módulo POE Campeche completado")


def _generar_solicitud_poe() -> str:
    return """SOLICITUD DE INFORMACIÓN — Periódico Oficial del Estado de Campeche

Dirigida a: Dirección del Periódico Oficial del Estado de Campeche
Correo de contacto: (buscar en periodicooficial.campeche.gob.mx/contacto)
Plataforma INFOMEX Campeche: https://www.infomex.campeche.gob.mx

DATOS DEL SOLICITANTE:
Nombre: [Daniela Naraai Caamal Ake]
Proyecto: Investigación histórica independiente — Hopelchén: 2000 años de historia

SOLICITUD:
Por medio de la presente, solicito respetuosamente se me proporcione:

1. Copias de los ejemplares del Periódico Oficial del Estado de Campeche
   que contengan la toma de protesta del Presidente Municipal de Hopelchén
   correspondiente a los períodos de gobierno 1984-1987, 1987-1990, 1990-1993
   y 1993-1996.

2. En su caso, los nombres completos de los presidentes municipales de
   Hopelchén que tomaron protesta en los años 1984, 1987, 1990 y 1993.

3. Copias de cualquier decreto o acuerdo publicado en el POE que haga
   referencia a cambios de uso de suelo en el municipio de Hopelchén,
   Campeche, entre los años 1987 y 1995.

FUNDAMENTO LEGAL:
Ley Federal de Transparencia y Acceso a la Información Pública Gubernamental
Artículo 4o. — Todo ciudadano tiene derecho a solicitar y recibir información
de cualquier autoridad, entidad, órgano y organismo de los Poderes Ejecutivo,
Legislativo y Judicial.

[Ciudad y fecha]
[Firma]
"""


# ─── Módulo FamilySearch (guía de búsqueda) ───────────────────────────────────

_FAMILYSEARCH_PREGUNTAS_RELACIONADAS = ["P001-01", "P002-02", "P003-01"]


def modulo_familysearch(solo_guia: bool = False) -> None:
    """
    Genera guía de búsqueda en FamilySearch para registros coloniales de Los Chenes.
    FamilySearch requiere cuenta gratuita; este módulo genera la guía de búsqueda
    y realiza búsquedas básicas sin autenticación donde sea posible.
    """
    print("\n🔍  Módulo FamilySearch — Registros de Bautismos, Matrimonios y Defunciones")

    guia = {
        "modulo": "familysearch",
        "fecha_generacion": datetime.now().isoformat(),
        "preguntas_relacionadas": _FAMILYSEARCH_PREGUNTAS_RELACIONADAS,
        "instrucciones": [
            "1. Ir a https://www.familysearch.org/es/ y crear cuenta gratuita",
            "2. En 'Buscar Registros' > 'Catálogo de Biblioteca' buscar: 'Campeche' o 'Hopelchén'",
            "3. En 'Buscar Personas' usar los campos: Apellido + Lugar de nacimiento = 'Hopelchén, Campeche, México'",
            "4. Colecciones de mayor interés para este proyecto:",
        ],
        "colecciones_prioritarias": [
            {
                "id_coleccion": "FX020",
                "nombre": "México, Registros Parroquiales y Diocesanos, 1514-1970 (Obispado de Campeche/Yucatán)",
                "descripcion": "Bautismos, matrimonios y defunciones de la diócesis de Campeche. Incluye registros de parroquias de Los Chenes.",
                "terminos_busqueda_sugeridos": [
                    "Apellido: Lara — Lugar: Hopelchén",
                    "Apellido: Baranda — Lugar: Campeche",
                    "Apellido: May — Lugar: Los Chenes",
                    "Apellido: Cauich — Lugar: Hopelchén",
                ]
            },
            {
                "id_coleccion": "FX025",
                "nombre": "México, Yucatán, Registros Parroquiales, 1750-1930 (Mérida)",
                "descripcion": "Parroquias de la Diócesis de Yucatán, que incluyó a Los Chenes antes de la creación del Obispado de Campeche (1895).",
                "terminos_busqueda_sugeridos": [
                    "Apellido: Lara — Evento: Bautismo — Lugar: Hopelchén",
                    "Apellido: Baranda — Lugar: Campeche, Yucatán",
                ]
            },
            {
                "id_coleccion": "FX030",
                "nombre": "México, Campeche, Registro Civil, 1861-2000",
                "descripcion": "Registros civiles del estado de Campeche desde la Ley del Registro Civil (1859).",
                "terminos_busqueda_sugeridos": [
                    "Apellido: Lara — Municipio: Hopelchén — Año: 1870-1920",
                    "Apellido: Aranda — Municipio: Hopelchén",
                ]
            }
        ],
        "apellidos_prioritarios_para_rastrear": [
            {"apellido": "LARA", "objetivo": "Conectar Pedro Advíncula Lara (hacendado porfiriano) con Emilio Lara Calderón (alcalde 2021-2024). P006-07."},
            {"apellido": "BARANDA/ARANDA", "objetivo": "Confirmar o descartar linaje Baranda-Aranda en poder de Campeche. P006-01."},
            {"apellido": "MAY", "objetivo": "Juan de Dios May (1848) — ¿tiene descendientes en Los Chenes? P009-02."},
            {"apellido": "CAUICH", "objetivo": "Sandy Baas Cauich — apellidos mayas en el poder político de Hopelchén. P006-08."},
            {"apellido": "SANSORES", "objetivo": "Parentesco Julio Sansores (alcalde) / Layda Sansores (gobernadora). P006-09."},
        ],
        "nota_acceso": (
            "FamilySearch es gratuito. La mayoría de registros coloniales de Campeche y Yucatán "
            "están digitalizados y son accesibles en línea. Los registros parroquiales del siglo XVII-XVIII "
            "(que contienen los bataboob de 1669 y las primeras generaciones post-conquista) están en "
            "la colección FX020 — algunos pueden necesitar lectura de imágenes en lugar de búsqueda por nombre."
        ),
    }

    # Intentar algunas búsquedas públicas sin autenticación
    if not solo_guia and _REQUESTS_OK:
        print("  → Intentando búsquedas básicas sin autenticación…")
        urls_publicas = [
            "https://www.familysearch.org/search/record/results?q.givenName=&q.surname=Lara&q.birthPlace=Hopelch%C3%A9n%2C+Campeche%2C+Mexico&count=5",
        ]
        busquedas_web: list[dict] = []
        for url in urls_publicas:
            resp = _get_pagina(url)
            if resp:
                soup = BeautifulSoup(resp.text, "html.parser")
                resultados_el = soup.select(".name-person, .result-name, .person-link")[:5]
                nombres = [el.get_text(strip=True) for el in resultados_el]
                busquedas_web.append({
                    "url": url,
                    "estado": "ok_parcial" if nombres else "requiere_autenticacion",
                    "nombres_encontrados": nombres,
                    "nota": "FamilySearch requiere cuenta para búsquedas completas.",
                })
                print(f"     ✓ {len(nombres)} resultado(s) sin autenticación")
            time.sleep(1)
        guia["busquedas_realizadas"] = busquedas_web

    ruta = guardar_resultados("familysearch", guia)
    print(f"  ✅  Módulo FamilySearch: guía guardada en {ruta.name}")


# ─── Punto de entrada ─────────────────────────────────────────────────────────

_MODULOS = {
    "pares": modulo_pares,
    "agn": modulo_agn,
    "scjn": modulo_scjn,
    "poe_campeche": modulo_poe_campeche,
    "familysearch": modulo_familysearch,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rastrea fuentes digitales públicas para el proyecto Hopelchén.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--modulo", "-m",
        choices=list(_MODULOS.keys()),
        metavar="MÓDULO",
        help=f"Módulo a ejecutar: {', '.join(_MODULOS.keys())}",
    )
    parser.add_argument(
        "--guia",
        action="store_true",
        help="Solo generar guía de búsqueda (sin peticiones HTTP; aplica a familysearch)",
    )
    args = parser.parse_args()

    # Verificar dependencias de requests/bs4 solo cuando se usan módulos que las necesitan.
    # El módulo 'familysearch --guia' no hace peticiones HTTP.
    if not (args.modulo == "familysearch" and args.guia):
        _verificar_dependencias()

    print(f"\n{'=' * 65}")
    print("   RASTREADOR DE FUENTES — Hopelchén: 2000 años de historia")
    print(f"{'=' * 65}")
    print(f"📁 Resultados en: {DATOS_INVESTIGACION.relative_to(ROOT)}\n")

    if args.modulo:
        func = _MODULOS[args.modulo]
        if args.modulo == "familysearch":
            modulo_familysearch(solo_guia=args.guia)
        else:
            func()
    else:
        # Ejecutar todos los módulos
        for nombre, func in _MODULOS.items():
            if nombre == "familysearch":
                modulo_familysearch(solo_guia=True)
            else:
                func()
            print()

    print(f"\n{'=' * 65}")
    print(f"  ✅  Rastreo completado — ver {DATOS_INVESTIGACION.relative_to(ROOT)}/")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
