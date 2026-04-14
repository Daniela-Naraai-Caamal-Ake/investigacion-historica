#!/usr/bin/env python3
"""
validar_fechas.py
=================
Valida la consistencia temporal de los registros históricos del proyecto.

Verificaciones realizadas:
    - Los registros tienen campo 'fecha_evento' presente
    - Los rangos temporales de cada nodo son coherentes con sus registros
    - No hay fechas futuras en los datos (más allá del año actual)
    - Los rangos invertidos (inicio > fin) se detectan y reportan
    - Los rango_temporal del nodo contienen texto de rango reconocible

Uso:
    python tools/validar_fechas.py
    python tools/validar_fechas.py --estricto
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS_HOPELCHEN = ROOT / "datos" / "hopelchen"

AÑO_MAX = datetime.now().year + 1   # Tolerancia de un año futuro

# Patrones para extraer años de cadenas de texto históricas.
# Se intentan en orden; se usa el primer patrón que empareje.
_PATRON_AÑO_NEGATIVO = re.compile(r"(\d{1,4})\s*a\.C\.", re.IGNORECASE)
# Matches 3- or 4-digit years (standalone, or followed by d.C.)
_PATRON_AÑO_POSITIVO = re.compile(r"\b(\d{3,4})\b")


def _extraer_años(texto: str) -> list[int]:
    """
    Extrae todos los valores numéricos de año de un texto libre.

    Los años a.C. se devuelven como valores negativos.
    Los años d.C. o sin indicador se devuelven como positivos.
    Retorna lista vacía si no hay números reconocibles.
    """
    if not isinstance(texto, str) or not texto.strip():
        return []

    años: list[int] = []

    # Busca pares "NNN a.C." → negativo
    for m in _PATRON_AÑO_NEGATIVO.finditer(texto):
        años.append(-int(m.group(1)))

    # Busca cuatro dígitos consecutivos que no estén seguidos de " a.C."
    for m in _PATRON_AÑO_POSITIVO.finditer(texto):
        inicio = m.start()
        fragmento_siguiente = texto[m.end(): m.end() + 6]
        if re.match(r"\s*a\.C\.", fragmento_siguiente, re.IGNORECASE):
            continue  # ya procesado como negativo
        año = int(m.group(1))
        años.append(año)

    return años


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
            print(f"  ❌  {len(self.errores)} ERROR(ES) de fecha encontrado(s):")
            for e in self.errores:
                print(f"     • {e}")
        if self.advertencias:
            print(f"\n{'─' * 60}")
            print(f"  ⚠   {len(self.advertencias)} ADVERTENCIA(S) de fecha:")
            for a in self.advertencias:
                print(f"     • {a}")
        if not self.errores and not self.advertencias:
            print("  ✅  Sin problemas de fecha encontrados.")


def validar_nodo_fechas(path: Path, res: Resultado, estricto: bool) -> None:
    nombre = path.name

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        res.error(f"{nombre}: no se pudo leer — {exc}")
        return

    nodo_id = data.get("nodo_id", nombre)
    rango_temporal = data.get("rango_temporal", "")

    # Extraer años del rango_temporal del nodo
    años_rango = _extraer_años(rango_temporal)
    año_min_nodo = min(años_rango) if años_rango else None
    año_max_nodo = max(años_rango) if años_rango else None

    if not rango_temporal:
        res.advertencia(f"{nombre} (nodo {nodo_id}): campo 'rango_temporal' vacío")
    elif not años_rango:
        res.advertencia(
            f"{nombre} (nodo {nodo_id}): 'rango_temporal' sin años reconocibles "
            f"→ '{rango_temporal}'"
        )

    registros = data.get("registros", [])
    for reg in registros:
        if not isinstance(reg, dict):
            continue

        rid = reg.get("registro_id", "?")
        fecha = reg.get("fecha_evento", "")

        if not fecha or not str(fecha).strip():
            if estricto:
                res.error(
                    f"{nombre} (nodo {nodo_id}): registro '{rid}' sin 'fecha_evento'"
                )
            else:
                res.advertencia(
                    f"{nombre} (nodo {nodo_id}): registro '{rid}' sin 'fecha_evento'"
                )
            continue

        años_reg = _extraer_años(str(fecha))
        if not años_reg:
            # Podría ser texto puramente cualitativo ("siglo XVII")
            res.advertencia(
                f"{nombre} (nodo {nodo_id}): registro '{rid}' — "
                f"fecha sin años numéricos reconocibles → '{fecha}'"
            )
            continue

        año_min_reg = min(años_reg)
        año_max_reg = max(años_reg)

        # Detectar años futuros
        for año in años_reg:
            if año > AÑO_MAX:
                res.error(
                    f"{nombre} (nodo {nodo_id}): registro '{rid}' — "
                    f"año futuro detectado ({año}) en fecha '{fecha}'"
                )

        # Detectar rango invertido en el propio registro (solo cuando hay 2+ años)
        if len(años_reg) >= 2 and año_min_reg > año_max_reg:
            res.error(
                f"{nombre} (nodo {nodo_id}): registro '{rid}' — "
                f"rango temporal invertido en '{fecha}'"
            )

        # Verificar coherencia con rango_temporal del nodo (holgura ±50 años)
        HOLGURA = 50
        if año_min_nodo is not None and año_min_reg < año_min_nodo - HOLGURA:
            res.advertencia(
                f"{nombre} (nodo {nodo_id}): registro '{rid}' — "
                f"año {año_min_reg} es anterior al inicio del nodo "
                f"({año_min_nodo}) con holgura de {HOLGURA} años"
            )
        if año_max_nodo is not None and año_max_reg > año_max_nodo + HOLGURA:
            res.advertencia(
                f"{nombre} (nodo {nodo_id}): registro '{rid}' — "
                f"año {año_max_reg} es posterior al fin del nodo "
                f"({año_max_nodo}) con holgura de {HOLGURA} años"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida la consistencia temporal de los datos históricos."
    )
    parser.add_argument(
        "--estricto",
        action="store_true",
        help="Falla con código 1 si hay advertencias",
    )
    args = parser.parse_args()

    res = Resultado()

    print(f"\n{'=' * 60}")
    print("   VALIDACIÓN DE FECHAS — Hopelchén: 2000 años de historia")
    print(f"{'=' * 60}")
    print(f"📁 Directorio: {DATOS_HOPELCHEN}\n")

    nodo_paths = sorted(DATOS_HOPELCHEN.glob("HOPELCHEN_NODO_*.json"))
    print(f"  📋 Nodos a validar: {len(nodo_paths)}")
    for path in nodo_paths:
        validar_nodo_fechas(path, res, estricto=args.estricto)

    res.imprimir()

    print()
    if res.errores:
        print(f"{'=' * 60}")
        print("  ❌  Validación FALLIDA — revisa los errores de fecha.")
        print(f"{'=' * 60}\n")
        return 1

    if args.estricto and res.advertencias:
        print(f"{'=' * 60}")
        print("  ❌  Modo estricto: las advertencias se tratan como errores.")
        print(f"{'=' * 60}\n")
        return 1

    print(f"{'=' * 60}")
    print("  ✅  Validación de fechas exitosa.")
    print(f"{'=' * 60}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
