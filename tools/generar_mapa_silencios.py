#!/usr/bin/env python3
"""
generar_mapa_silencios.py
=========================
Genera analisis/mapa_silencios.md — un análisis de ausencias estructurales
en el archivo histórico disponible sobre Hopelchén.

Los silencios son distintos de los vacíos (VACIOS.md):
- VACÍOS = preguntas sin respuesta todavía (técnico, resoluble con investigación)
- SILENCIOS = ausencias deliberadas o estructurales en las fuentes mismas
  (epistemológico, dice algo sobre cómo se produce el conocimiento histórico)

Tipos de silencio que este script detecta:
1. Actores sin fuente primaria (solo mencionados en secundarias)
2. Períodos sin registros
3. Voces ausentes (quién nunca es fuente, solo objeto)
4. Temas tabú (presentes en conexion_hipotesis pero sin registros propios)

Uso:
    python tools/generar_mapa_silencios.py
"""

from __future__ import annotations
import json
import glob
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
NODOS_DIR = ROOT / "datos" / "hopelchen"
SALIDA = ROOT / "analisis" / "mapa_silencios.md"

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

# Voces que deberían existir pero raramente son fuentes primarias en historia colonial
VOCES_ESPERADAS_AUSENTES = [
    "comunidades mayas", "mujeres mayas", "trabajadores chicleros",
    "ejidatarios", "bataboob", "memoria oral", "testimonios locales",
    "apicultores", "milperos",
]

# Temas que la hipótesis señala como centrales — ¿tienen registros?
TEMAS_HIPOTESIS = [
    "tierra", "despojo", "silencio", "resistencia", "poder", "control",
    "linaje", "apellido", "extracción", "autonomía",
]


def cargar_nodos() -> list[dict]:
    nodos = []
    for path in sorted(glob.glob(str(NODOS_DIR / "HOPELCHEN_NODO_*.json"))):
        with open(path, encoding="utf-8") as f:
            nodos.append(json.load(f))
    return nodos


def analizar_tipo_fuente(nodos: list[dict]) -> dict:
    """Clasifica registros según si tienen fuente primaria, secundaria o ninguna."""
    resultado = {
        "con_fuente_primaria": [],
        "solo_secundaria": [],
        "inferidos": [],
    }
    for data in nodos:
        nodo = data["nodo_id"]
        for r in data.get("registros", []):
            rid = r["registro_id"]
            tipo = r.get("tipo_dato", "").lower()
            tiene_primaria = (
                "primaria" in tipo or
                "archivo" in tipo or
                "epigráfico" in tipo or
                "arqueológico" in tipo or
                "acta" in tipo.lower() or
                "documento" in tipo.lower()
            )
            es_inferido = "inferido" in tipo or "estimado" in tipo
            info = {
                "nodo": nodo,
                "titulo_nodo": TITULOS_NODOS.get(nodo, nodo),
                "registro_id": rid,
                "subtitulo": r.get("subtitulo", "")[:80],
                "tipo_dato": r.get("tipo_dato", ""),
            }
            if es_inferido:
                resultado["inferidos"].append(info)
            elif tiene_primaria:
                resultado["con_fuente_primaria"].append(info)
            else:
                resultado["solo_secundaria"].append(info)
    return resultado


def detectar_voces_ausentes(nodos: list[dict]) -> list[dict]:
    """Detecta qué voces son objeto de estudio pero nunca son fuente."""
    voces_como_fuente = set()
    voces_como_objeto = set()

    for data in nodos:
        for r in data.get("registros", []):
            desc = r.get("descripcion", "").lower()
            fuente_str = json.dumps(
                r.get("fuente", {}) or r.get("fuente_academica", "") or ""
            ).lower()

            for voz in VOCES_ESPERADAS_AUSENTES:
                if voz.lower() in desc or voz.lower() in fuente_str:
                    voces_como_objeto.add(voz)
                if voz.lower() in fuente_str and (
                    "testimonio" in fuente_str or
                    "oral" in fuente_str or
                    "entrevista" in fuente_str
                ):
                    voces_como_fuente.add(voz)

    return [
        {"voz": v, "aparece_como_objeto": v in voces_como_objeto,
         "aparece_como_fuente": v in voces_como_fuente}
        for v in VOCES_ESPERADAS_AUSENTES
    ]


def detectar_periodos_sin_registros(nodos: list[dict]) -> list[dict]:
    """Detecta si hay períodos históricos sin ningún registro."""
    periodos_definidos = [
        ("Preclásico Medio", -1000, -300),
        ("Preclásico Tardío", -300, 0),
        ("Clásico", 0, 900),
        ("Posclásico", 900, 1521),
        ("Siglo XVI", 1521, 1600),
        ("Siglo XVII", 1600, 1700),
        ("Siglo XVIII", 1700, 1810),
        ("Independencia–Guerra Castas", 1810, 1860),
        ("Reforma–Porfiriato", 1860, 1910),
        ("Revolución", 1910, 1940),
        ("Posrevolución–Chicle", 1940, 1970),
        ("1970–2000", 1970, 2000),
        ("2000–2026", 2000, 2026),
    ]

    # Recopilar años de todos los registros
    años_cubiertos: list[int] = []
    for data in nodos:
        for r in data.get("registros", []):
            fe = r.get("fecha_evento", "")
            import re
            # Extraer años del campo fecha_evento
            nums = re.findall(r'\b(\d{3,4})\b', fe)
            for n in nums:
                año = int(n)
                if -2000 < año < 2030:
                    años_cubiertos.append(año)
            # Años negativos (a.C.)
            neg = re.findall(r'(\d+)\s*a\.?\s*C', fe)
            for n in neg:
                años_cubiertos.append(-int(n))

    resultado = []
    for nombre, inicio, fin in periodos_definidos:
        tiene_registros = any(inicio <= a <= fin for a in años_cubiertos)
        resultado.append({
            "periodo": nombre,
            "inicio": inicio,
            "fin": fin,
            "cubierto": tiene_registros,
        })
    return resultado


def generar_md(nodos: list[dict]) -> str:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    tipos_fuente = analizar_tipo_fuente(nodos)
    voces = detectar_voces_ausentes(nodos)
    periodos = detectar_periodos_sin_registros(nodos)

    total_registros = sum(len(d.get("registros", [])) for d in nodos)
    n_inferidos = len(tipos_fuente["inferidos"])
    n_solo_sec = len(tipos_fuente["solo_secundaria"])
    n_primaria = len(tipos_fuente["con_fuente_primaria"])

    lineas = [
        "# Mapa de silencios — *Dos Mil Años en Silencio*",
        "",
        "> Autora: Daniela Naraai Caamal Ake  ",
        f"> Generado: {ahora}  ",
        "> ⚙ Generado por `tools/generar_mapa_silencios.py`",
        "",
        "Este archivo documenta las **ausencias estructurales** del archivo histórico",
        "disponible sobre Hopelchén. Es distinto de `datos/VACIOS.md`:",
        "",
        "- **VACÍOS** → preguntas sin respuesta todavía (resoluble con investigación)",
        "- **SILENCIOS** → ausencias en las fuentes mismas (dice algo sobre *quién*",
        "  produce el conocimiento histórico y *qué* considera digno de registrar)",
        "",
        "Un silencio no es un error del sistema. Es un dato sobre el sistema.",
        "",
        "---",
        "",
        "## 1. Estructura de fuentes — quién habla en el archivo",
        "",
        f"De {total_registros} registros totales:",
        "",
        "| Tipo | Cantidad | % | Qué significa |",
        "|---|---|---|---|",
        f"| Con fuente primaria | {n_primaria} | {n_primaria*100//total_registros}% | Documento original, excavación, epigrafía |",
        f"| Solo fuente secundaria | {n_solo_sec} | {n_solo_sec*100//total_registros}% | Alguien más ya interpretó la fuente original |",
        f"| Inferido o estimado | {n_inferidos} | {n_inferidos*100//total_registros}% | No hay fuente directa — es análisis razonado |",
        "",
        "> **Lectura:** El porcentaje de registros sin fuente primaria directa no es",
        "> solo un problema técnico — refleja que gran parte de la historia de Hopelchén",
        "> llega mediada por investigadores externos que ya eligieron qué preservar.",
        "",
        "### Registros inferidos o estimados (sin fuente primaria)",
        "",
        "| Registro | Nodo | Subtítulo | Tipo de dato |",
        "|---|---|---|---|",
    ]

    for r in tipos_fuente["inferidos"]:
        lineas.append(
            f"| {r['registro_id']} | {r['nodo']} {r['titulo_nodo']} "
            f"| {r['subtitulo']} | {r['tipo_dato'][:50]} |"
        )

    lineas += [
        "",
        "---",
        "",
        "## 2. Voces ausentes — quién no es fuente",
        "",
        "Actores que aparecen como *objeto* de estudio en los registros pero",
        "raramente o nunca como *productores* de la fuente consultada.",
        "",
        "| Voz | Aparece como objeto | Aparece como fuente | Silencio |",
        "|---|---|---|---|",
    ]

    for v in voces:
        como_objeto = "✅" if v["aparece_como_objeto"] else "—"
        como_fuente = "✅" if v["aparece_como_fuente"] else "—"
        silencio = "🔴 Silenciada" if (v["aparece_como_objeto"] and not v["aparece_como_fuente"]) else (
            "🟡 Parcial" if v["aparece_como_fuente"] else "🔲 No detectada"
        )
        lineas.append(
            f"| {v['voz']} | {como_objeto} | {como_fuente} | {silencio} |"
        )

    lineas += [
        "",
        "> **Lectura:** Una voz 'silenciada' no significa que esas personas no",
        "> dejaron rastro — significa que los sistemas de archivo disponibles no",
        "> los preservaron como productores de conocimiento, solo como objeto de él.",
        "",
        "---",
        "",
        "## 3. Períodos históricos — cobertura temporal",
        "",
        "Qué tan bien cubiertos están los distintos períodos históricos",
        "en el sistema de registros actual.",
        "",
        "| Período | Años | Cubierto |",
        "|---|---|---|",
    ]

    for p in periodos:
        inicio = f"{abs(p['inicio'])} a.C." if p["inicio"] < 0 else str(p["inicio"])
        fin = str(p["fin"])
        estado = "✅ Sí" if p["cubierto"] else "🔴 Sin registros"
        lineas.append(f"| {p['periodo']} | {inicio}–{fin} | {estado} |")

    lineas += [
        "",
        "---",
        "",
        "## 4. Silencios temáticos — lo que la hipótesis señala pero el archivo no registra",
        "",
        "La hipótesis central del proyecto propone que el control del territorio,",
        "el conocimiento y el poder político ha operado mediante mecanismos que",
        "se renuevan. Estos son los temas que la hipótesis señala como centrales",
        "y el nivel de documentación directa que tiene cada uno:",
        "",
        "| Tema | Presente en nodos | Observación |",
        "|---|---|---|",
    ]

    # Calcular presencia de temas en nodos
    for tema in TEMAS_HIPOTESIS:
        nodos_con_tema = []
        for data in nodos:
            nodo = data["nodo_id"]
            for r in data.get("registros", []):
                ch = r.get("conexion_hipotesis", "").lower()
                desc = r.get("descripcion", "").lower()
                tags = [t.lower() for t in r.get("tags", [])]
                if tema.lower() in ch or tema.lower() in desc or tema.lower() in tags:
                    if nodo not in nodos_con_tema:
                        nodos_con_tema.append(nodo)
        cobertura = len(nodos_con_tema)
        if cobertura >= 7:
            obs = "Bien documentado transversalmente"
        elif cobertura >= 4:
            obs = "Documentación parcial — gaps en algunos períodos"
        elif cobertura >= 1:
            obs = "⚠ Documentación débil — merece más registros"
        else:
            obs = "🔴 Ausente del archivo — silencio total"
        nodos_str = ", ".join(nodos_con_tema) if nodos_con_tema else "ninguno"
        lineas.append(f"| **{tema}** | {nodos_str} ({cobertura}/10) | {obs} |")

    lineas += [
        "",
        "---",
        "",
        "## 5. Conclusión provisional",
        "",
        "Los silencios más estructurales detectados en este sistema son:",
        "",
        "1. **La voz maya como fuente** — las comunidades mayas aparecen como objeto",
        "   de estudio en casi todos los nodos, pero raramente como productoras de",
        "   las fuentes consultadas. La excepción más clara es el caso Leydy Pech",
        "   (nodos 005 y 009), donde la comunidad produce documentación jurídica propia.",
        "",
        "2. **El siglo XVIII** — el período de llegada de las 'familias de abolengo'",
        "   (1700-1810) está documentado principalmente en fuentes criollas que",
        "   describen ese proceso como 'acrecentamiento de la población'. Las fuentes",
        "   que registrarían la perspectiva maya de ese mismo proceso no se han",
        "   encontrado en los archivos digitalizados disponibles.",
        "",
        "3. **La memoria oral** — ningún registro del sistema tiene como fuente",
        "   primaria un testimonio oral recogido directamente. Todo lo que se sabe",
        "   sobre la experiencia vivida en Hopelchén viene mediado por académicos",
        "   externos (principalmente Schüren, FU Berlin, 2002).",
        "",
        "*Este mapa se actualiza cada vez que se corre el script.*",
        "*Los silencios que aquí aparecen son provisionales — algunos pueden resolverse*",
        "*con acceso a archivos primarios (AGI, AGEY, AGEC, Archivo Municipal de Hopelchén).*",
    ]

    return "\n".join(lineas)


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    nodos = cargar_nodos()
    contenido = generar_md(nodos)
    SALIDA.write_text(contenido, encoding="utf-8")
    print(f"[generar_mapa_silencios] ✅ Escrito: {SALIDA}")


if __name__ == "__main__":
    main()
