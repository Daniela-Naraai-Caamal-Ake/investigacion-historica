#!/usr/bin/env python3
"""
validar_datos.py
================
Valida la integridad estructural de todos los archivos de datos del proyecto
antes de ejecutar la generación de redacción.

Uso:
    python tools/validar_datos.py            # Valida todos los archivos
    python tools/validar_datos.py --estricto # Falla si hay advertencias

Salidas:
    0 — Sin errores (puede haber advertencias)
    1 — Se encontraron errores que bloquean la generación

Verificaciones realizadas:
    - Cada HOPELCHEN_NODO_*.json tiene los campos requeridos
    - Cada registro dentro de un nodo tiene registro_id, fuente y conexion_hipotesis
    - Cada HOPELCHEN_PREGUNTAS_*.json tiene estructura válida
    - No hay IDs de registro duplicados dentro de un mismo nodo
    - Las preguntas con estado RESPONDIDA tienen campo registro_respuesta
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"

# ─── Campos requeridos ────────────────────────────────────────────────────────

NODO_CAMPOS_REQUERIDOS = ["nodo_id", "titulo", "rango_temporal", "registros"]
REGISTRO_CAMPOS_REQUERIDOS = ["registro_id"]
REGISTRO_CAMPOS_RECOMENDADOS = ["conexion_hipotesis"]

# Aceptamos cualquiera de estos como campo de fuente
REGISTRO_CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica", "fuente_primaria",
    "fuente_secundaria", "fuentes",
]


# ─── Contadores y utilidades ─────────────────────────────────────────────────

class Resultado:
    def __init__(self) -> None:
        self.errores: list[str] = []
        self.advertencias: list[str] = []

    def error(self, msg: str) -> None:
        self.errores.append(msg)

    def advertencia(self, msg: str) -> None:
        self.advertencias.append(msg)

    @property
    def ok(self) -> bool:
        return len(self.errores) == 0

    def imprimir(self) -> None:
        if self.errores:
            print(f"\n{'─' * 60}")
            print(f"  ❌  {len(self.errores)} ERROR(ES) encontrado(s):")
            for e in self.errores:
                print(f"     • {e}")
        if self.advertencias:
            print(f"\n{'─' * 60}")
            print(f"  ⚠   {len(self.advertencias)} ADVERTENCIA(S):")
            for a in self.advertencias:
                print(f"     • {a}")
        if not self.errores and not self.advertencias:
            print("  ✅  Sin problemas encontrados.")


def _tiene_fuente(registro: dict) -> bool:
    """Devuelve True si el registro tiene al menos un campo de fuente con valor."""
    for campo in REGISTRO_CAMPOS_FUENTE:
        val = registro.get(campo)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return True
        if isinstance(val, dict) and val:
            return True
        if isinstance(val, list) and val:
            return True
    return False


# ─── Validación de NODO_*.json ───────────────────────────────────────────────

def validar_nodo(path: Path, res: Resultado) -> None:
    nombre = path.name

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        res.error(f"{nombre}: JSON inválido — {exc}")
        return

    # Campos requeridos en la raíz
    for campo in NODO_CAMPOS_REQUERIDOS:
        if campo not in data:
            res.error(f"{nombre}: campo requerido ausente en raíz → '{campo}'")

    nodo_id = data.get("nodo_id", nombre)
    registros = data.get("registros", [])

    if not isinstance(registros, list):
        res.error(f"{nombre}: 'registros' debe ser una lista, no {type(registros).__name__}")
        return

    if len(registros) == 0:
        res.advertencia(f"{nombre} (nodo {nodo_id}): 'registros' está vacío")

    ids_vistos: set[str] = set()
    for i, reg in enumerate(registros):
        if not isinstance(reg, dict):
            res.error(f"{nombre}: registro[{i}] no es un objeto JSON")
            continue

        # registro_id obligatorio
        rid = reg.get("registro_id")
        if not rid:
            res.error(f"{nombre} (nodo {nodo_id}): registro[{i}] sin 'registro_id'")
        else:
            if rid in ids_vistos:
                res.error(
                    f"{nombre} (nodo {nodo_id}): registro_id duplicado → '{rid}'"
                )
            ids_vistos.add(str(rid))

        # fuente (requerida)
        if not _tiene_fuente(reg):
            res.advertencia(
                f"{nombre} (nodo {nodo_id}): registro '{rid}' sin campo de fuente"
            )

        # conexion_hipotesis (recomendada)
        for campo in REGISTRO_CAMPOS_RECOMENDADOS:
            if not reg.get(campo):
                res.advertencia(
                    f"{nombre} (nodo {nodo_id}): registro '{rid}' sin '{campo}'"
                )


# ─── Validación de PREGUNTAS_*.json ──────────────────────────────────────────

def _extraer_lista_preguntas(data: dict) -> list[dict]:
    """Busca la lista de preguntas bajo distintas claves posibles."""
    for clave in ("preguntas", "preguntas_urgentes", "preguntas_alta_prioridad"):
        val = data.get(clave)
        if isinstance(val, list):
            return val
    # Buscar recursivamente listas de dicts con 'pregunta_id'
    for val in data.values():
        if isinstance(val, list) and val and isinstance(val[0], dict):
            if val[0].get("pregunta_id"):
                return val
    return []


def validar_preguntas(path: Path, res: Resultado) -> None:
    nombre = path.name

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        res.error(f"{nombre}: JSON inválido — {exc}")
        return

    if "nodo_origen" not in data:
        res.advertencia(f"{nombre}: campo 'nodo_origen' ausente")

    preguntas = _extraer_lista_preguntas(data)
    if not preguntas:
        res.advertencia(f"{nombre}: no se encontró lista de preguntas")
        return

    ids_vistos: set[str] = set()
    for i, preg in enumerate(preguntas):
        if not isinstance(preg, dict):
            res.error(f"{nombre}: pregunta[{i}] no es un objeto JSON")
            continue

        pid = preg.get("pregunta_id")
        if not pid:
            res.advertencia(f"{nombre}: pregunta[{i}] sin 'pregunta_id'")
        else:
            if pid in ids_vistos:
                res.error(f"{nombre}: pregunta_id duplicado → '{pid}'")
            ids_vistos.add(str(pid))

        if not preg.get("pregunta"):
            res.advertencia(f"{nombre}: pregunta '{pid}' sin texto de pregunta")

        # Preguntas marcadas RESPONDIDA deben tener registro_respuesta
        estado = preg.get("estado", "")
        if isinstance(estado, str) and estado.upper().startswith("RESPONDIDA"):
            if not preg.get("registro_respuesta"):
                res.advertencia(
                    f"{nombre}: pregunta '{pid}' tiene estado '{estado}' "
                    f"pero no tiene campo 'registro_respuesta'"
                )


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida la integridad de los datos del proyecto histórico."
    )
    parser.add_argument(
        "--estricto",
        action="store_true",
        help="Falla con código 1 si hay advertencias (además de errores)",
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="Suprime la salida de advertencias; solo muestra errores",
    )
    args = parser.parse_args()

    res = Resultado()

    print(f"\n{'=' * 60}")
    print("   VALIDACIÓN DE DATOS — Hopelchén: 2000 años de historia")
    print(f"{'=' * 60}")
    print(f"📁 Directorio: {DATOS_HOPELCHEN}\n")

    # Validar nodos
    nodo_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))
    print(f"  📋 Nodos encontrados: {len(nodo_paths)}")
    for path in nodo_paths:
        validar_nodo(path, res)

    # Validar preguntas
    preguntas_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_PREGUNTAS_*.json"))
    print(f"  📋 Archivos de preguntas: {len(preguntas_paths)}")
    for path in preguntas_paths:
        validar_preguntas(path, res)

    # Filtrar advertencias si --silencioso
    if args.silencioso:
        res.advertencias.clear()

    res.imprimir()

    print()
    if res.errores:
        print(f"{'=' * 60}")
        print("  ❌  Validación FALLIDA — corrige los errores antes de generar.")
        print(f"{'=' * 60}\n")
        return 1

    if args.estricto and res.advertencias:
        print(f"{'=' * 60}")
        print("  ❌  Modo estricto: las advertencias se tratan como errores.")
        print(f"{'=' * 60}\n")
        return 1

    print(f"{'=' * 60}")
    print("  ✅  Validación exitosa.")
    print(f"{'=' * 60}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
