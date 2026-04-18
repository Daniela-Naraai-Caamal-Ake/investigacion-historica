#!/usr/bin/env python3
"""
generar_matriz_cruces.py
========================
Genera análisis/cruce_informacion.md — una matriz que muestra cómo los
registros de distintos nodos se relacionan a través de actores comunes,
mecanismos estructurales y temas transversales.

Esto es la Capa 4 del sistema (relaciones): hace visibles patrones y
tensiones que no son visibles dentro de un solo nodo.

Uso:
    python tools/generar_matriz_cruces.py
"""

from __future__ import annotations
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
NODOS_DIR = ROOT / "datos" / "hopelchen"
SALIDA = ROOT / "analisis" / "cruce_informacion.md"

TITULOS_NODOS = {
    "001": "Prehispánico",
    "002": "Conquista Colonial",
    "003": "Colonia Tardía–Porfiriato",
    "004": "Revolución–Chicle",
    "005": "Contemporáneo",
    "006": "Poder Político Local",
    "007": "Rutas y Territorio",
    "008": "Demografía",
    "009": "Resistencia Maya",
    "010": "Conocimiento y Cultura",
}

MECANISMOS_CLAVE = [
    "control", "poder", "resistencia", "despojo", "tierra",
    "extracción", "silencio", "linaje", "apellido", "concentración",
    "subordinación", "autonomía",
]

TAGS_IGNORAR = {"Hopelchén", "Los Chenes", "Campeche", "maya", "mayas"}


def cargar_nodos() -> list[dict]:
    nodos = []
    for path in sorted(glob.glob(str(NODOS_DIR / "HOPELCHEN_NODO_*.json"))):
        with open(path, encoding="utf-8") as f:
            nodos.append(json.load(f))
    return nodos


def extraer_actores(nodos: list[dict]) -> dict[str, list[dict]]:
    """Actor → lista de {nodo, registro_id, subtitulo, descripcion}"""
    actores: dict[str, list] = {}
    for data in nodos:
        nodo = data["nodo_id"]
        for r in data.get("registros", []):
            for p in r.get("personajes", []):
                nombre = p.get("nombre", "") if isinstance(p, dict) else str(p)
                if not nombre:
                    continue
                actores.setdefault(nombre, []).append({
                    "nodo": nodo,
                    "titulo_nodo": TITULOS_NODOS.get(nodo, nodo),
                    "registro_id": r["registro_id"],
                    "subtitulo": r.get("subtitulo", "")[:80],
                    "cargo": p.get("cargo", "") if isinstance(p, dict) else "",
                    "descripcion": r.get("descripcion", "")[:200],
                })
    return actores


def extraer_tags(nodos: list[dict]) -> dict[str, list[dict]]:
    """Tag → lista de {nodo, registro_id, subtitulo}"""
    tags: dict[str, list] = {}
    for data in nodos:
        nodo = data["nodo_id"]
        for r in data.get("registros", []):
            for t in r.get("tags", []):
                if t in TAGS_IGNORAR:
                    continue
                tags.setdefault(t, []).append({
                    "nodo": nodo,
                    "titulo_nodo": TITULOS_NODOS.get(nodo, nodo),
                    "registro_id": r["registro_id"],
                    "subtitulo": r.get("subtitulo", "")[:80],
                })
    return tags


def extraer_mecanismos(nodos: list[dict]) -> dict[str, list[dict]]:
    """Mecanismo → lista de registros donde aparece en conexion_hipotesis"""
    mecanismos: dict[str, list] = {}
    for data in nodos:
        nodo = data["nodo_id"]
        for r in data.get("registros", []):
            ch = r.get("conexion_hipotesis", "").lower()
            desc = r.get("descripcion", "")[:200]
            for mec in MECANISMOS_CLAVE:
                if mec.lower() in ch:
                    mecanismos.setdefault(mec, []).append({
                        "nodo": nodo,
                        "titulo_nodo": TITULOS_NODOS.get(nodo, nodo),
                        "registro_id": r["registro_id"],
                        "subtitulo": r.get("subtitulo", "")[:80],
                        "fragmento_conexion": r.get("conexion_hipotesis", "")[:180],
                    })
    return mecanismos


def nodos_set(refs: list[dict]) -> list[str]:
    return sorted(set(r["nodo"] for r in refs))


def generar_md(nodos: list[dict]) -> str:
    actores = extraer_actores(nodos)
    tags = extraer_tags(nodos)
    mecanismos = extraer_mecanismos(nodos)
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lineas = [
        "# Matriz de cruces — *Dos Mil Años en Silencio*",
        "",
        "> Autora: Daniela Naraai Caamal Ake  ",
        f"> Generado: {ahora}  ",
        "> ⚙ Generado automáticamente por `tools/generar_matriz_cruces.py`",
        "",
        "Este archivo es la **Capa 4 del sistema** (relaciones). Muestra cómo registros",
        "de distintos nodos se conectan a través de actores comunes, mecanismos",
        "estructurales y temas transversales. Las relaciones aquí no son conclusiones:",
        "son patrones visibles que el análisis humano puede usar o cuestionar.",
        "",
        "---",
        "",
        "## Índice",
        "",
        "1. [Actores en múltiples nodos](#1-actores-en-múltiples-nodos)",
        "2. [Mecanismos estructurales transversales](#2-mecanismos-estructurales-transversales)",
        "3. [Temas que atraviesan períodos](#3-temas-que-atraviesan-períodos)",
        "4. [Tabla de cobertura por nodo](#4-tabla-de-cobertura-por-nodo)",
        "",
        "---",
        "",
        "## 1. Actores en múltiples nodos",
        "",
        "Personas que aparecen en más de un nodo temático. Su presencia en distintos",
        "períodos o ámbitos indica continuidad histórica o conexión estructural.",
        "",
    ]

    # Actores en 2+ nodos
    multi_nodo = {
        k: v for k, v in actores.items()
        if len(set(r["nodo"] for r in v)) > 1
    }

    if multi_nodo:
        for nombre, refs in sorted(multi_nodo.items(),
                                   key=lambda x: -len(set(r["nodo"] for r in x[1]))):
            nodos_involucrados = nodos_set(refs)
            nombres_nodos = " · ".join(
                f"{n} ({TITULOS_NODOS.get(n,n)})" for n in nodos_involucrados
            )
            lineas += [
                f"### {nombre}",
                "",
                f"**Nodos:** {nombres_nodos}",
                "",
            ]
            for ref in refs:
                cargo = f" — *{ref['cargo']}*" if ref.get("cargo") else ""
                lineas.append(
                    f"- **[{ref['nodo']}] {ref['registro_id']}**{cargo}: "
                    f"{ref['subtitulo']}"
                )
            lineas.append("")
    else:
        lineas.append("*No se detectaron actores en múltiples nodos.*\n")

    lineas += [
        "---",
        "",
        "## 2. Mecanismos estructurales transversales",
        "",
        "Mecanismos de control, despojo o resistencia que el sistema detecta",
        "repetidos a través del tiempo. Su recurrencia en múltiples nodos es",
        "evidencia del patrón estructural que la hipótesis propone verificar.",
        "",
    ]

    for mec, refs in sorted(mecanismos.items(), key=lambda x: -len(x[1])):
        nodos_involucrados = nodos_set(refs)
        cobertura = len(nodos_involucrados)
        nombres_nodos = " · ".join(
            f"{n} ({TITULOS_NODOS.get(n,n)})" for n in nodos_involucrados
        )
        lineas += [
            f"### `{mec}` — {cobertura} nodos",
            "",
            f"**Presente en:** {nombres_nodos}",
            "",
            "| Registro | Nodo | Contexto |",
            "|---|---|---|",
        ]
        for ref in refs:
            fragmento = ref["fragmento_conexion"].replace("\n", " ").replace("|", "·")[:120]
            lineas.append(
                f"| {ref['registro_id']} | {ref['nodo']} {ref['titulo_nodo']} "
                f"| {fragmento}… |"
            )
        lineas.append("")

    lineas += [
        "---",
        "",
        "## 3. Temas que atraviesan períodos",
        "",
        "Tags que aparecen en registros de 3 o más nodos distintos. Indican",
        "continuidades temáticas que no se confinan a un solo período histórico.",
        "",
        "| Tema | Registros | Nodos donde aparece |",
        "|---|---|---|",
    ]

    tags_multi = {
        k: v for k, v in tags.items()
        if len(set(r["nodo"] for r in v)) >= 3
    }
    for tag, refs in sorted(tags_multi.items(),
                            key=lambda x: -len(set(r["nodo"] for r in x[1]))):
        nodos_inv = nodos_set(refs)
        nombres = ", ".join(f"{n} ({TITULOS_NODOS.get(n,n)})" for n in nodos_inv)
        lineas.append(f"| **{tag}** | {len(refs)} | {nombres} |")

    lineas += [
        "",
        "---",
        "",
        "## 4. Tabla de cobertura por nodo",
        "",
        "Cuántos registros contribuye cada nodo a los cruces detectados.",
        "",
        "| Nodo | Título | Registros | En cruces de actores | En cruces de mecanismos |",
        "|---|---|---|---|---|",
    ]

    for data in nodos:
        nodo = data["nodo_id"]
        titulo = TITULOS_NODOS.get(nodo, nodo)
        total = len(data.get("registros", []))

        # Cuántos registros aparecen en cruces de actores
        ids_en_actores = set()
        for refs in multi_nodo.values():
            for ref in refs:
                if ref["nodo"] == nodo:
                    ids_en_actores.add(ref["registro_id"])

        # Cuántos registros aparecen en cruces de mecanismos
        ids_en_mec = set()
        for refs in mecanismos.values():
            for ref in refs:
                if ref["nodo"] == nodo:
                    ids_en_mec.add(ref["registro_id"])

        lineas.append(
            f"| {nodo} | {titulo} | {total} | {len(ids_en_actores)} | {len(ids_en_mec)} |"
        )

    lineas += [
        "",
        "---",
        "",
        "*Las relaciones aquí registradas son el resultado del análisis automático*",
        "*sobre los campos `personajes`, `tags` y `conexion_hipotesis` de los nodos.*",
        "*No sustituyen el juicio analítico — son su punto de partida.*",
    ]

    return "\n".join(lineas)


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    nodos = cargar_nodos()
    contenido = generar_md(nodos)
    SALIDA.write_text(contenido, encoding="utf-8")
    n_palabras = len(contenido.split())
    print(f"[generar_matriz_cruces] ✅ Escrito: {SALIDA} ({n_palabras:,} palabras)")


if __name__ == "__main__":
    main()
