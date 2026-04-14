#!/usr/bin/env python3
"""
busqueda_semantica.py
=====================
Motor de búsqueda semántica para los datos históricos del proyecto.
Utiliza TF-IDF con similitud coseno para encontrar registros relevantes
a partir de una consulta en lenguaje natural.

No requiere servidor externo. Trabaja directamente sobre el índice local
(docs/search_index.json generado por generar_indice_busqueda.py).

Uso:
    python tools/busqueda_semantica.py "resistencia maya siglo XVIII"
    python tools/busqueda_semantica.py "tierra despojo hacendados" --top 10
    python tools/busqueda_semantica.py "agua territorio control" --nodo 007
    python tools/busqueda_semantica.py --interactivo

Dependencias:
    pip install scikit-learn
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
INDICE_DEFAULT = ROOT / "docs" / "search_index.json"

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False


# ─── Motor TF-IDF ────────────────────────────────────────────────────────────

class MotorBusqueda:
    """Motor de búsqueda semántica basado en TF-IDF + coseno."""

    def __init__(self, indice: list[dict]) -> None:
        if not SKLEARN_OK:
            raise ImportError(
                "scikit-learn es requerido para la búsqueda semántica.\n"
                "Instala con: pip install scikit-learn"
            )
        self._indice = indice
        self._textos = [e["texto_completo"] for e in indice]
        self._vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            max_features=20000,
            sublinear_tf=True,
            strip_accents=None,     # Preserva acentos del español
            token_pattern=r"(?u)\b\w+\b",
        )
        self._matriz = self._vectorizer.fit_transform(self._textos)

    def buscar(
        self,
        consulta: str,
        top_k: int = 5,
        nodo_filtro: Optional[str] = None,
        umbral: float = 0.01,
    ) -> list[tuple[float, dict]]:
        """
        Devuelve hasta top_k registros ordenados por relevancia.

        Args:
            consulta:     Texto de búsqueda en lenguaje natural.
            top_k:        Número máximo de resultados.
            nodo_filtro:  Si se indica (p.ej. "007"), filtra a ese nodo.
            umbral:       Similitud mínima para incluir un resultado.

        Returns:
            Lista de tuplas (score, registro_dict) ordenadas de mayor a menor.
        """
        vec_consulta = self._vectorizer.transform([consulta])
        scores = cosine_similarity(vec_consulta, self._matriz).flatten()

        # Aplicar filtro de nodo si corresponde
        if nodo_filtro:
            nodo_filtro_clean = nodo_filtro.lstrip("0") or "0"
            for i, entry in enumerate(self._indice):
                nid = str(entry.get("nodo_id", "")).lstrip("0") or "0"
                if nid != nodo_filtro_clean:
                    scores[i] = 0.0

        indices_ord = np.argsort(scores)[::-1]

        resultados: list[tuple[float, dict]] = []
        for idx in indices_ord:
            score = float(scores[idx])
            if score < umbral:
                break
            if len(resultados) >= top_k:
                break
            resultados.append((score, self._indice[idx]))
        return resultados


# ─── Carga del índice ─────────────────────────────────────────────────────────

def _cargar_indice(ruta: Path) -> list[dict]:
    if not ruta.exists():
        print(
            f"❌  Índice no encontrado: {ruta}\n"
            "   Genera el índice primero con:\n"
            "   python tools/generar_indice_busqueda.py",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# ─── Formateo de resultados ──────────────────────────────────────────────────

def _mostrar_resultado(rank: int, score: float, reg: dict) -> None:
    SEP = "─" * 60
    titulo_nodo = reg.get("titulo_nodo", "")
    print(f"\n{SEP}")
    print(f"  #{rank}  Score: {score:.4f}  │  ID: {reg['registro_id']}  │  Nodo {reg['nodo_id']}")
    print(f"  📅  {reg.get('fecha_evento', '—')}  │  📍 {reg.get('lugar', '—')}")
    if titulo_nodo:
        print(f"  📖  {titulo_nodo}")
    subtitulo = reg.get("subtitulo", "")
    if subtitulo:
        print(f"\n  {subtitulo}")
    descripcion = reg.get("descripcion", "")
    if descripcion:
        wrapped = textwrap.fill(descripcion, width=72, initial_indent="  ", subsequent_indent="  ")
        print(f"\n{wrapped}")
    conexion = reg.get("conexion_hipotesis", "")
    if conexion:
        wrapped = textwrap.fill(
            f"🔗  Hipótesis: {conexion}", width=72,
            initial_indent="  ", subsequent_indent="      ",
        )
        print(f"\n{wrapped}")
    fuente = reg.get("fuente", "")
    if fuente:
        fuente_corta = fuente[:120] + "…" if len(fuente) > 120 else fuente
        print(f"\n  📚  {fuente_corta}")
    tags = reg.get("tags", [])
    if tags:
        print(f"  🏷   {' · '.join(str(t) for t in tags[:8])}")


# ─── Modo interactivo ────────────────────────────────────────────────────────

def _modo_interactivo(motor: MotorBusqueda, top_k: int) -> None:
    print("\n🔍  Motor de búsqueda semántica — Hopelchén: 2000 años de historia")
    print("   Escribe una consulta en español (o 'salir' para terminar).\n")
    while True:
        try:
            consulta = input("Búsqueda > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if not consulta:
            continue
        if consulta.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break

        nodo = None
        if consulta.lower().startswith("nodo:"):
            partes = consulta.split(None, 1)
            if len(partes) == 2:
                nodo = partes[0].split(":")[1]
                consulta = partes[1]

        resultados = motor.buscar(consulta, top_k=top_k, nodo_filtro=nodo)
        if not resultados:
            print("  Sin resultados relevantes para esta consulta.\n")
            continue
        print(f"\n  {len(resultados)} resultado(s) encontrado(s):")
        for i, (score, reg) in enumerate(resultados, 1):
            _mostrar_resultado(i, score, reg)
        print(f"\n{'─' * 60}\n")


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Búsqueda semántica en datos históricos de Hopelchén.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Ejemplos:
              python tools/busqueda_semantica.py "resistencia maya Caste War"
              python tools/busqueda_semantica.py "tierra despojo chicle" --top 8
              python tools/busqueda_semantica.py "rutas caminos" --nodo 007
              python tools/busqueda_semantica.py --interactivo
        """),
    )
    parser.add_argument("consulta", nargs="?", help="Texto de búsqueda")
    parser.add_argument(
        "--top", type=int, default=5,
        help="Número máximo de resultados (default: 5)",
    )
    parser.add_argument(
        "--nodo", default=None,
        help="Filtrar resultados a un nodo específico (p.ej. 007)",
    )
    parser.add_argument(
        "--indice", default=str(INDICE_DEFAULT),
        help="Ruta al archivo search_index.json",
    )
    parser.add_argument(
        "--interactivo", action="store_true",
        help="Modo interactivo: ingresa consultas una por una",
    )
    parser.add_argument(
        "--umbral", type=float, default=0.01,
        help="Similitud mínima (0–1) para incluir resultados (default: 0.01)",
    )
    args = parser.parse_args()

    if not SKLEARN_OK:
        print(
            "❌  scikit-learn no está instalado.\n"
            "   Instala con: pip install scikit-learn",
            file=sys.stderr,
        )
        return 1

    indice = _cargar_indice(Path(args.indice))
    motor = MotorBusqueda(indice)

    print(f"✅  Índice cargado: {len(indice)} registros")

    if args.interactivo:
        _modo_interactivo(motor, top_k=args.top)
        return 0

    if not args.consulta:
        parser.print_help()
        return 1

    resultados = motor.buscar(
        args.consulta,
        top_k=args.top,
        nodo_filtro=args.nodo,
        umbral=args.umbral,
    )

    if not resultados:
        print(f"\n  Sin resultados relevantes para: '{args.consulta}'")
        return 0

    print(f"\n🔍  Consulta: '{args.consulta}'")
    if args.nodo:
        print(f"   Filtro: Nodo {args.nodo}")
    print(f"   {len(resultados)} resultado(s) encontrado(s):\n")
    for i, (score, reg) in enumerate(resultados, 1):
        _mostrar_resultado(i, score, reg)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
