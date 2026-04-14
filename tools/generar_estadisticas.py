#!/usr/bin/env python3
"""
generar_estadisticas.py
=======================
Genera el archivo docs/stats.json con estadísticas del proyecto histórico
para el tablero interactivo en GitHub Pages.

Uso:
    python tools/generar_estadisticas.py
    python tools/generar_estadisticas.py --salida docs/stats.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
FUENTES_DIR = ROOT / "fuentes"
TRABAJO_DIR = ROOT / "trabajo"
SALIDA_DEFAULT = ROOT / "docs" / "stats.json"

# Campos de fuente reconocidos en registros
CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica", "fuente_primaria",
    "fuente_secundaria", "fuentes",
]


def _tiene_fuente(registro: dict) -> bool:
    for campo in CAMPOS_FUENTE:
        val = registro.get(campo)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return True
        if isinstance(val, (dict, list)) and val:
            return True
    return False


def _tiene_conexion(registro: dict) -> bool:
    val = registro.get("conexion_hipotesis", "")
    return bool(val and str(val).strip())


def _extraer_años(texto: str) -> list[int]:
    """Extrae valores numéricos de año de texto histórico libre."""
    if not isinstance(texto, str):
        return []
    patron_neg = re.compile(r"(\d{1,4})\s*a\.C\.", re.IGNORECASE)
    patron_pos = re.compile(r"\b(\d{3,4})\b")
    años: list[int] = []
    for m in patron_neg.finditer(texto):
        años.append(-int(m.group(1)))
    for m in patron_pos.finditer(texto):
        if re.match(r"\s*a\.C\.", texto[m.end(): m.end() + 6], re.IGNORECASE):
            continue
        años.append(int(m.group(1)))
    return años


def _contar_preguntas(path: Path) -> dict[str, int]:
    """Devuelve conteo de preguntas por estado en un archivo PREGUNTAS_*.json."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    for clave in ("preguntas", "preguntas_urgentes", "preguntas_alta_prioridad"):
        lista = data.get(clave)
        if isinstance(lista, list):
            break
    else:
        return {}

    conteo: dict[str, int] = {}
    for preg in lista:
        if not isinstance(preg, dict):
            continue
        estado = str(preg.get("estado", "PENDIENTE")).upper()
        # Normalizar a RESPONDIDA / PENDIENTE / EN_CURSO / otro
        if estado.startswith("RESPONDIDA"):
            clave_estado = "Respondida"
        elif estado.startswith("EN_CURSO") or estado.startswith("EN CURSO"):
            clave_estado = "En curso"
        else:
            clave_estado = "Pendiente"
        conteo[clave_estado] = conteo.get(clave_estado, 0) + 1
    return conteo


def generar_stats() -> dict:
    stats: dict = {
        "generado_en": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nodos": [],
        "resumen": {},
        "preguntas": {"por_nodo": {}, "totales": {}},
        "cobertura": {},
    }

    total_registros = 0
    total_con_fuente = 0
    total_con_conexion = 0
    total_sin_fuente = 0
    total_sin_conexion = 0
    tipos_dato: dict[str, int] = {}

    nodo_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))

    for path in nodo_paths:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        registros = data.get("registros", [])
        n_registros = len(registros)
        n_con_fuente = sum(1 for r in registros if _tiene_fuente(r))
        n_con_conexion = sum(1 for r in registros if _tiene_conexion(r))

        total_registros += n_registros
        total_con_fuente += n_con_fuente
        total_con_conexion += n_con_conexion
        total_sin_fuente += n_registros - n_con_fuente
        total_sin_conexion += n_registros - n_con_conexion

        for reg in registros:
            tipo = str(reg.get("tipo_dato", "sin_tipo")).strip()
            if tipo:
                tipos_dato[tipo] = tipos_dato.get(tipo, 0) + 1

        nodo_id = data.get("nodo_id", path.stem)
        titulo = data.get("titulo", nodo_id)
        rango = data.get("rango_temporal", "")
        años = _extraer_años(rango)
        año_inicio = min(años) if años else None
        año_fin = max(años) if años else None

        stats["nodos"].append({
            "id": nodo_id,
            "titulo": titulo,
            "rango_temporal": rango,
            "año_inicio": año_inicio,
            "año_fin": año_fin,
            "n_registros": n_registros,
            "n_con_fuente": n_con_fuente,
            "n_con_conexion": n_con_conexion,
            "pct_fuente": round(100 * n_con_fuente / n_registros, 1) if n_registros else 0,
            "pct_conexion": round(100 * n_con_conexion / n_registros, 1) if n_registros else 0,
        })

    # Preguntas
    preguntas_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_PREGUNTAS_*.json"))
    totales_preguntas: dict[str, int] = {}
    for path in preguntas_paths:
        nodo_num = re.search(r"_(\d+)_", path.name)
        clave = nodo_num.group(1) if nodo_num else path.stem
        conteo = _contar_preguntas(path)
        stats["preguntas"]["por_nodo"][clave] = conteo
        for estado, n in conteo.items():
            totales_preguntas[estado] = totales_preguntas.get(estado, 0) + n

    stats["preguntas"]["totales"] = totales_preguntas

    # Resumen global
    stats["resumen"] = {
        "total_nodos": len(stats["nodos"]),
        "total_registros": total_registros,
        "total_con_fuente": total_con_fuente,
        "total_sin_fuente": total_sin_fuente,
        "total_con_conexion": total_con_conexion,
        "total_sin_conexion": total_sin_conexion,
        "total_preguntas": sum(totales_preguntas.values()),
        "pct_fuente_global": round(100 * total_con_fuente / total_registros, 1) if total_registros else 0,
        "pct_conexion_global": round(100 * total_con_conexion / total_registros, 1) if total_registros else 0,
    }

    stats["cobertura"]["tipos_dato"] = dict(
        sorted(tipos_dato.items(), key=lambda x: x[1], reverse=True)
    )

    # Tipos agrupados para visualización
    grupos: dict[str, int] = {
        "Citado": 0, "Análisis": 0, "Biográfico": 0,
        "Inferido": 0, "Verificado": 0, "Contextual": 0, "Otros": 0,
    }
    for tipo, n in tipos_dato.items():
        t = tipo.lower()
        if "citado" in t:
            grupos["Citado"] += n
        elif "análisis" in t or "analisis" in t:
            grupos["Análisis"] += n
        elif "biográfico" in t or "biografico" in t:
            grupos["Biográfico"] += n
        elif "inferido" in t:
            grupos["Inferido"] += n
        elif "verificado" in t:
            grupos["Verificado"] += n
        elif "contextual" in t:
            grupos["Contextual"] += n
        else:
            grupos["Otros"] += n
    stats["cobertura"]["tipos_agrupados"] = {
        k: v for k, v in grupos.items() if v > 0
    }

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera docs/stats.json para el tablero de estadísticas."
    )
    parser.add_argument(
        "--salida",
        default=str(SALIDA_DEFAULT),
        help="Ruta del archivo de salida (default: docs/stats.json)",
    )
    args = parser.parse_args()

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    stats = generar_stats()

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    total = stats["resumen"]["total_registros"]
    nodos = stats["resumen"]["total_nodos"]
    print(f"✅  stats.json generado → {salida}")
    print(f"   {nodos} nodos · {total} registros · "
          f"{stats['resumen']['pct_fuente_global']}% con fuente")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
