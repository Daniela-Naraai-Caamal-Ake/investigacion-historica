#!/usr/bin/env python3
"""
actualizar_vacios.py
====================
Regenera automáticamente ``datos/VACIOS.md`` leyendo los estados actuales
de las preguntas desde todos los archivos ``HOPELCHEN_PREGUNTAS_*.json``.

Uso:
    python tools/actualizar_vacios.py

Salida:
    datos/VACIOS.md  — sobrescrito con el estado más reciente de las preguntas

Flujo recomendado:
    1. Editar el campo ``estado`` en el JSON de preguntas correspondiente.
    2. Ejecutar este script.
    3. VACIOS.md se regenera con los estados actualizados.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"
VACIOS_PATH = ROOT / "datos" / "VACIOS.md"

# ─── Prioridades y su orden de aparición en el documento ─────────────────────

_PRIORIDAD_ORDEN = {
    "urgente": 0,
    "urgente — alta": 0,
    "alta": 1,
    "media-alta": 2,
    "alta — situación activa": 1,
    "alta — central para la hipótesis": 1,
    "media": 3,
    "media-baja": 4,
    "baja": 5,
}

_NIVEL_LABEL = {
    0: "URGENTE",
    1: "Alta",
    2: "Media-Alta",
    3: "Media",
    4: "Media-Baja",
    5: "Baja",
}

# ─── Iconos por estado ────────────────────────────────────────────────────────

_ESTADO_ICONO = {
    "pendiente": "🔴",
    "en proceso": "🟡",
    "respondida parcialmente": "🟠",
    "respondida": "🟢",
}


def _icono_estado(estado: str) -> str:
    estado_lower = estado.lower()
    for clave, icono in _ESTADO_ICONO.items():
        if estado_lower.startswith(clave):
            return icono
    return "⚪"


def _nivel_prioridad(prioridad: str) -> int:
    return _PRIORIDAD_ORDEN.get(prioridad.lower().strip(), 9)


def _extraer_preguntas(data: dict) -> list[dict]:
    """Extrae todas las preguntas de un archivo de preguntas."""
    preguntas: list[dict] = []
    for clave in (
        "preguntas", "preguntas_urgentes",
        "preguntas_alta_prioridad", "preguntas_media_prioridad",
    ):
        val = data.get(clave)
        if isinstance(val, list):
            preguntas.extend(v for v in val if isinstance(v, dict))
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


def cargar_todas_las_preguntas() -> list[dict]:
    """Carga y combina todas las preguntas de todos los archivos PREGUNTAS_*.json."""
    todas: list[dict] = []
    for path in sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_PREGUNTAS_*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  ⚠  No se pudo leer {path.name}: {exc}")
            continue
        nodo_origen = data.get("nodo_origen", path.stem)
        preguntas = _extraer_preguntas(data)
        for p in preguntas:
            p["_nodo_origen"] = nodo_origen
            p["_archivo"] = path.name
        todas.extend(preguntas)
    return todas


def agrupar_por_nivel(preguntas: list[dict]) -> dict[int, list[dict]]:
    """Agrupa preguntas por nivel de prioridad."""
    grupos: dict[int, list[dict]] = {}
    for p in preguntas:
        nivel = _nivel_prioridad(p.get("prioridad", "media"))
        grupos.setdefault(nivel, []).append(p)
    return grupos


def extraer_nodo_id(preg: dict) -> str:
    """Extrae el ID de nodo de una pregunta (p.ej. 'P006-08' → '006')."""
    pid = preg.get("pregunta_id", "")
    if pid.startswith("P") and "-" in pid:
        return pid[1:4]
    nodo = preg.get("_nodo_origen", "")
    if nodo and nodo[0:3].isdigit():
        return nodo[0:3]
    return "—"


def _donde_buscar(preg: dict) -> str:
    fuentes = preg.get("fuentes_a_consultar", [])
    if not fuentes:
        return "—"
    return "; ".join(str(f) for f in fuentes[:2])


def _estado_breve(preg: dict) -> str:
    estado = preg.get("estado", "PENDIENTE")
    if not estado:
        return "PENDIENTE"
    # Acortar si es muy largo
    if len(estado) > 120:
        return estado[:117] + "…"
    return estado


def generar_tabla_preguntas(preguntas: list[dict]) -> str:
    """Genera la tabla Markdown para una lista de preguntas."""
    lineas = [
        "| ID | Pregunta | Nodo | Dónde buscar | Estado |",
        "|----|----------|------|--------------|--------|",
    ]
    for p in preguntas:
        pid = p.get("pregunta_id", "—")
        pregunta = p.get("pregunta", "—")
        # Truncar pregunta larga
        if len(pregunta) > 110:
            pregunta = pregunta[:107] + "…"
        nodo_id = extraer_nodo_id(p)
        donde = _donde_buscar(p)
        estado = _estado_breve(p)
        icono = _icono_estado(p.get("estado", "PENDIENTE"))
        lineas.append(
            f"| **{pid}** | {pregunta} | {nodo_id} | {donde} | {icono} {estado} |"
        )
    return "\n".join(lineas)


def generar_vacios_md(preguntas: list[dict]) -> str:
    """Genera el contenido completo de VACIOS.md."""
    ahora = datetime.now().strftime("%Y-%m-%d")
    grupos = agrupar_por_nivel(preguntas)

    # Contar por estado
    total = len(preguntas)
    pendientes = sum(
        1 for p in preguntas
        if p.get("estado", "PENDIENTE").upper().startswith("PENDIENTE")
    )
    en_proceso = sum(
        1 for p in preguntas
        if p.get("estado", "").upper().startswith("EN PROCESO")
    )
    respondidas_parcial = sum(
        1 for p in preguntas
        if "RESPONDIDA PARCIALMENTE" in p.get("estado", "").upper()
    )
    respondidas = sum(
        1 for p in preguntas
        if p.get("estado", "").upper() == "RESPONDIDA"
    )

    lineas: list[str] = []

    # Encabezado
    lineas.append("# VACÍOS — Mapa Unificado de Preguntas Abiertas\n")
    lineas.append(
        "> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  \n"
        "> Autora: Daniela Naraai Caamal  \n"
        f"> Fuente: Consolidado de `datos/hopelchen/HOPELCHEN_PREGUNTAS_*.json`  \n"
        f"> Última actualización: {ahora}  \n"
        "> ⚙ Generado automáticamente por `tools/actualizar_vacios.py`\n"
    )
    lineas.append("\n")
    lineas.append("Este archivo unifica todas las preguntas abiertas del proyecto en una sola tabla de trabajo.  ")
    lineas.append("Estado posible: `PENDIENTE` · `EN PROCESO` · `RESPONDIDA PARCIALMENTE` · `RESPONDIDA`\n")

    # Resumen estadístico
    lineas.append("\n---\n")
    lineas.append("## Resumen estadístico\n")
    lineas.append(f"| Estado | Cantidad |")
    lineas.append(f"|--------|----------|")
    lineas.append(f"| 🔴 PENDIENTE | {pendientes} |")
    lineas.append(f"| 🟡 EN PROCESO | {en_proceso} |")
    lineas.append(f"| 🟠 RESPONDIDA PARCIALMENTE | {respondidas_parcial} |")
    lineas.append(f"| 🟢 RESPONDIDA | {respondidas} |")
    lineas.append(f"| **TOTAL** | **{total}** |\n")

    # Secciones por nivel de prioridad
    lineas.append("\n---\n")

    for nivel in sorted(grupos.keys()):
        pregs_nivel = grupos[nivel]
        label = _NIVEL_LABEL.get(nivel, f"Prioridad {nivel}")

        if nivel == 0:
            lineas.append(f"## PREGUNTAS {label.upper()} — Resolver primero\n")
            lineas.append(
                "Estas preguntas son cuellos de botella: sin ellas, capítulos enteros quedan incompletos.\n"
            )
        else:
            lineas.append(f"## PREGUNTAS DE PRIORIDAD {label.upper()}\n")

        # Agrupar por nodo dentro del nivel
        por_nodo: dict[str, list[dict]] = {}
        for p in pregs_nivel:
            nodo = extraer_nodo_id(p)
            por_nodo.setdefault(nodo, []).append(p)

        for nodo_id in sorted(por_nodo.keys()):
            nodo_pregs = por_nodo[nodo_id]
            nodo_origen = nodo_pregs[0].get("_nodo_origen", f"Nodo {nodo_id}")
            # Título breve del nodo
            nodo_titulo = nodo_origen.split(" — ")[-1][:60] if " — " in nodo_origen else nodo_origen[:60]
            lineas.append(f"\n### Nodo {nodo_id} — {nodo_titulo}\n")
            lineas.append(generar_tabla_preguntas(nodo_pregs))
            lineas.append("")

        lineas.append("\n---\n")

    # Instrucciones de uso
    lineas.append("## CÓMO USAR ESTE ARCHIVO\n")
    lineas.append(
        "- **Para actualizar estados:** edita el campo `estado` en el archivo "
        "`datos/hopelchen/HOPELCHEN_PREGUNTAS_<nodo>.json` correspondiente, "
        "luego ejecuta `python tools/actualizar_vacios.py`.\n"
        "- **Al encontrar una respuesta:** cambia el estado a "
        "`RESPONDIDA PARCIALMENTE` o `RESPONDIDA` y agrega el campo "
        "`registro_respuesta` con el ID del registro JSON donde se guardó la evidencia.\n"
        "- **Al identificar un nuevo vacío:** agrega la pregunta al archivo "
        "PREGUNTAS correspondiente con un `pregunta_id` nuevo; luego ejecuta este script.\n"
    )
    lineas.append(f"\n---\n")
    lineas.append(
        f"*Fuente de datos: `datos/hopelchen/HOPELCHEN_PREGUNTAS_*.json`*  \n"
        f"*Generado: {ahora} — ver también `datos/SINTESIS.md` para resumen ejecutivo del estado del repositorio*\n"
    )

    return "\n".join(lineas)


def main() -> None:
    print("\n=== Actualizando VACIOS.md ===\n")

    preguntas = cargar_todas_las_preguntas()
    print(f"  📋 Preguntas cargadas: {len(preguntas)}")

    if not preguntas:
        print("  ⚠  No se encontraron preguntas. VACIOS.md no fue modificado.")
        return

    contenido = generar_vacios_md(preguntas)
    VACIOS_PATH.parent.mkdir(parents=True, exist_ok=True)
    VACIOS_PATH.write_text(contenido, encoding="utf-8")
    print(f"  ✓ {VACIOS_PATH.relative_to(ROOT)}")
    print(f"\n=== Listo ===\n")


if __name__ == "__main__":
    main()
