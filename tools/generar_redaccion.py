#!/usr/bin/env python3
"""
generar_redaccion.py
====================
Genera los archivos de redacción anotada para la investigación histórica de
Hopelchén / Los Chenes a partir de los datos en datos/.

Uso:
    python tools/generar_redaccion.py

Salida (idempotente — sobrescribe si ya existen):
    fuentes/catalogo_fuentes.md       Chicago + IDs F001…
    trabajo/periodos/<slug>.md        Un archivo por nodo/período
    trabajo/indice.md                 Índice de períodos
    mapa/personajes.md                Ficha de personajes con fuentes

El script es idempotente: puede ejecutarse múltiples veces sin duplicar
contenido. Modifica únicamente las carpetas trabajo/, fuentes/ y mapa/.
No modifica datos/ ni ningún otro archivo.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

# ─── Rutas base ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "datos"
DATOS_CURATED = DATOS / "curated"
DATOS_HOPELCHEN = DATOS / "hopelchen"
FUENTES_DIR = ROOT / "fuentes"
TRABAJO_DIR = ROOT / "trabajo" / "periodos"
INDICE_PATH = ROOT / "trabajo" / "indice.md"
MAPA_DIR = ROOT / "mapa"


# ─── Utilidades ─────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def slug(text: str) -> str:
    """Convierte texto a slug seguro para nombres de archivo."""
    text = text.lower()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = re.sub(r"ñ", "n", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {path.relative_to(ROOT)}")


def wrap(text: str, width: int = 90, indent: str = "") -> str:
    return textwrap.fill(text, width=width, subsequent_indent=indent)


# ─── Chicago citation builder ────────────────────────────────────────────────

def chicago_book(author: str, title: str, city: str = "", publisher: str = "",
                 year: str = "", edition: str = "", isbn: str = "",
                 url: str = "", paginas: str = "") -> str:
    parts = []
    if author:
        parts.append(author + ".")
    if title:
        parts.append(f"*{title}*.")
    pub_parts = [p for p in [city, publisher] if p]
    if pub_parts:
        pub_str = ": ".join(pub_parts) if len(pub_parts) == 2 else pub_parts[0]
        parts.append(pub_str + ("," if year else "."))
    if year:
        parts.append(year + ".")
    if edition:
        parts.append(edition + ".")
    if isbn:
        parts.append(f"ISBN {isbn}.")
    if url:
        parts.append(f"<{url}>.")
    return " ".join(parts)


def chicago_article(author: str, title: str, journal: str = "",
                    volume: str = "", issue: str = "", year: str = "",
                    pages: str = "", doi: str = "", url: str = "") -> str:
    parts = []
    if author:
        parts.append(author + ".")
    if title:
        parts.append(f'"{title}."')
    if journal:
        j = f"*{journal}*"
        if volume:
            j += f" {volume}"
            if issue:
                j += f", no. {issue}"
        if year:
            j += f" ({year})"
        if pages:
            j += f": {pages}"
        parts.append(j + ".")
    if doi:
        parts.append(f"<https://doi.org/{doi}>.")
    elif url:
        parts.append(f"<{url}>.")
    return " ".join(parts)


def chicago_web(author: str, title: str, site: str = "", date: str = "",
                url: str = "", consulta: str = "") -> str:
    parts = []
    if author:
        parts.append(author + ".")
    if title:
        parts.append(f'"{title}."')
    if site:
        parts.append(f"*{site}*.")
    if date:
        parts.append(date + ".")
    if url:
        parts.append(f"<{url}>.")
    if consulta:
        parts.append(f"Consultado el {consulta}.")
    return " ".join(parts)


def chicago_archive(institution: str, description: str, collection: str = "",
                    expediente: str = "", year: str = "") -> str:
    parts = []
    if institution:
        parts.append(institution + ".")
    if description:
        parts.append(f'"{description}."')
    if collection:
        parts.append(collection + ".")
    if expediente:
        parts.append(expediente + ".")
    if year:
        parts.append(year + ".")
    return " ".join(parts)


def build_chicago(source: dict) -> str:
    """Construye la cita Chicago a partir de un diccionario de fuente."""
    tipo = source.get("tipo", "")
    author = source.get("autor", source.get("autores", ""))
    if isinstance(author, list):
        author = ", ".join(author)

    title = (source.get("titulo") or source.get("titulo_original") or
             source.get("titulo_en_espanol") or source.get("nombre") or
             source.get("descripcion", ""))

    year = str(source.get("año", source.get("año_original", source.get("fecha", ""))))

    if tipo in ("articulo_academico", "articulo_cientifico", "articulo_critico"):
        journal = (source.get("publicacion") or source.get("revista") or
                   source.get("journal", ""))
        doi = source.get("DOI", "")
        url = source.get("url", source.get("URL", ""))
        return chicago_article(author=author, title=title, journal=journal,
                                year=year, doi=doi, url=url)
    elif tipo in ("archivo_primario", "fondo_archivistico"):
        institution = source.get("institucion", author)
        collection = source.get("fondo", source.get("collection", ""))
        expediente = source.get("expediente", "")
        return chicago_archive(institution=institution, description=title,
                                collection=collection, expediente=expediente,
                                year=year)
    elif tipo in ("fuente_web", "web") or source.get("URL") or source.get("url"):
        url = source.get("URL", source.get("url", ""))
        site = source.get("sitio", source.get("nombre", ""))
        consulta = source.get("fecha_consulta", "")
        display_title = title if title else site
        return chicago_web(author=author, title=display_title, site=site,
                           date=year, url=url, consulta=consulta)
    else:
        # libro / tesis / default
        city = source.get("ciudad", source.get("city", ""))
        publisher = source.get("editorial", source.get("publisher", ""))
        isbn = source.get("ISBN", source.get("isbn", ""))
        url = source.get("url", source.get("URL", ""))
        reedicion = source.get("reedicion", "")
        full_year = reedicion if reedicion else year
        return chicago_book(author=author, title=title, city=city,
                             publisher=publisher, year=full_year, isbn=isbn,
                             url=url)


# ─── Catálogo de fuentes ─────────────────────────────────────────────────────

CATALOG_HEADER = """\
# Catálogo de Fuentes — Investigación Histórica de Hopelchén

> Proyecto: *Archivo Vivo — Hopelchén, Campeche*  
> Autora: Daniela Naraai Caamal Ake  
> Generado por: `tools/generar_redaccion.py`

**Convención de cita interna:**  
Dentro de los archivos de `trabajo/` y `mapa/` se usan IDs tipo `[F001]`.
Cada ID enlaza a la entrada de este catálogo.

---

"""


def make_catalog_entry(fid: str, source: dict, origin_file: str) -> str:
    tipo = source.get("tipo", "desconocido")
    author = source.get("autor", source.get("autores", "—"))
    if isinstance(author, list):
        author = ", ".join(author)
    title = (source.get("titulo") or source.get("titulo_original") or
             source.get("nombre") or source.get("descripcion") or "Sin título")
    year = str(source.get("año", source.get("año_original", source.get("fecha", "s.f."))))
    url = source.get("url", source.get("URL", ""))
    archivo_local = source.get("archivo_local", "")
    confiabilidad = source.get("confiabilidad", "")
    datos_clave = source.get("datos_clave_extraidos", source.get("datos_clave", []))
    nota = source.get("nota", "")
    chicago = build_chicago(source)

    lines = [f"## {fid} — {title[:70]}"]
    lines.append("")
    lines.append(f"| Campo | Valor |")
    lines.append(f"|---|---|")
    lines.append(f"| **Tipo** | {tipo} |")
    lines.append(f"| **Autor** | {author} |")
    lines.append(f"| **Año** | {year} |")
    if confiabilidad:
        lines.append(f"| **Confiabilidad** | {confiabilidad} |")
    if url:
        lines.append(f"| **URL** | <{url}> |")
    if archivo_local:
        lines.append(f"| **Archivo local** | `{archivo_local}` |")
    lines.append(f"| **Origen (repo)** | `datos/{origin_file}` |")
    lines.append("")
    lines.append(f"**Cita Chicago:** {chicago}")
    lines.append("")
    if datos_clave:
        lines.append("**Datos clave extraídos:**")
        for dk in datos_clave[:6]:
            lines.append(f"- {dk}")
        lines.append("")
    if nota:
        lines.append(f"**Nota:** {nota}")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def generate_catalog() -> dict[str, str]:
    """
    Lee datos/curated/03_fuentes_bibliograficas.json y devuelve
    un dict {id: chicago_citation} además de escribir el catálogo.
    """
    src_path = DATOS_CURATED / "03_fuentes_bibliograficas.json"
    if not src_path.exists():
        print("  ⚠  No se encontró 03_fuentes_bibliograficas.json")
        return {}

    data = load_json(src_path)
    meta = data.get("META", {})

    id_map: dict[str, dict] = {}  # fid -> source dict
    origin = "curated/03_fuentes_bibliograficas.json"

    def collect(section: Any, section_name: str) -> None:
        if isinstance(section, dict):
            for v in section.values():
                if isinstance(v, dict) and v.get("id"):
                    id_map[v["id"]] = (v, origin)
                elif isinstance(v, list):
                    collect(v, section_name)
        elif isinstance(section, list):
            for v in section:
                if isinstance(v, dict) and v.get("id"):
                    id_map[v["id"]] = (v, origin)

    for key, val in data.items():
        if key == "META":
            continue
        collect(val, key)

    # Also collect sources without explicit id by assigning sequential IDs
    # (from libros_academicos that have no id field yet)
    seq = 1
    for key, val in data.items():
        if key in ("META",):
            continue
        if isinstance(val, dict):
            for v in val.values():
                if isinstance(v, dict) and not v.get("id"):
                    while f"FX{seq:03d}" in id_map:
                        seq += 1
                    v["id"] = f"FX{seq:03d}"
                    id_map[v["id"]] = (v, origin)
                    seq += 1
        elif isinstance(val, list):
            for v in val:
                if isinstance(v, dict) and not v.get("id"):
                    while f"FX{seq:03d}" in id_map:
                        seq += 1
                    v["id"] = f"FX{seq:03d}"
                    id_map[v["id"]] = (v, origin)
                    seq += 1

    # Sort by id
    def sort_key(fid: str) -> tuple:
        m = re.match(r"([A-Z]+)(\d+)", fid)
        if m:
            return (m.group(1), int(m.group(2)))
        return (fid, 0)

    sorted_ids = sorted(id_map.keys(), key=sort_key)

    lines = [CATALOG_HEADER]
    lines.append(f"**Total de fuentes:** {len(sorted_ids)}\n\n")

    # Quick index
    lines.append("## Índice rápido\n")
    for fid in sorted_ids:
        src, orig = id_map[fid]
        title = (src.get("titulo") or src.get("titulo_original") or
                 src.get("nombre") or src.get("descripcion") or "Sin título")[:55]
        author = src.get("autor", src.get("autores", ""))
        if isinstance(author, list):
            author = author[0] if author else ""
        # get last name
        last = author.split(",")[0].split()[-1] if author else "—"
        year = str(src.get("año", src.get("año_original", "")))[:4]
        lines.append(f"- [{fid}](#{fid.lower()}) — {last} ({year or 's.f.'}) — {title}")
    lines.append("\n---\n\n")

    for fid in sorted_ids:
        src, orig = id_map[fid]
        lines.append(make_catalog_entry(fid, src, orig))

    write_file(FUENTES_DIR / "catalogo_fuentes.md", "".join(lines))

    # Return id -> chicago citation string
    return {fid: build_chicago(id_map[fid][0]) for fid in sorted_ids}


# ─── Redacción anotada por período ──────────────────────────────────────────

PERIOD_HEADER = """\
# {titulo}

> **Nodo:** {nodo_id} · **Era:** {era}  
> **Período:** {rango_temporal}  
> **Hipótesis marco:** {hipotesis}  
> **Archivo origen:** `datos/hopelchen/{filename}`  
> **Generado por:** `tools/generar_redaccion.py`

---

"""

BLOCK_TEMPLATE = """\
### Bloque {bid} — {subtitulo}

| Campo | Valor |
|---|---|
| **Tipo** | {tipo} |
| **Fecha / Período** | {fecha} |
| **Lugar** | {lugar} |
| **Personajes** | {personajes} |
| **Cargos** | {cargos} |
| **Fuente(s)** | {fuentes_str} |
| **Origen** | `datos/hopelchen/{filename}` |

{cita}
{notas}
---

"""


def format_personajes(personajes: Any) -> str:
    if not personajes:
        return "—"
    if isinstance(personajes, list):
        items = []
        for p in personajes:
            if isinstance(p, dict):
                nombre = p.get("nombre", p.get("name", str(p)))
                cargo = p.get("cargo", p.get("rol", ""))
                items.append(f"{nombre} ({cargo})" if cargo else nombre)
            else:
                items.append(str(p))
        return "; ".join(items) if items else "—"
    return str(personajes)


def format_cargos(personajes: Any) -> str:
    if not personajes:
        return "—"
    if isinstance(personajes, list):
        cargos = []
        for p in personajes:
            if isinstance(p, dict):
                cargo = p.get("cargo", p.get("rol", ""))
                if cargo:
                    cargos.append(cargo)
        return "; ".join(cargos) if cargos else "—"
    return "—"


def format_fuentes(fuente: Any, fuente2: Any, fuente3: Any) -> str:
    parts = []
    for f in [fuente, fuente2, fuente3]:
        if not f or not isinstance(f, dict):
            continue
        nombre = (f.get("nombre") or f.get("name") or f.get("autor") or
                  f.get("journal") or "")
        url = f.get("url", f.get("URL", ""))
        if url:
            parts.append(f"[{nombre}](<{url}>)" if nombre else f"<{url}>")
        elif nombre:
            parts.append(nombre)
    return "; ".join(parts) if parts else "—"


def build_cita(registro: dict) -> str:
    desc = registro.get("descripcion", "")
    if not desc:
        return ""
    fuente = registro.get("fuente", {})
    fuente_nombre = ""
    fuente_url = ""
    if isinstance(fuente, dict):
        fuente_nombre = (fuente.get("nombre") or fuente.get("autor") or "")
        fuente_url = fuente.get("url", fuente.get("URL", ""))
    elif isinstance(fuente, str):
        fuente_nombre = fuente

    lines = [f"> {desc}"]
    lines.append("")
    if fuente_nombre or fuente_url:
        ref = fuente_nombre
        if fuente_url:
            ref += f" <{fuente_url}>"
        lines.append(f"_Origen: {ref.strip()}_")
    return "\n".join(lines)


def build_notas(registro: dict) -> str:
    notas = registro.get("notas_contradiccion", "")
    conexion = registro.get("conexion_hipotesis", "")
    tags = registro.get("tags", [])
    lines = []
    if notas:
        lines.append(f"**⚠ Nota/contradicción:** {notas[:300]}")
    if conexion:
        lines.append(f"**→ Conexión hipótesis:** {conexion[:200]}")
    if tags:
        lines.append(f"**Etiquetas:** {', '.join(tags)}")
    return "\n".join(lines) + "\n" if lines else ""


def process_nodo(nodo_path: Path) -> tuple[str, str]:
    """Procesa un HOPELCHEN_NODO_*.json y devuelve (slug, md_content)."""
    data = load_json(nodo_path)
    nodo_id = data.get("nodo_id", "")
    titulo = data.get("titulo", nodo_path.stem)
    era = data.get("era", "")
    rango = data.get("rango_temporal", "")
    hipotesis = data.get("hipotesis_marco", "")
    filename = nodo_path.name

    header = PERIOD_HEADER.format(
        titulo=titulo,
        nodo_id=nodo_id,
        era=era,
        rango_temporal=rango,
        hipotesis=hipotesis[:200] if hipotesis else "—",
        filename=filename,
    )

    registros = data.get("registros", [])
    blocks = []
    for reg in registros:
        bid = reg.get("registro_id", "?")
        subtitulo = reg.get("subtitulo", reg.get("descripcion", "")[:60])
        tipo = reg.get("tipo_dato", "contexto")
        fecha = reg.get("fecha_evento", "—")
        lugar = reg.get("lugar", "—")
        personajes_raw = reg.get("personajes", [])
        personajes_str = format_personajes(personajes_raw)
        cargos_str = format_cargos(personajes_raw)
        fuente1 = reg.get("fuente", {})
        fuente2 = reg.get("fuente_secundaria", {})
        fuente3 = reg.get("fuente_academica", {})
        fuentes_str = format_fuentes(fuente1, fuente2, fuente3)
        cita = build_cita(reg)
        notas = build_notas(reg)

        block = BLOCK_TEMPLATE.format(
            bid=bid,
            subtitulo=subtitulo[:70],
            tipo=tipo,
            fecha=fecha,
            lugar=lugar,
            personajes=personajes_str,
            cargos=cargos_str,
            fuentes_str=fuentes_str,
            filename=filename,
            cita=cita,
            notas=notas,
        )
        blocks.append(block)

    # Fuentes pendientes section
    pendientes = data.get("fuentes_pendientes_consultar", [])
    pend_section = ""
    if pendientes:
        pend_lines = ["## Fuentes pendientes de consulta\n"]
        for p in pendientes:
            if isinstance(p, dict):
                nombre = p.get("nombre", p.get("institucion", str(p)))
                pend_lines.append(f"- {nombre}")
            else:
                pend_lines.append(f"- {p}")
        pend_section = "\n".join(pend_lines) + "\n"

    content = header + "\n".join(blocks) + pend_section
    file_slug = f"nodo-{nodo_id}-{slug(titulo[:40])}"
    return file_slug, content


def generate_periods() -> list[tuple[str, str, str, str]]:
    """
    Procesa todos los HOPELCHEN_NODO_*.json.
    Devuelve lista de (file_slug, titulo, rango_temporal, filename).
    """
    nodo_files = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))
    # Deduplicate NODO_006 — prefer PoderPolitico_Local (more complete)
    seen_ids: set[str] = set()
    filtered = []
    for nf in nodo_files:
        data = load_json(nf)
        nid = data.get("nodo_id", nf.stem)
        if nid in seen_ids:
            continue
        seen_ids.add(nid)
        filtered.append(nf)

    index_entries = []
    for nf in filtered:
        data = load_json(nf)
        file_slug, content = process_nodo(nf)
        titulo = data.get("titulo", nf.stem)
        rango = data.get("rango_temporal", "")
        write_file(TRABAJO_DIR / f"{file_slug}.md", content)
        index_entries.append((file_slug, titulo, rango, nf.name))

    return index_entries


# ─── Personajes ──────────────────────────────────────────────────────────────

PERSONAJES_HEADER = """\
# Mapa de Personajes — Investigación Histórica de Hopelchén

> Fuente principal: `datos/curated/01_personajes.json`  
> Generado por: `tools/generar_redaccion.py`

**Cómo leer este archivo:**  
Cada sección es un personaje o linaje familiar. Los campos incluyen
evidencia documental con IDs de fuente que remiten a
`fuentes/catalogo_fuentes.md`.

---

"""


def _fmt_list(items: Any) -> str:
    if not items:
        return "—"
    if isinstance(items, list):
        return "; ".join(str(x) for x in items if x) or "—"
    return str(items)


def generate_personajes() -> None:
    src_path = DATOS_CURATED / "01_personajes.json"
    if not src_path.exists():
        return

    data = load_json(src_path)
    sections = []

    # Linajes familiares
    linajes = data.get("linajes_familiares", {})
    if linajes:
        sections.append("## Linajes Familiares\n")
        for lid, linaje in linajes.items():
            nombre = lid.replace("FAM", "Familia ").replace("_", " ")
            tipo = linaje.get("tipo", "")
            periodo = linaje.get("periodo", "")
            fuente = linaje.get("fuente_primaria", "—")
            sections.append(f"### {nombre}\n")
            sections.append(f"| Campo | Valor |\n|---|---|\n")
            sections.append(f"| **Tipo** | {tipo} |\n")
            sections.append(f"| **Período** | {periodo} |\n")
            sections.append(f"| **Fuente** | {fuente} |\n")
            sections.append(f"| **Origen** | `datos/curated/01_personajes.json` |\n\n")

            linea = linaje.get("linea_cronologica", [])
            if linea:
                sections.append("**Línea cronológica:**\n\n")
                sections.append("| Año | Nombre | Cargo |\n|---|---|---|\n")
                for item in linea:
                    anio = str(item.get("año", "—"))
                    nombre_p = item.get("nombre", "—")
                    cargo = item.get("cargo", "—")
                    sections.append(f"| {anio} | {nombre_p} | {cargo} |\n")
                sections.append("\n")
            nota = linaje.get("nota", "")
            if nota:
                sections.append(f"> {nota}\n\n")
            sections.append("---\n\n")

    # Personajes individuales (dict keyed by P001, P002, ...)
    personajes_raw = data.get("personajes", {})
    if isinstance(personajes_raw, list):
        personajes_items = [(p.get("id", f"P{i:03d}"), p)
                            for i, p in enumerate(personajes_raw)]
    elif isinstance(personajes_raw, dict):
        personajes_items = list(personajes_raw.items())
    else:
        personajes_items = []

    if personajes_items:
        sections.append("## Personajes Individuales\n\n")
        for pid, p in personajes_items:
            nombre = p.get("nombre", "Sin nombre")
            roles = p.get("roles", [])
            rol = "; ".join(roles[:2]) if roles else p.get("rol_historico", p.get("rol", ""))
            periodo = p.get("periodo", "")
            lugar = p.get("origen", p.get("lugar_principal", p.get("lugar", "")))
            fuentes = p.get("fuentes", p.get("fuentes_verificadas", []))
            fuentes_str = _fmt_list(fuentes)
            conexiones = _fmt_list(p.get("conexiones", []))
            descripcion = p.get("descripcion", p.get("notas", ""))
            hechos = p.get("hechos_verificados", [])

            sections.append(f"### {pid} — {nombre}\n\n")
            sections.append(f"| Campo | Valor |\n|---|---|\n")
            sections.append(f"| **Rol** | {rol} |\n")
            sections.append(f"| **Período** | {periodo} |\n")
            sections.append(f"| **Lugar** | {lugar} |\n")
            sections.append(f"| **Fuente(s)** | {fuentes_str} |\n")
            sections.append(f"| **Conexiones** | {conexiones} |\n")
            sections.append(f"| **Origen** | `datos/curated/01_personajes.json` |\n\n")
            if descripcion:
                sections.append(f"> {descripcion[:400]}\n\n")
            if hechos:
                sections.append("**Hechos verificados:**\n\n")
                for h in hechos[:5]:
                    sections.append(f"- {h}\n")
                sections.append("\n")
            sections.append("---\n\n")

    write_file(MAPA_DIR / "personajes.md",
               PERSONAJES_HEADER + "".join(sections))


# ─── Índice ───────────────────────────────────────────────────────────────────

INDICE_HEADER = """\
# Índice de Redacción Anotada — Hopelchén: 2000 años de historia

> Autora: Daniela Naraai Caamal Ake  
> Generado por: `tools/generar_redaccion.py`

Los archivos en `trabajo/periodos/` contienen la información extraída de los
datos fuente en bloques con **metadatos explícitos** (tipo, fecha, lugar,
personajes, cargos, fuentes rastreables).

Para agregar nueva información:
1. Edita el JSON en `datos/hopelchen/` o agrega un nuevo `HOPELCHEN_NODO_*.json`.
2. Ejecuta: `python tools/generar_redaccion.py`
3. El archivo de período correspondiente se regenera.

---

## Fuentes

| Archivo | Descripción |
|---|---|
| [`fuentes/catalogo_fuentes.md`](../fuentes/catalogo_fuentes.md) | Catálogo Chicago completo con IDs F### |

---

## Períodos históricos

"""

INDICE_ENTRY = "| [{titulo_corto}]({link}) | {rango} | `datos/hopelchen/{filename}` |\n"


def generate_indice(entries: list[tuple[str, str, str, str]]) -> None:
    lines = [INDICE_HEADER]
    lines.append("| Archivo | Período | Fuente JSON |\n")
    lines.append("|---|---|---|\n")
    for file_slug, titulo, rango, filename in entries:
        titulo_corto = titulo[:60]
        link = f"periodos/{file_slug}.md"
        lines.append(INDICE_ENTRY.format(
            titulo_corto=titulo_corto,
            link=link,
            rango=rango,
            filename=filename,
        ))
    lines.append("\n---\n\n")
    lines.append("## Mapa de conexiones\n\n")
    lines.append("| Archivo | Descripción |\n|---|---|\n")
    lines.append("| [`mapa/personajes.md`](../mapa/personajes.md) | "
                 "Personajes históricos con fuentes rastreables |\n")
    lines.append("\n---\n\n")
    lines.append("## Agregar excerpts manualmente\n\n")
    lines.append("Para agregar un bloque en un período existente, copia la plantilla:\n\n")
    lines.append("```markdown\n")
    lines.append("### Bloque XX — Título del bloque\n\n")
    lines.append("| Campo | Valor |\n|---|---|\n")
    lines.append("| **Tipo** | evento / personaje / contexto / hilo |\n")
    lines.append("| **Fecha / Período** | YYYY o rango |\n")
    lines.append("| **Lugar** | Hopelchén, Campeche |\n")
    lines.append("| **Personajes** | Nombre (Cargo) |\n")
    lines.append("| **Cargos** | — |\n")
    lines.append("| **Fuente(s)** | [F001](../fuentes/catalogo_fuentes.md#f001) |\n")
    lines.append("| **Origen** | `datos/archivo.json` |\n\n")
    lines.append("> \"Cita textual o paráfrasis directa del texto fuente.\"\n\n")
    lines.append("_Origen: Autor, Título. Ciudad: Editorial, Año._\n\n")
    lines.append("---\n```\n")

    write_file(INDICE_PATH, "".join(lines))


# ─── .gitkeep para carpetas vacías ──────────────────────────────────────────

def ensure_gitkeep(directory: Path) -> None:
    gitkeep = directory / ".gitkeep"
    if not any(directory.iterdir()) or (
        list(directory.iterdir()) == [gitkeep]
    ):
        gitkeep.touch()


# ─── Validación de IDs de fuentes (F###) en nodos ────────────────────────────

def validate_source_ids(chicago_map: dict[str, str]) -> list[str]:
    """
    Verifica que los IDs de fuente mencionados como texto ``F###`` o ``FX###``
    dentro de los registros de los nodos existen en el catálogo cargado.

    Args:
        chicago_map: Diccionario {id: chicago_citation_string} devuelto por
                     :func:`generate_catalog`.

    Returns:
        list[str]: Lista de advertencias (vacía si todo está bien).
    """
    import re as _re
    patron = _re.compile(r'\bF(?:X)?[0-9]{1,4}\b', _re.IGNORECASE)
    ids_catalogo = {k.upper() for k in chicago_map}
    advertencias: list[str] = []

    for nodo_path in sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json")):
        try:
            data = load_json(nodo_path)
        except (OSError, json.JSONDecodeError):
            continue
        texto_nodo = json.dumps(data, ensure_ascii=False)
        ids_en_nodo = {m.upper() for m in patron.findall(texto_nodo)}
        # Sólo reportar los que parecen ser referencias intencionadas a fuentes
        # (presentes como valor standalone, ej. "F001", no como substrings de URLs)
        for fid in sorted(ids_en_nodo):
            if fid not in ids_catalogo:
                advertencias.append(
                    f"{nodo_path.name}: referencia a '{fid}' no encontrada en el catálogo"
                )
    return advertencias


# ─── Mapa de citas cruzadas ───────────────────────────────────────────────────

MAPA_CITAS_HEADER = """\
# Mapa de Citas — Índice Cruzado de Fuentes

> Generado por: `tools/generar_redaccion.py`  
> Muestra qué fuentes (F###) aparecen en cada archivo de `trabajo/` y `mapa/`.

---

"""


def generate_mapa_citas(chicago_map: dict[str, str]) -> None:
    """
    Genera ``fuentes/mapa_citas.md`` con un índice cruzado: para cada F### del
    catálogo lista los archivos de trabajo/ y mapa/ que lo citan.

    Args:
        chicago_map: Diccionario {id: chicago_citation_string} devuelto por
                     :func:`generate_catalog`.
    """
    import re as _re
    patron = _re.compile(r'\bF(?:X)?[0-9]{1,4}\b', _re.IGNORECASE)

    # {fid_upper: set of relative paths}
    citas: dict[str, set[str]] = {}

    directorios_buscar = [ROOT / "trabajo", ROOT / "mapa"]
    for directorio in directorios_buscar:
        if not directorio.exists():
            continue
        for ruta in sorted(directorio.rglob("*.md")):
            try:
                texto = ruta.read_text(encoding="utf-8")
            except OSError:
                continue
            ruta_rel = str(ruta.relative_to(ROOT))
            for m in patron.findall(texto):
                fid = m.upper()
                citas.setdefault(fid, set()).add(ruta_rel)

    # Ordenar IDs
    def _sort_key(fid: str) -> tuple:
        m = re.match(r"([A-Z]+)(\d+)", fid)
        if m:
            return (m.group(1), int(m.group(2)))
        return (fid, 0)

    ids_catalogo = sorted(chicago_map.keys(), key=_sort_key)
    ids_catalogo_upper = {k.upper() for k in chicago_map}
    ids_fuera = sorted(
        (fid for fid in citas if fid not in ids_catalogo_upper),
        key=_sort_key,
    )

    lineas = [MAPA_CITAS_HEADER]
    lineas.append(f"**Total fuentes en catálogo:** {len(ids_catalogo)}  \n")
    lineas.append(f"**Fuentes con al menos una cita:** {len(citas)}  \n\n")
    lineas.append("---\n\n")

    lineas.append("## Fuentes del catálogo y sus citas\n\n")
    for fid in ids_catalogo:
        # Use the chicago citation as the description (truncated)
        chicago = chicago_map.get(fid, "")
        titulo = chicago[:60] if chicago else fid
        archivos = sorted(citas.get(fid.upper(), []))
        if archivos:
            lineas.append(f"### {fid} — {titulo}\n\n")
            for a in archivos:
                lineas.append(f"- `{a}`\n")
            lineas.append("\n")
        else:
            lineas.append(f"### {fid} — {titulo}\n\n")
            lineas.append("_Sin citas detectadas en trabajo/ ni mapa/_\n\n")

    if ids_fuera:
        lineas.append("---\n\n")
        lineas.append("## IDs citados pero sin entrada en el catálogo\n\n")
        for fid in ids_fuera:
            archivos = sorted(citas[fid])
            lineas.append(f"- **{fid}** → {', '.join(f'`{a}`' for a in archivos)}\n")
        lineas.append("\n")

    write_file(FUENTES_DIR / "mapa_citas.md", "".join(lineas))


# ─── Log de cambios ──────────────────────────────────────────────────────────

def _log_cambios(archivos_generados: list[str]) -> None:
    """Registra en logs/generar_redaccion.log los archivos modificados."""
    log_path = ROOT / "datos" / "logs" / "generar_redaccion.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] Ejecución de generar_redaccion.py\n")
        for archivo in archivos_generados:
            f.write(f"  ✓ {archivo}\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def _construir_parser() -> "argparse.ArgumentParser":
    import argparse as _argparse
    parser = _argparse.ArgumentParser(
        description="Genera archivos de redacción anotada para la investigación histórica.",
        formatter_class=_argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--nodo",
        metavar="ID",
        help="Regenera solo el nodo con este ID (ej: 001, 003). "
             "Si se omite, regenera todos los nodos.",
    )
    parser.add_argument(
        "--sin-validacion",
        action="store_true",
        help="Omite la validación de datos (validar_datos.py) antes de generar.",
    )
    return parser


def main() -> None:
    parser = _construir_parser()
    args = parser.parse_args()

    print("\n=== Pipeline: validar → generar → actualizar vacíos ===\n")

    # ─── Paso 0: Validar datos ───────────────────────────────────────────────
    if not args.sin_validacion:
        print("0. Validando datos...")
        validar_script = ROOT / "tools" / "validar_datos.py"
        if validar_script.exists():
            resultado = subprocess.run(
                [sys.executable, str(validar_script), "--silencioso"],
                capture_output=True, text=True,
            )
            # Imprimir salida del validador (sin líneas vacías redundantes)
            for linea in resultado.stdout.splitlines():
                if linea.strip():
                    print(f"   {linea}")
            if resultado.returncode != 0:
                print("\n   ❌  La validación encontró errores. Corrígelos antes de generar.")
                print("       Ejecuta: python tools/validar_datos.py")
                sys.exit(1)
        else:
            print("   ⚠  validar_datos.py no encontrado — se omite la validación.")
    else:
        print("0. Validación omitida (--sin-validacion).")

    print("\n1. Catálogo de fuentes...")
    id_map = generate_catalog()

    # ─── Validación F### ─────────────────────────────────────────────────────
    if id_map:
        advertencias = validate_source_ids(id_map)
        if advertencias:
            print(f"\n   ⚠  {len(advertencias)} referencia(s) a IDs de fuente no encontrada(s):")
            for adv in advertencias:
                print(f"      • {adv}")
        else:
            print("   ✅ Todos los IDs de fuente referenciados están en el catálogo.")

    archivos_generados: list[str] = ["fuentes/catalogo_fuentes.md"]

    print("\n2. Archivos por período...")
    if args.nodo:
        # Modo individual: regenerar solo el nodo solicitado
        nodo_id_buscado = args.nodo.lstrip("0") or "0"  # normalizar "001" → "1"
        nodo_files = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))
        encontrado = False
        entries: list[tuple[str, str, str, str]] = []
        for nf in nodo_files:
            data = load_json(nf)
            nid = data.get("nodo_id", "")
            # Comparar ignorando ceros iniciales
            if nid.lstrip("0") == nodo_id_buscado or nid == args.nodo:
                file_slug, content = process_nodo(nf)
                titulo = data.get("titulo", nf.stem)
                rango = data.get("rango_temporal", "")
                write_file(TRABAJO_DIR / f"{file_slug}.md", content)
                entries.append((file_slug, titulo, rango, nf.name))
                archivos_generados.append(f"trabajo/periodos/{file_slug}.md")
                encontrado = True
                break
        if not encontrado:
            print(f"   ❌ No se encontró nodo con ID '{args.nodo}'.")
            sys.exit(1)
    else:
        entries = generate_periods()
        for file_slug, titulo, rango, filename in entries:
            archivos_generados.append(f"trabajo/periodos/{file_slug}.md")

    print("\n3. Mapa de personajes...")
    generate_personajes()
    archivos_generados.append("mapa/personajes.md")

    print("\n4. Índice...")
    if not args.nodo:
        generate_indice(entries)
        archivos_generados.append("trabajo/indice.md")
    else:
        print("   (omitido en modo --nodo)")

    # ─── Mapa de citas ───────────────────────────────────────────────────────
    if id_map and not args.nodo:
        print("\n4b. Mapa de citas cruzadas...")
        generate_mapa_citas(id_map)
        archivos_generados.append("fuentes/mapa_citas.md")

    # Ensure fuentes/pdf/ has a .gitkeep so it appears in git
    pdf_dir = FUENTES_DIR / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = pdf_dir / ".gitkeep"
    if not list(pdf_dir.iterdir()):
        gitkeep.touch()
        print(f"  ✓ fuentes/pdf/.gitkeep")

    # ─── Paso 5: Actualizar vacíos ───────────────────────────────────────────
    if not args.nodo:
        print("\n5. Actualizando VACIOS.md...")
        actualizar_script = ROOT / "tools" / "actualizar_vacios.py"
        if actualizar_script.exists():
            resultado = subprocess.run(
                [sys.executable, str(actualizar_script)],
                capture_output=True, text=True,
            )
            for linea in resultado.stdout.splitlines():
                if linea.strip():
                    print(f"   {linea}")
            if resultado.returncode != 0:
                print("   ⚠  actualizar_vacios.py retornó error (no es crítico).")
            else:
                archivos_generados.append("datos/VACIOS.md")
        else:
            print("   ⚠  actualizar_vacios.py no encontrado — se omite.")

    # ─── Log de cambios ──────────────────────────────────────────────────────
    _log_cambios(archivos_generados)

    print("\n=== Listo ===\n")
    print("Archivos generados:")
    for a in archivos_generados:
        print(f"  {a}")


if __name__ == "__main__":
    main()
