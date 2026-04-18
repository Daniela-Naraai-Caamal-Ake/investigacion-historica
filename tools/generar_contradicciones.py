#!/usr/bin/env python3
"""
generar_contradicciones.py
==========================
Genera analisis/contradicciones.md — un consolidado de todas las tensiones
y contradicciones detectadas entre fuentes a través de los 10 nodos.

Extrae el campo `notas_contradiccion` de cada registro y los organiza por
tipo de tensión: factual, interpretativa, de silencio o de versión.

Uso:
    python tools/generar_contradicciones.py
"""

from __future__ import annotations
import json
import glob
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
NODOS_DIR = ROOT / "datos" / "hopelchen"
SALIDA = ROOT / "analisis" / "contradicciones.md"

TITULOS_NODOS = {
    "001": "Prehispánico (~1000 a.C.–1517)",
    "002": "Conquista Colonial (1517–1669)",
    "003": "Colonia Tardía–Porfiriato (1670–1910)",
    "004": "Revolución–Chicle (1910–1970)",
    "005": "Contemporáneo (1970–2026)",
    "006": "Poder Político Local (1959–2026)",
    "007": "Rutas y Territorio (1517–2026)",
    "008": "Demografía (300 a.C.–2026)",
    "009": "Resistencia Maya (1669–2026)",
    "010": "Conocimiento y Cultura (300 a.C.–2026)",
}

# Palabras clave para clasificar el tipo de contradicción
TIPOS = {
    "factual": [
        "contradicción", "contradicción detectada", "desfase", "discrepancia",
        "error", "incorrecto", "distinto", "diferente", "no coincide",
        "cifra", "fecha", "dato", "actualización",
    ],
    "interpretativa": [
        "perspectiva", "interpretación", "versión", "enfoque", "ángulo",
        "punto de vista", "lectura", "relato", "narrativa", "discurso",
        "cuestiona", "debate",
    ],
    "de_fuente": [
        "fuente", "requiere verificación", "pendiente", "sin fuente primaria",
        "no confirmado", "verificar", "acceso directo", "consultar",
        "fuente secundaria", "no digitalizado",
    ],
    "de_silencio": [
        "silencio", "ausencia", "no aparece", "ningún", "no se menciona",
        "omitido", "borrado", "invisibilizado", "no está", "no existe",
        "nadie", "no hay registro",
    ],
}


def clasificar(texto: str) -> str:
    texto_lower = texto.lower()
    puntajes = {tipo: 0 for tipo in TIPOS}
    for tipo, palabras in TIPOS.items():
        for p in palabras:
            if p in texto_lower:
                puntajes[tipo] += 1
    mejor = max(puntajes, key=puntajes.get)
    return mejor if puntajes[mejor] > 0 else "factual"


def cargar_contradicciones() -> list[dict]:
    registros = []
    for path in sorted(glob.glob(str(NODOS_DIR / "HOPELCHEN_NODO_*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        nodo = data["nodo_id"]
        for r in data.get("registros", []):
            nota = r.get("notas_contradiccion", "").strip()
            if not nota or len(nota) < 30:
                continue
            registros.append({
                "nodo": nodo,
                "titulo_nodo": TITULOS_NODOS.get(nodo, nodo),
                "registro_id": r["registro_id"],
                "subtitulo": r.get("subtitulo", "")[:90],
                "fecha": r.get("fecha_evento", ""),
                "tipo": clasificar(nota),
                "nota": nota,
                "tipo_dato": r.get("tipo_dato", ""),
            })
    return registros


def generar_md(registros: list[dict]) -> str:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Agrupar por tipo
    por_tipo: dict[str, list] = {}
    for r in registros:
        por_tipo.setdefault(r["tipo"], []).append(r)

    # Agrupar por nodo
    por_nodo: dict[str, list] = {}
    for r in registros:
        por_nodo.setdefault(r["nodo"], []).append(r)

    etiquetas = {
        "factual": "Contradicciones factuales",
        "interpretativa": "Tensiones interpretativas",
        "de_fuente": "Problemas de fuente o verificación",
        "de_silencio": "Silencios y ausencias detectadas",
    }

    lineas = [
        "# Contradicciones y tensiones entre fuentes",
        "",
        "> Autora: Daniela Naraai Caamal Ake  ",
        f"> Generado: {ahora}  ",
        "> ⚙ Generado por `tools/generar_contradicciones.py`",
        "",
        "Este archivo consolida todas las tensiones detectadas entre fuentes",
        "a lo largo de los 10 nodos del sistema. No son errores a corregir:",
        "son la evidencia de que el territorio tiene múltiples narrativas que",
        "coexisten sin resolverse. Cada tensión es una entrada analítica.",
        "",
        f"**Total de tensiones registradas:** {len(registros)}",
        "",
        "---",
        "",
        "## Resumen por tipo",
        "",
        "| Tipo | Cantidad | Descripción |",
        "|---|---|---|",
        f"| Factual | {len(por_tipo.get('factual',[]))} | Datos numéricos, fechas o hechos que difieren entre fuentes |",
        f"| Interpretativa | {len(por_tipo.get('interpretativa',[]))} | Lecturas o versiones distintas sobre el mismo evento |",
        f"| De fuente | {len(por_tipo.get('de_fuente',[]))} | Registros que requieren verificación primaria pendiente |",
        f"| De silencio | {len(por_tipo.get('de_silencio',[]))} | Ausencias o borramientos detectados en el archivo histórico |",
        "",
        "---",
        "",
        "## Resumen por nodo",
        "",
        "| Nodo | Título | Tensiones |",
        "|---|---|---|",
    ]

    for nodo in sorted(por_nodo.keys()):
        n = len(por_nodo[nodo])
        titulo = TITULOS_NODOS.get(nodo, nodo)
        lineas.append(f"| {nodo} | {titulo} | {n} |")

    lineas += ["", "---", ""]

    # Secciones por tipo
    for tipo in ["factual", "interpretativa", "de_fuente", "de_silencio"]:
        refs = por_tipo.get(tipo, [])
        if not refs:
            continue

        lineas += [
            f"## {etiquetas[tipo]} ({len(refs)})",
            "",
        ]

        # Agrupar por nodo dentro del tipo
        por_nodo_tipo: dict[str, list] = {}
        for r in refs:
            por_nodo_tipo.setdefault(r["nodo"], []).append(r)

        for nodo in sorted(por_nodo_tipo.keys()):
            titulo_n = TITULOS_NODOS.get(nodo, nodo)
            lineas += [f"### Nodo {nodo} — {titulo_n}", ""]

            for r in por_nodo_tipo[nodo]:
                fecha = f" ({r['fecha']})" if r.get("fecha") else ""
                lineas += [
                    f"**[{r['registro_id']}]{fecha}** — {r['subtitulo']}",
                    "",
                    f"> {r['nota']}",
                    "",
                ]

        lineas.append("---")
        lineas.append("")

    lineas += [
        "*Las tensiones aquí registradas provienen del campo `notas_contradiccion`*",
        "*de cada registro. Son declaradas por la investigadora, no generadas automáticamente.*",
        "*Su función es hacer visibles las fricciones entre narrativas, no resolverlas.*",
    ]

    return "\n".join(lineas)


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    registros = cargar_contradicciones()
    contenido = generar_md(registros)
    SALIDA.write_text(contenido, encoding="utf-8")
    print(
        f"[generar_contradicciones] ✅ Escrito: {SALIDA} "
        f"({len(registros)} tensiones registradas)"
    )


if __name__ == "__main__":
    main()
