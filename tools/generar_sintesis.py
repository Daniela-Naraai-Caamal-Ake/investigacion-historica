#!/usr/bin/env python3
"""
generar_sintesis.py
===================
Genera SINTESIS_MAESTRA.md consolidando TODA la información del proyecto:

  - Hipótesis central
  - Los 10 nodos con sus registros
  - Cronología maestra de todos los eventos
  - Personajes clave (árboles genealógicos)
  - Mapa de vacíos / preguntas (por prioridad)
  - Catálogo de fuentes

Uso:
    python tools/generar_sintesis.py
    python tools/generar_sintesis.py --salida docs/SINTESIS_MAESTRA.md
"""

import argparse
import glob
import json
import os
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "datos"
HOPELCHEN = DATOS / "hopelchen"
ARCHIVO_VIVO = DATOS / "archivo_vivo"
FUENTES = ROOT / "fuentes"
TRABAJO = ROOT / "trabajo"
SALIDA_DEFAULT = ROOT / "SINTESIS_MAESTRA.md"

# ── helpers ──────────────────────────────────────────────────────────────────

def _cargar_json(ruta: Path) -> dict | list | None:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return None


def _estado_emoji(estado: str) -> str:
    if "RESPONDIDA PARCIALMENTE" in estado:
        return "🟠"
    if "RESPONDIDA" in estado:
        return "🟢"
    if "EN PROCESO" in estado:
        return "🟡"
    if "PENDIENTE" in estado:
        return "🔴"
    return "⚪"


# ── secciones ────────────────────────────────────────────────────────────────

def _seccion_cabecera(fecha: str) -> str:
    return f"""# SÍNTESIS MAESTRA — Hopelchén: 2000 años de historia

> **Dos Mil Años en Silencio** — Investigación histórica sobre Hopelchén y Los Chenes  
> Autora: **Daniela Naraai Caamal Ake**  
> ⚙ Generado automáticamente por `tools/generar_sintesis.py`  
> Última actualización: **{fecha}**

---

## Cómo usar este documento

Este archivo es la **capa de síntesis** del proyecto. Está organizado en capas
de acceso progresivo. Para navegar:

| Capa | Archivo | Descripción |
|------|---------|-------------|
| **Capa 0** | `README.md` | Descripción general y guía de inicio |
| **Capa 1** | **`SINTESIS_MAESTRA.md`** ← (este archivo) | Síntesis completa: todo en un lugar |
| **Capa 2** | `trabajo/periodos/nodo-*.md` | Redacción detallada por período |
| **Capa 3** | `datos/VACIOS.md` | Preguntas abiertas por prioridad |
| **Capa 4** | `fuentes/catalogo_fuentes.md` | Catálogo bibliográfico completo |
| **Capa 5** | `datos/archivo_vivo/AV_PERSONAS.md` | Genealogías y personajes |

---
"""


def _seccion_hipotesis() -> str:
    hipotesis_file = ROOT / "HIPOTESIS.md"
    if hipotesis_file.exists():
        content = hipotesis_file.read_text(encoding="utf-8")
        # Bajar todos los headers un nivel para que queden dentro de H2
        # H1 (#) → H3 (###), H2 (##) → H3 (###), H3+ sin cambio
        lines = content.splitlines()[:120]
        adjusted = []
        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                adjusted.append("### " + line[2:])
            elif line.startswith("## "):
                adjusted.append("### " + line[3:])
            else:
                adjusted.append(line)
        return "## 1. Hipótesis Central\n\n" + "\n".join(adjusted) + "\n\n---\n"

    return """## 1. Hipótesis Central

El control del territorio, del cuerpo y del conocimiento en Hopelchén ha sido
ejercido por grupos de poder que se renuevan en cada era, pero mantienen el
mismo patrón extractivo: conquistadores coloniales → hacendados porfirianos
→ chicleros norteamericanos → menonitas + agroindustria transgénica.

La resistencia maya es una constante, no una excepción.

---
"""


def _seccion_estructura_libro() -> str:
    lines = [
        "## 2. Estructura del Libro (10 Nodos Temáticos)\n",
        "El libro está organizado en 10 nodos que combinan cronología y temática:\n",
        "| Nodo | Período | Título | Registros |",
        "|------|---------|--------|-----------|",
    ]
    for f in sorted(HOPELCHEN.glob("HOPELCHEN_NODO_*.json")):
        d = _cargar_json(f)
        if not d:
            continue
        nodo_id = d.get("nodo_id", "?")
        titulo = d.get("titulo", "")[:65]
        rango = d.get("rango_temporal", "")
        n_regs = len(d.get("registros", []))
        lines.append(f"| **{nodo_id}** | {rango} | {titulo}… | {n_regs} |")
    lines.append("\n---\n")
    return "\n".join(lines)


def _seccion_registros() -> str:
    lines = ["## 3. Registros por Nodo — Lo que se sabe\n"]
    for f in sorted(HOPELCHEN.glob("HOPELCHEN_NODO_*.json")):
        d = _cargar_json(f)
        if not d:
            continue
        nodo_id = d.get("nodo_id", "?")
        titulo = d.get("titulo", "")
        rango = d.get("rango_temporal", "")
        hipotesis = d.get("hipotesis_marco", "")[:200]
        registros = d.get("registros", [])

        lines.append(f"### Nodo {nodo_id} — {titulo}")
        lines.append(f"**Período:** {rango}  ")
        lines.append(f"**Hipótesis:** {hipotesis}…\n")
        lines.append("| ID | Fecha | Subtítulo | Fuente |")
        lines.append("|----|-------|-----------|--------|")

        for r in registros:
            rid = r.get("registro_id", "")
            fecha = str(r.get("fecha_evento", ""))[:30]
            sub = r.get("subtitulo", "")[:60]
            fuente_raw = r.get("fuente", {})
            if isinstance(fuente_raw, dict):
                fuente = fuente_raw.get("nombre", fuente_raw.get("url", ""))[:50]
            else:
                fuente = str(fuente_raw)[:50]
            has_source = "✅" if fuente.strip() else "❌"
            lines.append(f"| `{rid}` | {fecha} | {sub}… | {has_source} {fuente} |")

        lines.append("")

        # Hallazgo crítico si existe
        hallazgo = d.get("HALLAZGO_CRITICO_NUEVO") or d.get("hallazgo_critico", "")
        if hallazgo:
            if isinstance(hallazgo, dict):
                hallazgo = str(hallazgo)
            lines.append(f"> 🔑 **Hallazgo crítico:** {str(hallazgo)[:200]}\n")

        lines.append("---\n")

    return "\n".join(lines)


def _seccion_cronologia() -> str:
    """Construye cronología maestra desde todos los nodos."""
    lines = ["## 4. Cronología Maestra\n",
             "Todos los eventos documentados, ordenados cronológicamente.\n",
             "| Fecha | Evento | Nodo |",
             "|-------|--------|------|"]

    events: list[tuple] = []
    for f in sorted(HOPELCHEN.glob("HOPELCHEN_NODO_*.json")):
        d = _cargar_json(f)
        if not d:
            continue
        nodo_id = d.get("nodo_id", "?")
        for r in d.get("registros", []):
            fecha = str(r.get("fecha_evento", "")).strip()
            sub = r.get("subtitulo", "")[:70]
            # Extraer año para ordenar
            year_match = re.search(r"-?\d{3,4}", fecha)
            sort_key = int(year_match.group()) if year_match else 9999
            events.append((sort_key, fecha, sub, nodo_id))

    for _, fecha, sub, nodo_id in sorted(events, key=lambda x: x[0]):
        lines.append(f"| {fecha} | {sub}… | {nodo_id} |")

    lines.append("\n---\n")
    return "\n".join(lines)


def _seccion_personajes() -> str:
    personas_file = ARCHIVO_VIVO / "AV_PERSONAS.md"
    if not personas_file.exists():
        return "## 5. Personajes Clave\n\nVer `datos/archivo_vivo/AV_PERSONAS.md`\n\n---\n"

    content = personas_file.read_text(encoding="utf-8")
    # Extraer solo los árboles genealógicos (hasta 150 líneas)
    lines_all = content.splitlines()
    genealogy_lines: list[str] = []
    in_section = False
    count = 0
    for line in lines_all:
        if line.startswith("## ÁRBOL GENEALÓGICO"):
            in_section = True
        if in_section:
            genealogy_lines.append(line)
            count += 1
        if count > 160:
            genealogy_lines.append("\n*… ver `datos/archivo_vivo/AV_PERSONAS.md` para el árbol completo*")
            break

    if genealogy_lines:
        return "## 5. Personajes Clave — Árboles Genealógicos\n\n" + "\n".join(genealogy_lines) + "\n\n---\n"
    return "## 5. Personajes Clave\n\nVer `datos/archivo_vivo/AV_PERSONAS.md`\n\n---\n"


def _seccion_vacios() -> str:
    lines = ["## 6. Vacíos — Preguntas Abiertas\n"]

    # Estadísticas
    conteo = {"PENDIENTE": 0, "EN PROCESO": 0,
               "RESPONDIDA PARCIALMENTE": 0, "RESPONDIDA": 0}
    urgentes: list[dict] = []
    pendientes: list[dict] = []
    parciales: list[dict] = []

    for f in sorted(HOPELCHEN.glob("HOPELCHEN_PREGUNTAS_*.json")):
        d = _cargar_json(f)
        if not d:
            continue
        key = next((k for k, v in d.items() if isinstance(v, list)), None)
        if not key:
            continue
        nodo_num = d.get("nodo_id", f.stem.split("_")[1] if "_" in f.stem else "?")
        for p in d[key]:
            est = p.get("estado", "PENDIENTE")
            prio = p.get("prioridad", "")
            pid = p.get("pregunta_id", "")
            pregunta = p.get("pregunta", "")[:100]
            where = p.get("donde_buscar", p.get("fuente_sugerida", ""))[:80]

            for k in conteo:
                if k in est:
                    conteo[k] += 1
                    break

            item = {
                "id": pid, "pregunta": pregunta,
                "estado": est, "prioridad": prio,
                "donde": where, "nodo": nodo_num
            }
            if "URGENTE" in prio.upper():
                urgentes.append(item)
            elif "PENDIENTE" in est:
                pendientes.append(item)
            elif "PARCIALMENTE" in est:
                parciales.append(item)

    lines.append("### Resumen\n")
    lines.append("| Estado | Cantidad |")
    lines.append("|--------|----------|")
    lines.append(f"| 🔴 PENDIENTE | {conteo['PENDIENTE']} |")
    lines.append(f"| 🟡 EN PROCESO | {conteo['EN PROCESO']} |")
    lines.append(f"| 🟠 RESPONDIDA PARCIALMENTE | {conteo['RESPONDIDA PARCIALMENTE']} |")
    lines.append(f"| 🟢 RESPONDIDA | {conteo['RESPONDIDA']} |")
    lines.append(f"| **TOTAL** | **{sum(conteo.values())}** |\n")

    if urgentes:
        lines.append("### 🚨 URGENTES — Cuellos de botella\n")
        lines.append("| ID | Nodo | Pregunta | Dónde buscar |")
        lines.append("|----|------|----------|--------------|")
        for p in urgentes:
            lines.append(f"| `{p['id']}` | {p['nodo']} | {p['pregunta']}… | {p['donde']} |")
        lines.append("")

    if pendientes:
        lines.append("### 🔴 PENDIENTES\n")
        lines.append("| ID | Nodo | Prioridad | Pregunta |")
        lines.append("|----|------|-----------|----------|")
        for p in pendientes:
            lines.append(f"| `{p['id']}` | {p['nodo']} | {p['prioridad']} | {p['pregunta']}… |")
        lines.append("")

    if parciales:
        lines.append("### 🟠 RESPONDIDAS PARCIALMENTE — completar\n")
        lines.append("| ID | Nodo | Pregunta |")
        lines.append("|----|------|----------|")
        for p in parciales:
            lines.append(f"| `{p['id']}` | {p['nodo']} | {p['pregunta']}… |")
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)


def _seccion_fuentes() -> str:
    catalogo = FUENTES / "catalogo_fuentes.md"
    if not catalogo.exists():
        return "## 7. Fuentes\n\nVer `fuentes/catalogo_fuentes.md`\n\n---\n"

    content = catalogo.read_text(encoding="utf-8")
    lines_all = content.splitlines()
    # Tomar hasta 80 líneas del catálogo y bajar headers un nivel
    preview = []
    for line in lines_all[:80]:
        if line.startswith("# ") and not line.startswith("## "):
            preview.append("### " + line[2:])
        elif line.startswith("## "):
            preview.append("#### " + line[3:])
        else:
            preview.append(line)
    if len(lines_all) > 80:
        preview.append(f"\n*… {len(lines_all) - 80} líneas adicionales en `fuentes/catalogo_fuentes.md`*")

    return "## 7. Fuentes Bibliográficas (extracto)\n\n" + "\n".join(preview) + "\n\n---\n"


def _seccion_menonitas() -> str:
    f = HOPELCHEN / "menonitas_hopelchen.json"
    d = _cargar_json(f)
    if not d:
        return ""
    colonias = d.get("colonias_menonitas_hopelchen", [])
    if not colonias:
        return ""
    historia = d.get("historia", {})
    llegada = historia.get("llegada", {}) if isinstance(historia, dict) else {}
    impacto = d.get("impacto_ambiental", {})
    deforestacion = impacto.get("deforestacion", {}) if isinstance(impacto, dict) else {}
    acuerdo = d.get("acuerdo_historico_2021", {})

    lines = ["## 8. Datos Adicionales — Menonitas en Hopelchén\n"]
    if llegada:
        lines.append(f"- **Llegada:** {llegada.get('año', '1987')} — {llegada.get('descripcion', '')[:120]}")
    if deforestacion:
        lines.append(f"- **Deforestación:** {deforestacion.get('total_20_anos', '')}")
    if isinstance(acuerdo, dict) and acuerdo.get("fecha"):
        firmantes = ", ".join(acuerdo.get("colonias_firmantes", []))
        lines.append(f"- **Acuerdo Semarnat {acuerdo.get('fecha', '')}:** colonias firmantes: {firmantes}")
    lines.append(f"\n**Colonias documentadas ({len(colonias)}):** {', '.join(str(c) for c in colonias)}\n")
    lines.append("---\n")
    return "\n".join(lines)


def _seccion_legisladores() -> str:
    f = HOPELCHEN / "legisladores_hopelchen_1861-2003.json"
    d = _cargar_json(f)
    if not d:
        return ""
    key = next((k for k, v in d.items() if isinstance(v, list)), None)
    if not key:
        return ""
    legs = d[key]
    lines = [f"## 9. Legisladores de Hopelchén/Bolonchenticul (1861–2003)\n",
             f"Total registros: **{len(legs)}**\n",
             "| Legislatura | Municipio | Propietario | Suplente |",
             "|-------------|-----------|-------------|----------|"]
    for l in legs[:30]:
        leg = l.get("legislatura", "")
        mun = l.get("municipio", "")
        prop = l.get("propietario", "")
        sup = l.get("suplente", "")
        lines.append(f"| {leg} | {mun} | {prop} | {sup} |")
    if len(legs) > 30:
        lines.append(f"\n*… {len(legs) - 30} registros adicionales en `datos/hopelchen/legisladores_hopelchen_1861-2003.json`*")
    lines.append("\n---\n")
    return "\n".join(lines)


def _seccion_estado_borradores() -> str:
    borradores = sorted((DATOS / "borradores").glob("*.md"))
    if not borradores:
        return ""
    lines = ["## 10. Estado de los Borradores\n",
             f"Total borradores: **{len(borradores)}**\n",
             "| Archivo | Tamaño | Estado visible |",
             "|---------|--------|----------------|"]
    for b in borradores:
        content = b.read_text(encoding="utf-8", errors="replace")
        size = f"{len(content):,} chars"
        # Look for estado in first 3 lines
        first_lines = content.splitlines()[:5]
        estado = next(
            (ln for ln in first_lines if "Estado" in ln or "estado" in ln or "✅" in ln or "⚠" in ln),
            "—"
        )
        estado = estado.strip().lstrip("#>-").strip()[:50]
        lines.append(f"| `{b.name}` | {size} | {estado} |")
    lines.append("\n---\n")
    return "\n".join(lines)


def _seccion_pie(fecha: str) -> str:
    return f"""## Notas de generación

- **Generado:** {fecha}
- **Script:** `tools/generar_sintesis.py`
- **Repositorio:** Daniela-Naraai-Caamal-Ake/investigacion-historica
- **Regenerar:** `python tools/generar_sintesis.py`

> Para actualizar este documento después de agregar datos a cualquier nodo,
> ejecuta el script. El documento se regenera completamente desde los JSON fuente.
"""


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Genera SINTESIS_MAESTRA.md")
    parser.add_argument("--salida", default=str(SALIDA_DEFAULT),
                        help="Ruta del archivo de salida")
    args = parser.parse_args()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[generar_sintesis] Generando síntesis maestra… ({fecha})")

    secciones = [
        _seccion_cabecera(fecha),
        _seccion_hipotesis(),
        _seccion_estructura_libro(),
        _seccion_registros(),
        _seccion_cronologia(),
        _seccion_personajes(),
        _seccion_vacios(),
        _seccion_fuentes(),
        _seccion_menonitas(),
        _seccion_legisladores(),
        _seccion_estado_borradores(),
        _seccion_pie(fecha),
    ]

    contenido = "\n".join(s for s in secciones if s)

    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(contenido, encoding="utf-8")

    words = len(contenido.split())
    print(f"[generar_sintesis] ✅ Escrito: {salida} ({words:,} palabras)")


if __name__ == "__main__":
    main()
