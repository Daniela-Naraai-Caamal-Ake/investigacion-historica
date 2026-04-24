#!/usr/bin/env python3
"""
verificar_sincronizacion.py
===========================
Detecta inconsistencias entre las fuentes canónicas (JSON) y los archivos
derivados (VACIOS.md, SINTESIS_MAESTRA.md) del proyecto.

Problema que resuelve
---------------------
Cuando se actualiza el estado de una pregunta en un archivo
``HOPELCHEN_PREGUNTAS_*.json``, los archivos generados (VACIOS.md,
SINTESIS_MAESTRA.md) no se actualizan solos: hay que ejecutar los scripts
correspondientes manualmente.  Este verificador detecta cuándo hay
discrepancias y qué preguntas son las afectadas, o regenera los archivos
automáticamente si se pasa ``--auto-fix``.

Uso:
    python tools/verificar_sincronizacion.py            # Solo verificar
    python tools/verificar_sincronizacion.py --auto-fix # Regenerar archivos

Salidas:
    0 — Todo está sincronizado
    1 — Se detectaron discrepancias (o errores al regenerar)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
VACIOS_PATH = ROOT / "datos" / "VACIOS.md"
SINTESIS_PATH = ROOT / "SINTESIS_MAESTRA.md"
TOOLS = ROOT / "tools"

# ─── Extracción de preguntas desde JSON ──────────────────────────────────────

_CLAVES_CONOCIDAS = (
    "preguntas",
    "preguntas_urgentes",
    "preguntas_alta_prioridad",
    "preguntas_media_prioridad",
)


def extraer_preguntas_de_datos(data: dict) -> list[dict]:
    """
    Extrae todas las preguntas de un archivo PREGUNTAS_*.json.

    Busca en las claves canónicas y en cualquier clave que empiece con
    ``"preguntas"``, para capturar variantes como ``"preguntas_urgentes_005"``.
    Solo incluye entradas que sean dicts con el campo ``pregunta_id``.
    """
    claves_extra = [
        k for k in data
        if k.startswith("preguntas") and k not in _CLAVES_CONOCIDAS
    ]
    preguntas: list[dict] = []
    for clave in (*_CLAVES_CONOCIDAS, *claves_extra):
        val = data.get(clave)
        if isinstance(val, list):
            preguntas.extend(
                v for v in val
                if isinstance(v, dict) and v.get("pregunta_id")
            )
    # Deduplicar por pregunta_id
    vistos: set[str] = set()
    resultado: list[dict] = []
    for p in preguntas:
        pid = p.get("pregunta_id", "")
        if pid in vistos:
            continue
        vistos.add(pid)
        resultado.append(p)
    return resultado


def cargar_todas_las_preguntas() -> dict[str, dict]:
    """
    Lee todos los HOPELCHEN_PREGUNTAS_*.json y devuelve un mapa
    ``pregunta_id → {estado, prioridad, pregunta, archivo}``.
    """
    resultado: dict[str, dict] = {}
    for path in sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_PREGUNTAS_*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  ⚠  No se pudo leer {path.name}: {exc}")
            continue
        for p in extraer_preguntas_de_datos(data):
            pid = p.get("pregunta_id", "")
            if not pid:
                continue
            resultado[pid] = {
                "estado": p.get("estado", "PENDIENTE"),
                "prioridad": p.get("prioridad", ""),
                "pregunta": p.get("pregunta", "")[:80],
                "archivo": path.name,
            }
    return resultado


# ─── Lectura del estado desde VACIOS.md ──────────────────────────────────────

def leer_estados_vacios_md() -> dict[str, str]:
    """
    Parsea VACIOS.md y extrae el estado de cada pregunta de las tablas.
    Devuelve mapa ``pregunta_id → estado_texto``.
    """
    if not VACIOS_PATH.exists():
        return {}
    texto = VACIOS_PATH.read_text(encoding="utf-8")
    # Buscar filas de tabla: | **P001-01** | ... | 🟠 RESPONDIDA PARCIALMENTE |
    patron = re.compile(
        r"\|\s*\*\*(?P<pid>P\d{3}-\d+)\*\*\s*\|[^|]*\|[^|]*\|[^|]*\|"
        r"\s*(?:[🔴🟡🟠🟢⚪]\s*)?(?P<estado>[A-ZÁÉÍÓÚÑÜ][^\|]+?)\s*\|"
    )
    estados: dict[str, str] = {}
    for m in patron.finditer(texto):
        pid = m.group("pid")
        estado_raw = m.group("estado").strip()
        # Eliminar el icono emoji al inicio si quedara
        estado_limpio = re.sub(r"^[🔴🟡🟠🟢⚪]\s*", "", estado_raw).strip()
        estados[pid] = estado_limpio
    return estados


# ─── Comparación y reporte ────────────────────────────────────────────────────

def _normalizar(estado: str) -> str:
    """Normaliza el texto de estado para comparación insensible a mayúsculas."""
    return estado.upper().strip()


def verificar_vacios(
    preguntas_json: dict[str, dict],
    estados_md: dict[str, str],
) -> list[dict]:
    """
    Compara los estados del JSON con los de VACIOS.md.

    Detecta tres tipos de inconsistencias:
    - ``estado_diferente``: el estado en JSON difiere del estado en VACIOS.md
    - ``ausente_en_md``: pregunta existe en JSON pero no en VACIOS.md
    - ``fantasma_en_md``: pregunta aparece en VACIOS.md pero no en los JSON
    """
    inconsistencias: list[dict] = []

    for pid, info in preguntas_json.items():
        if pid not in estados_md:
            inconsistencias.append({
                "tipo": "ausente_en_md",
                "pregunta_id": pid,
                "estado_json": info["estado"],
                "estado_md": None,
                "archivo": info["archivo"],
                "pregunta": info["pregunta"],
            })
        else:
            estado_json = _normalizar(info["estado"])
            estado_md = _normalizar(estados_md[pid])
            if estado_json != estado_md:
                inconsistencias.append({
                    "tipo": "estado_diferente",
                    "pregunta_id": pid,
                    "estado_json": info["estado"],
                    "estado_md": estados_md[pid],
                    "archivo": info["archivo"],
                    "pregunta": info["pregunta"],
                })

    ids_json = set(preguntas_json.keys())
    for pid in estados_md:
        if pid not in ids_json:
            inconsistencias.append({
                "tipo": "fantasma_en_md",
                "pregunta_id": pid,
                "estado_json": None,
                "estado_md": estados_md[pid],
                "archivo": None,
                "pregunta": None,
            })

    return inconsistencias


def verificar_resumen_vacios(preguntas_json: dict[str, dict]) -> list[str]:
    """
    Compara el resumen estadístico en VACIOS.md (totales por estado)
    con lo que dicen los JSON.
    """
    if not VACIOS_PATH.exists():
        return ["VACIOS.md no existe"]

    texto = VACIOS_PATH.read_text(encoding="utf-8")

    # Contar desde JSON
    conteo_json: dict[str, int] = {
        "PENDIENTE": 0, "EN PROCESO": 0,
        "RESPONDIDA PARCIALMENTE": 0, "RESPONDIDA": 0,
    }
    for info in preguntas_json.values():
        est = _normalizar(info["estado"])
        for clave in conteo_json:
            if est.startswith(clave):
                conteo_json[clave] += 1
                break

    # Extraer totales del resumen en VACIOS.md
    inconsistencias: list[str] = []
    patron_fila = re.compile(
        r"\|\s*[🔴🟡🟠🟢⚪]\s*(PENDIENTE|EN PROCESO|RESPONDIDA PARCIALMENTE|RESPONDIDA)\s*\|\s*(\d+)\s*\|"
    )
    conteo_md: dict[str, int] = {}
    for m in patron_fila.finditer(texto):
        conteo_md[m.group(1)] = int(m.group(2))

    for clave, esperado in conteo_json.items():
        en_md = conteo_md.get(clave)
        if en_md is None:
            inconsistencias.append(
                f"Falta fila '{clave}' en el resumen de VACIOS.md"
            )
        elif en_md != esperado:
            inconsistencias.append(
                f"'{clave}': VACIOS.md dice {en_md}, JSON dice {esperado}"
            )

    return inconsistencias


# ─── Auto-fix ────────────────────────────────────────────────────────────────

def regenerar_archivos() -> bool:
    """
    Ejecuta los scripts de generación para sincronizar los archivos derivados.
    Devuelve True si todos los scripts terminaron sin error.
    """
    scripts = [
        (TOOLS / "actualizar_vacios.py", "VACIOS.md"),
        (TOOLS / "generar_sintesis.py", "SINTESIS_MAESTRA.md"),
        (TOOLS / "grafo_epistemologico.py", "grafo_epistemologico.md / .json"),
    ]
    ok = True
    for script, descripcion in scripts:
        if not script.exists():
            print(f"  ⚠  No se encontró {script.name} — omitiendo")
            continue
        print(f"  ⏳ Regenerando {descripcion}…")
        resultado = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            print(f"  ❌ Error en {script.name}:")
            print(resultado.stderr[-500:] if resultado.stderr else "(sin stderr)")
            ok = False
        else:
            print(f"  ✅ {script.name} completado")
    return ok


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifica que VACIOS.md y archivos derivados estén sincronizados con los JSON."
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Regenera los archivos derivados automáticamente si hay discrepancias.",
    )
    args = parser.parse_args()

    print("\n=== Verificación de sincronización ===\n")

    # 1. Cargar datos canónicos
    preguntas_json = cargar_todas_las_preguntas()
    print(f"  📋 Preguntas en JSON: {len(preguntas_json)}")

    if not preguntas_json:
        print("  ⚠  No se encontraron preguntas en los JSON. Abortando.")
        sys.exit(1)

    # 2. Verificar VACIOS.md
    hay_inconsistencias = False

    if not VACIOS_PATH.exists():
        print(f"\n  ❌ {VACIOS_PATH.name} no existe — debe ser generado.\n")
        hay_inconsistencias = True
    else:
        estados_md = leer_estados_vacios_md()
        print(f"  📋 Preguntas en VACIOS.md: {len(estados_md)}")

        inconsistencias = verificar_vacios(preguntas_json, estados_md)
        resumen_inconsistencias = verificar_resumen_vacios(preguntas_json)

        if not inconsistencias and not resumen_inconsistencias:
            print(f"\n  ✅ VACIOS.md está sincronizado con los JSON.\n")
        else:
            hay_inconsistencias = True
            print(f"\n  ⚠  VACIOS.md tiene {len(inconsistencias)} discrepancia(s) de estado:\n")

            por_tipo: dict[str, list[dict]] = {}
            for inc in inconsistencias:
                por_tipo.setdefault(inc["tipo"], []).append(inc)

            if por_tipo.get("estado_diferente"):
                print("  🔄 Estado diferente entre JSON y VACIOS.md:")
                for inc in por_tipo["estado_diferente"]:
                    print(
                        f"     {inc['pregunta_id']:12s} | JSON: {inc['estado_json']!r:35s}"
                        f" | VACIOS.md: {inc['estado_md']!r}"
                    )
                    print(f"                  Archivo: {inc['archivo']}")
                    print(f"                  Pregunta: {inc['pregunta']}…")
                    print()

            if por_tipo.get("ausente_en_md"):
                print("  ➕ Preguntas en JSON pero ausentes en VACIOS.md:")
                for inc in por_tipo["ausente_en_md"]:
                    print(
                        f"     {inc['pregunta_id']:12s} | {inc['estado_json']!r}"
                        f" ({inc['archivo']})"
                    )
                print()

            if por_tipo.get("fantasma_en_md"):
                print("  👻 Preguntas en VACIOS.md sin registro en JSON:")
                for inc in por_tipo["fantasma_en_md"]:
                    print(f"     {inc['pregunta_id']:12s} | {inc['estado_md']!r}")
                print()

            if resumen_inconsistencias:
                print("  📊 Resumen estadístico de VACIOS.md desactualizado:")
                for msg in resumen_inconsistencias:
                    print(f"     • {msg}")
                print()

    # 3. Auto-fix
    if hay_inconsistencias:
        if args.auto_fix:
            print("  🔧 --auto-fix activado: regenerando archivos…\n")
            ok = regenerar_archivos()
            if ok:
                print(
                    "\n  ✅ Archivos regenerados. Ejecuta este script de nuevo "
                    "para confirmar la sincronización.\n"
                )
                sys.exit(0)
            else:
                print("\n  ❌ Algunos scripts fallaron al regenerar.\n")
                sys.exit(1)
        else:
            print(
                "  💡 Para sincronizar, ejecuta:\n"
                "     python tools/actualizar_vacios.py\n"
                "     python tools/generar_sintesis.py\n"
                "     python tools/grafo_epistemologico.py\n"
                "\n"
                "     O de forma automática:\n"
                "     python tools/verificar_sincronizacion.py --auto-fix\n"
            )
            sys.exit(1)
    else:
        print("  ✅ Todo sincronizado.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
