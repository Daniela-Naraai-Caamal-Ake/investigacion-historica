#!/usr/bin/env python3
"""
generar_indice_busqueda.py
==========================
Genera docs/search_index.json con el índice de búsqueda semántica del proyecto.

El índice contiene, por cada registro histórico:
    - registro_id, nodo_id, titulo_nodo
    - fecha_evento, lugar
    - texto_completo: concatenación de todos los campos textuales
    - tags

Uso:
    python tools/generar_indice_busqueda.py
    python tools/generar_indice_busqueda.py --salida docs/search_index.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
SALIDA_DEFAULT = ROOT / "docs" / "search_index.json"

CAMPOS_TEXTO = [
    "subtitulo", "descripcion", "conexion_hipotesis",
    "notas_contradiccion", "personajes",
]
CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica", "fuente_primaria",
    "fuente_secundaria",
]


def _texto_campo(val) -> str:
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, list):
        return " ".join(str(v) for v in val if v)
    if isinstance(val, dict):
        return " ".join(str(v) for v in val.values() if v)
    return ""


def _fuente_str(registro: dict) -> str:
    partes: list[str] = []
    for campo in CAMPOS_FUENTE:
        val = registro.get(campo)
        if val:
            t = _texto_campo(val)
            if t:
                partes.append(t)
    fuentes_lista = registro.get("fuentes")
    if isinstance(fuentes_lista, list):
        for item in fuentes_lista:
            t = _texto_campo(item)
            if t:
                partes.append(t)
    return " | ".join(partes)


def construir_indice() -> list[dict]:
    entradas: list[dict] = []

    nodo_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))
    for path in nodo_paths:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        nodo_id = data.get("nodo_id", path.stem)
        titulo_nodo = data.get("titulo", nodo_id)
        era = data.get("era", "")
        rango = data.get("rango_temporal", "")

        for reg in data.get("registros", []):
            if not isinstance(reg, dict):
                continue

            rid = str(reg.get("registro_id", ""))

            # Construir texto completo concatenando todos los campos relevantes
            partes_texto = [
                titulo_nodo,
                reg.get("subtitulo", ""),
                reg.get("descripcion", ""),
                reg.get("conexion_hipotesis", ""),
                reg.get("notas_contradiccion", ""),
                _texto_campo(reg.get("personajes", "")),
                reg.get("lugar", ""),
                reg.get("fecha_evento", ""),
                era,
            ]
            # Añadir tags
            tags = reg.get("tags", [])
            if isinstance(tags, list):
                partes_texto.extend(tags)
            elif isinstance(tags, str):
                partes_texto.append(tags)

            texto_completo = " ".join(p for p in partes_texto if p and str(p).strip())

            entrada = {
                "registro_id": rid,
                "nodo_id": nodo_id,
                "titulo_nodo": titulo_nodo,
                "era": era,
                "rango_temporal": rango,
                "fecha_evento": reg.get("fecha_evento", ""),
                "lugar": reg.get("lugar", ""),
                "subtitulo": reg.get("subtitulo", ""),
                "descripcion": reg.get("descripcion", ""),
                "conexion_hipotesis": reg.get("conexion_hipotesis", ""),
                "fuente": _fuente_str(reg),
                "tags": tags if isinstance(tags, list) else ([tags] if tags else []),
                "tipo_dato": reg.get("tipo_dato", ""),
                "texto_completo": texto_completo,
            }
            entradas.append(entrada)

    return entradas


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera docs/search_index.json para búsqueda semántica."
    )
    parser.add_argument(
        "--salida",
        default=str(SALIDA_DEFAULT),
        help="Ruta del archivo de salida (default: docs/search_index.json)",
    )
    args = parser.parse_args()

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    indice = construir_indice()

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

    print(f"✅  search_index.json generado → {salida}")
    print(f"   {len(indice)} registros indexados")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
