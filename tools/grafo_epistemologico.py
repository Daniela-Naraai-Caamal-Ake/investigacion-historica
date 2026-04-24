#!/usr/bin/env python3
"""
grafo_epistemologico.py
=======================
Construye el grafo de conocimiento del proyecto *Dos Mil Años en Silencio* y
analiza su robustez epistemológica:

  - ¿Qué registros no están enlazados a la hipótesis central?
  - ¿Qué registros carecen de fuente verificable?
  - ¿Qué nodos históricos quedan aislados del resto?
  - ¿Qué preguntas permanecen abiertas?
  - ¿Qué componentes del grafo son débiles (pocos enlaces salientes)?

Diseño epistemológico
---------------------
Un conocimiento es robusto cuando cada afirmación cumple la cadena:

    Hipótesis → Nodo histórico → Registro → Fuente

Si algún eslabón de esa cadena falta, el registro queda "flotando" —
es decir, no integrado al sistema epistemológico del proyecto.

Tipos de nodo en el grafo:
  • ``hipotesis``      — la hipótesis central (nodo raíz)
  • ``nodo_historico`` — los 10 períodos históricos
  • ``registro``       — afirmaciones históricas concretas con fuente
  • ``fuente``         — referencias bibliográficas / archivos
  • ``pregunta``       — preguntas de investigación (respondidas o pendientes)

Tipos de arista (dirigida):
  • ``pertenece_a``       registro → nodo_historico / pregunta → nodo_historico
  • ``conecta_hipotesis`` registro → hipotesis (cuando tiene conexion_hipotesis)
  • ``cita``              registro → fuente
  • ``continua_desde``    nodo_historico → nodo_historico (enlace temporal)
  • ``comparte_actor``    nodo_historico → nodo_historico (actor común)
  • ``comparte_tag``      nodo_historico → nodo_historico (etiqueta común)
  • ``responde_a``        pregunta → nodo_historico (cuando estado ≠ PENDIENTE)

Uso:
    python tools/grafo_epistemologico.py
    python tools/grafo_epistemologico.py --solo-reporte
    python tools/grafo_epistemologico.py --solo-json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
NODOS_DIR = ROOT / "datos" / "hopelchen"
SALIDA_MD = ROOT / "analisis" / "grafo_epistemologico.md"
SALIDA_JSON = ROOT / "docs" / "grafo_epistemologico.json"

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

CAMPOS_FUENTE = [
    "fuente", "fuente_1", "fuente_academica", "fuente_primaria",
    "fuente_secundaria", "fuentes",
]

# Prefijos de IDs de nodo
PREFIJO_HIPOTESIS = "HIPOTESIS"
PREFIJO_NODO = "NODO"
PREFIJO_REGISTRO = "REGISTRO"
PREFIJO_FUENTE = "FUENTE"
PREFIJO_PREGUNTA = "PREGUNTA"


# ---------------------------------------------------------------------------
# Clase del grafo
# ---------------------------------------------------------------------------

class GrafoEpistemologico:
    """
    Grafo dirigido que modela el sistema epistemológico de la investigación.

    Atributos
    ---------
    nodos : dict[str, dict]
        Mapa id_nodo → {tipo, etiqueta, datos}.
    aristas : list[dict]
        Lista de {origen, destino, tipo}.
    """

    def __init__(self) -> None:
        self.nodos: dict[str, dict] = {}
        self.aristas: list[dict] = []
        self._adyacencia: dict[str, list[str]] = {}   # origen → [destinos]
        self._inversa: dict[str, list[str]] = {}      # destino → [orígenes]

    # ── construcción ─────────────────────────────────────────────────────────

    def agregar_nodo(
        self,
        nodo_id: str,
        tipo: str,
        etiqueta: str,
        datos: dict | None = None,
    ) -> None:
        self.nodos[nodo_id] = {
            "tipo": tipo,
            "etiqueta": etiqueta,
            "datos": datos or {},
        }
        self._adyacencia.setdefault(nodo_id, [])
        self._inversa.setdefault(nodo_id, [])

    def agregar_arista(
        self,
        origen: str,
        destino: str,
        tipo: str,
        datos: dict | None = None,
    ) -> None:
        if origen not in self.nodos or destino not in self.nodos:
            return
        self.aristas.append({"origen": origen, "destino": destino, "tipo": tipo,
                              "datos": datos or {}})
        self._adyacencia[origen].append(destino)
        self._inversa[destino].append(origen)

    # ── métricas básicas ──────────────────────────────────────────────────────

    def grado_salida(self, nodo_id: str) -> int:
        return len(self._adyacencia.get(nodo_id, []))

    def grado_entrada(self, nodo_id: str) -> int:
        return len(self._inversa.get(nodo_id, []))

    def vecinos(self, nodo_id: str) -> list[str]:
        """Devuelve los nodos alcanzables directamente desde *nodo_id*."""
        return list(self._adyacencia.get(nodo_id, []))

    def predecesores(self, nodo_id: str) -> list[str]:
        return list(self._inversa.get(nodo_id, []))

    # ── análisis de conectividad ──────────────────────────────────────────────

    def componentes_conectados_no_dirigidos(self) -> list[set[str]]:
        """
        Encuentra componentes conexos ignorando la dirección de las aristas
        (BFS sobre el grafo subyacente no dirigido).
        """
        visitados: set[str] = set()
        grafo_nd: dict[str, set[str]] = {n: set() for n in self.nodos}
        for a in self.aristas:
            grafo_nd[a["origen"]].add(a["destino"])
            grafo_nd[a["destino"]].add(a["origen"])

        componentes: list[set[str]] = []
        for nodo in self.nodos:
            if nodo in visitados:
                continue
            comp: set[str] = set()
            cola: deque[str] = deque([nodo])
            while cola:
                actual = cola.popleft()
                if actual in visitados:
                    continue
                visitados.add(actual)
                comp.add(actual)
                cola.extend(grafo_nd[actual] - visitados)
            componentes.append(comp)
        return componentes

    def nodos_aislados(self) -> list[str]:
        """Nodos sin ninguna arista (ni entrante ni saliente)."""
        return [
            nid for nid in self.nodos
            if not self._adyacencia.get(nid) and not self._inversa.get(nid)
        ]

    def alcanzables_desde(self, origen: str) -> set[str]:
        """BFS desde *origen*; devuelve todos los nodos alcanzables (dirigido)."""
        visitados: set[str] = set()
        cola: deque[str] = deque([origen])
        while cola:
            actual = cola.popleft()
            if actual in visitados:
                continue
            visitados.add(actual)
            cola.extend(self._adyacencia.get(actual, []))
        visitados.discard(origen)
        return visitados

    # ── análisis epistemológico ───────────────────────────────────────────────

    def analizar_robustez(self) -> dict[str, Any]:
        """
        Evalúa la robustez del sistema epistemológico.

        Retorna un diccionario con las siguientes claves:
          - registros_sin_hipotesis   : IDs de registros sin conexion_hipotesis
          - registros_sin_fuente      : IDs de registros sin ninguna fuente
          - registros_sin_tags        : IDs de registros sin etiquetas temáticas
          - nodos_aislados            : nodos históricos sin conexión a otros
          - preguntas_pendientes      : preguntas con estado PENDIENTE
          - componentes               : lista de componentes conexos
          - nodos_debiles             : nodos con grado_salida == 1
          - metricas                  : estadísticas globales
        """
        registros_sin_hipotesis: list[str] = []
        registros_sin_fuente: list[str] = []
        registros_sin_tags: list[str] = []
        preguntas_pendientes: list[str] = []

        for nid, info in self.nodos.items():
            tipo = info["tipo"]
            datos = info["datos"]

            if tipo == PREFIJO_REGISTRO:
                # ¿Tiene arista hacia la hipótesis?
                tiene_hip = any(
                    a["tipo"] == "conecta_hipotesis"
                    for a in self.aristas
                    if a["origen"] == nid
                )
                if not tiene_hip:
                    registros_sin_hipotesis.append(nid)

                # ¿Tiene arista de cita?
                tiene_fuente = any(
                    a["tipo"] == "cita"
                    for a in self.aristas
                    if a["origen"] == nid
                )
                if not tiene_fuente:
                    registros_sin_fuente.append(nid)

                # ¿Tiene tags?
                if not datos.get("tags"):
                    registros_sin_tags.append(nid)

            elif tipo == PREFIJO_PREGUNTA:
                if datos.get("estado", "").upper() == "PENDIENTE":
                    preguntas_pendientes.append(nid)

        # Nodos históricos aislados (sin aristas con otros nodos históricos)
        nodos_historicos_aislados: list[str] = []
        for nid, info in self.nodos.items():
            if info["tipo"] != PREFIJO_NODO:
                continue
            vecinos_nodos = [
                v for v in self._adyacencia.get(nid, []) + self._inversa.get(nid, [])
                if self.nodos.get(v, {}).get("tipo") == PREFIJO_NODO
            ]
            if not vecinos_nodos:
                nodos_historicos_aislados.append(nid)

        componentes = self.componentes_conectados_no_dirigidos()

        # Nodos débiles (grado salida == 1, excluye hipótesis y fuentes)
        nodos_debiles = [
            nid for nid in self.nodos
            if self.nodos[nid]["tipo"] in (PREFIJO_NODO, PREFIJO_REGISTRO)
            and self.grado_salida(nid) == 1
        ]

        total_nodos = len(self.nodos)
        total_aristas = len(self.aristas)
        total_registros = sum(
            1 for i in self.nodos.values() if i["tipo"] == PREFIJO_REGISTRO
        )
        total_nodos_hist = sum(
            1 for i in self.nodos.values() if i["tipo"] == PREFIJO_NODO
        )
        total_preguntas = sum(
            1 for i in self.nodos.values() if i["tipo"] == PREFIJO_PREGUNTA
        )
        total_fuentes = sum(
            1 for i in self.nodos.values() if i["tipo"] == PREFIJO_FUENTE
        )

        cobertura_hipotesis = (
            round(
                (total_registros - len(registros_sin_hipotesis)) / total_registros * 100,
                1,
            )
            if total_registros else 0
        )
        cobertura_fuente = (
            round(
                (total_registros - len(registros_sin_fuente)) / total_registros * 100,
                1,
            )
            if total_registros else 0
        )

        return {
            "registros_sin_hipotesis": registros_sin_hipotesis,
            "registros_sin_fuente": registros_sin_fuente,
            "registros_sin_tags": registros_sin_tags,
            "nodos_historicos_aislados": nodos_historicos_aislados,
            "preguntas_pendientes": preguntas_pendientes,
            "componentes": componentes,
            "nodos_debiles": nodos_debiles,
            "metricas": {
                "total_nodos": total_nodos,
                "total_aristas": total_aristas,
                "total_nodos_historicos": total_nodos_hist,
                "total_registros": total_registros,
                "total_preguntas": total_preguntas,
                "total_fuentes": total_fuentes,
                "num_componentes": len(componentes),
                "cobertura_hipotesis_pct": cobertura_hipotesis,
                "cobertura_fuente_pct": cobertura_fuente,
            },
        }

    # ── exportación ───────────────────────────────────────────────────────────

    def exportar_json(self) -> dict:
        """Devuelve el grafo serializable como JSON (formato nodos + aristas)."""
        nodos_json = [
            {
                "id": nid,
                "tipo": info["tipo"],
                "etiqueta": info["etiqueta"],
                "grado_entrada": self.grado_entrada(nid),
                "grado_salida": self.grado_salida(nid),
            }
            for nid, info in self.nodos.items()
        ]
        aristas_json = [
            {"origen": a["origen"], "destino": a["destino"], "tipo": a["tipo"]}
            for a in self.aristas
        ]
        return {"nodos": nodos_json, "aristas": aristas_json}


# ---------------------------------------------------------------------------
# Construcción del grafo desde los archivos de datos
# ---------------------------------------------------------------------------

def _tiene_fuente(registro: dict) -> bool:
    for campo in CAMPOS_FUENTE:
        v = registro.get(campo)
        if v:
            if isinstance(v, str) and v.strip():
                return True
            if isinstance(v, (dict, list)):
                return True
    return False


def _id_fuente(registro_id: str, campo: str) -> str:
    return f"{PREFIJO_FUENTE}:{registro_id}:{campo}"


def _extraer_preguntas_de_archivo(data: dict) -> list[dict]:
    """
    Extrae todos los objetos de pregunta de un archivo PREGUNTAS_*.json.

    Busca primero en las claves canónicas conocidas y luego en cualquier clave
    que comience con ``"preguntas"`` para capturar variantes futuras como
    ``"preguntas_urgentes_005"``.  Solo se incluyen entradas que sean dicts
    con el campo ``pregunta_id``.
    """
    CLAVES_CONOCIDAS = (
        "preguntas",
        "preguntas_urgentes",
        "preguntas_alta_prioridad",
        "preguntas_media_prioridad",
    )
    claves_extra = [
        k for k in data
        if k.startswith("preguntas") and k not in CLAVES_CONOCIDAS
    ]
    preguntas: list[dict] = []
    for clave in (*CLAVES_CONOCIDAS, *claves_extra):
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


def construir_grafo() -> GrafoEpistemologico:
    """Carga todos los datos del proyecto y construye el grafo."""

    g = GrafoEpistemologico()

    # ── 1. Nodo raíz: hipótesis ────────────────────────────────────────────
    g.agregar_nodo(
        PREFIJO_HIPOTESIS,
        PREFIJO_HIPOTESIS,
        "Hipótesis central (v5)",
        {"descripcion": (
            "En Hopelchén, entre 1200 y 2026, el control de tierra, conocimiento "
            "y decisión política ha tendido a concentrarse en élites externas."
        )},
    )

    # ── 2. Nodos históricos ───────────────────────────────────────────────
    nodo_archivos = sorted(
        glob.glob(str(NODOS_DIR / "HOPELCHEN_NODO_*.json"))
    )
    nodos_data: list[dict] = []

    for ruta in nodo_archivos:
        try:
            with open(ruta, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue

        nodo_id_num = data.get("nodo_id", "")
        nodo_id = f"{PREFIJO_NODO}:{nodo_id_num}"
        titulo = data.get("titulo", nodo_id)
        g.agregar_nodo(
            nodo_id,
            PREFIJO_NODO,
            titulo,
            {
                "nodo_id": nodo_id_num,
                "rango_temporal": data.get("rango_temporal", ""),
                "continua_desde": data.get("continua_desde", ""),
            },
        )
        nodos_data.append({"id": nodo_id, "num": nodo_id_num, "data": data})

    # Aristas continua_desde (enlace temporal entre nodos)
    for entrada in nodos_data:
        continua = entrada["data"].get("continua_desde", "")
        if not continua:
            continue
        # Extraer número de nodo del texto "NODO 001 — …"
        match = re.search(r"NODO\s+(\d+)", continua)
        if match:
            num_prev = match.group(1).zfill(3)
            nodo_prev_id = f"{PREFIJO_NODO}:{num_prev}"
            g.agregar_arista(
                entrada["id"], nodo_prev_id, "continua_desde"
            )

    # ── 3. Registros, fuentes y conexiones con hipótesis ──────────────────
    actores_por_nodo: dict[str, list[str]] = {}
    tags_por_nodo: dict[str, list[str]] = {}

    for entrada in nodos_data:
        nodo_id = entrada["id"]
        registros = entrada["data"].get("registros", [])
        actores_por_nodo[nodo_id] = []
        tags_por_nodo[nodo_id] = []

        for reg in registros:
            rid = reg.get("registro_id", "")
            if not rid:
                continue
            reg_id = f"{PREFIJO_REGISTRO}:{rid}"
            subtitulo = reg.get("subtitulo", reg.get("descripcion", rid))[:80]
            g.agregar_nodo(
                reg_id,
                PREFIJO_REGISTRO,
                subtitulo,
                {
                    "registro_id": rid,
                    "tags": reg.get("tags", []),
                    "tipo_dato": reg.get("tipo_dato", ""),
                    "tiene_conexion_hipotesis": bool(reg.get("conexion_hipotesis")),
                },
            )

            # Arista: registro → nodo_historico
            g.agregar_arista(reg_id, nodo_id, "pertenece_a")

            # Arista: registro → hipótesis
            if reg.get("conexion_hipotesis"):
                g.agregar_arista(reg_id, PREFIJO_HIPOTESIS, "conecta_hipotesis")

            # Aristas: registro → fuentes
            for campo in CAMPOS_FUENTE:
                v = reg.get(campo)
                if not v:
                    continue
                fuente_id = _id_fuente(rid, campo)
                if isinstance(v, dict):
                    nombre_fuente = v.get("nombre", campo)
                elif isinstance(v, str):
                    nombre_fuente = v
                elif isinstance(v, list):
                    nombre_fuente = f"{campo} ({len(v)} entradas)"
                else:
                    continue
                g.agregar_nodo(fuente_id, PREFIJO_FUENTE, nombre_fuente[:80])
                g.agregar_arista(reg_id, fuente_id, "cita")

            # Colectar actores y tags para aristas inter-nodo
            for p in reg.get("personajes", []):
                if isinstance(p, dict):
                    nombre = p.get("nombre", "")
                else:
                    nombre = str(p)
                if nombre:
                    actores_por_nodo[nodo_id].append(nombre)
            tags_por_nodo[nodo_id].extend(reg.get("tags", []))

    # ── 4. Aristas inter-nodo: actores y tags compartidos ─────────────────
    nodo_ids = [e["id"] for e in nodos_data]
    for i, nodo_a in enumerate(nodo_ids):
        for nodo_b in nodo_ids[i + 1:]:
            # actores comunes
            actores_a = set(actores_por_nodo.get(nodo_a, []))
            actores_b = set(actores_por_nodo.get(nodo_b, []))
            comunes = actores_a & actores_b - {""}
            for actor in comunes:
                g.agregar_arista(nodo_a, nodo_b, "comparte_actor",
                                 {"actor": actor})
                g.agregar_arista(nodo_b, nodo_a, "comparte_actor",
                                 {"actor": actor})

            # tags comunes
            TAGS_IGNORAR = {"Hopelchén", "Los Chenes", "Campeche", "maya", "mayas"}
            tags_a = set(tags_por_nodo.get(nodo_a, [])) - TAGS_IGNORAR
            tags_b = set(tags_por_nodo.get(nodo_b, [])) - TAGS_IGNORAR
            tags_comunes = tags_a & tags_b - {""}
            for tag in tags_comunes:
                g.agregar_arista(nodo_a, nodo_b, "comparte_tag",
                                 {"tag": tag})

    # ── 5. Preguntas ──────────────────────────────────────────────────────
    pregunta_archivos = sorted(
        glob.glob(str(NODOS_DIR / "HOPELCHEN_PREGUNTAS_*.json"))
    )

    for ruta in pregunta_archivos:
        try:
            with open(ruta, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue

        # Determinar nodo de origen desde el nombre de archivo o campo
        nodo_origen_texto = data.get("nodo_origen", "")
        match = re.search(r"(\d+)", nodo_origen_texto)
        nodo_num = match.group(1).zfill(3) if match else None

        # Fallback: extraer del nombre del archivo
        if not nodo_num:
            fname = Path(ruta).stem
            m2 = re.search(r"PREGUNTAS_(\d+)", fname)
            if m2:
                nodo_num = m2.group(1).zfill(3)

        nodo_origen_id = f"{PREFIJO_NODO}:{nodo_num}" if nodo_num else None

        for preg in _extraer_preguntas_de_archivo(data):
            pid = preg.get("pregunta_id", "")
            if not pid:
                continue
            preg_id = f"{PREFIJO_PREGUNTA}:{pid}"
            texto = preg.get("pregunta", pid)[:80]
            estado = preg.get("estado", "PENDIENTE").upper()
            g.agregar_nodo(
                preg_id,
                PREFIJO_PREGUNTA,
                texto,
                {
                    "pregunta_id": pid,
                    "estado": estado,
                    "prioridad": preg.get("prioridad", ""),
                    "tipo": preg.get("tipo", ""),
                },
            )

            if nodo_origen_id:
                g.agregar_arista(preg_id, nodo_origen_id, "pertenece_a")

            # Las preguntas respondidas se enlazan también a la hipótesis
            if estado.startswith("RESPONDIDA"):
                g.agregar_arista(preg_id, PREFIJO_HIPOTESIS, "responde_a")

    return g


# ---------------------------------------------------------------------------
# Generación del reporte Markdown
# ---------------------------------------------------------------------------

def _etiqueta_breve(g: GrafoEpistemologico, nid: str) -> str:
    info = g.nodos.get(nid, {})
    return info.get("etiqueta", nid)[:60]


def generar_reporte(g: GrafoEpistemologico, analisis: dict) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    m = analisis["metricas"]
    lineas: list[str] = []

    lineas += [
        "# Grafo Epistemológico — *Dos Mil Años en Silencio*",
        "",
        f"> Autora: Daniela Naraai Caamal Ake  ",
        f"> Generado: {ts}  ",
        "> ⚙ Generado automáticamente por `tools/grafo_epistemologico.py`",
        "",
        "Este documento analiza la **robustez epistemológica** del proyecto:",
        "cada afirmación (registro) debe estar encadenada a:",
        "",
        "```",
        "Hipótesis → Nodo histórico → Registro → Fuente",
        "```",
        "",
        "Un registro que rompe esta cadena es una **brecha epistemológica**: "
        "puede ser válido pero no está integrado al sistema de conocimiento del proyecto.",
        "",
        "---",
        "",
        "## Índice",
        "",
        "1. [Métricas del grafo](#1-métricas-del-grafo)",
        "2. [Componentes conexos](#2-componentes-conexos)",
        "3. [Brechas epistemológicas: sin conexión a hipótesis]"
        "(#3-brechas-epistemológicas-sin-conexión-a-hipótesis)",
        "4. [Brechas epistemológicas: sin fuente verificable]"
        "(#4-brechas-epistemológicas-sin-fuente-verificable)",
        "5. [Registros sin etiquetas temáticas](#5-registros-sin-etiquetas-temáticas)",
        "6. [Nodos históricos aislados](#6-nodos-históricos-aislados)",
        "7. [Preguntas pendientes](#7-preguntas-pendientes)",
        "8. [Conectividad inter-nodo](#8-conectividad-inter-nodo)",
        "",
        "---",
        "",
        "## 1. Métricas del grafo",
        "",
        f"| Indicador | Valor |",
        f"|---|---|",
        f"| Nodos totales | {m['total_nodos']} |",
        f"| Aristas totales | {m['total_aristas']} |",
        f"| Nodos históricos | {m['total_nodos_historicos']} |",
        f"| Registros | {m['total_registros']} |",
        f"| Fuentes | {m['total_fuentes']} |",
        f"| Preguntas | {m['total_preguntas']} |",
        f"| Componentes conexos | {m['num_componentes']} |",
        f"| Cobertura de hipótesis | **{m['cobertura_hipotesis_pct']}%** |",
        f"| Cobertura de fuente | **{m['cobertura_fuente_pct']}%** |",
        "",
        "---",
        "",
        "## 2. Componentes conexos",
        "",
        "Un componente conexo es un grupo de nodos que se pueden alcanzar entre sí "
        "(ignorando la dirección de las aristas).",
        "",
    ]

    componentes = analisis["componentes"]
    tipos_deseados = {PREFIJO_HIPOTESIS, PREFIJO_NODO}
    comp_principales = [
        c for c in componentes
        if any(g.nodos.get(n, {}).get("tipo") in tipos_deseados for n in c)
    ]
    comp_pequeños = [c for c in componentes if len(c) == 1]

    lineas.append(
        f"Se detectaron **{len(componentes)} componente(s) conexo(s)**. "
        f"{len(comp_pequeños)} nodo(s) completamente aislado(s)."
    )
    lineas.append("")

    if len(comp_principales) == 1:
        lineas.append(
            "✅ Todos los nodos históricos y la hipótesis forman un único componente conectado."
        )
    else:
        lineas.append(
            f"⚠️ Hay **{len(comp_principales)} subgrafos** que contienen nodos históricos o la hipótesis. "
            "Esto indica fragmentación del grafo principal."
        )
        for i, comp in enumerate(comp_principales, 1):
            nombres = sorted(
                g.nodos[n]["etiqueta"][:50]
                for n in comp
                if g.nodos.get(n, {}).get("tipo") in tipos_deseados
            )
            lineas.append(f"  - Subgrafo {i}: {', '.join(nombres)}")

    lineas += [
        "",
        "---",
        "",
        "## 3. Brechas epistemológicas: sin conexión a hipótesis",
        "",
        "Registros que **no tienen** campo `conexion_hipotesis` — sus afirmaciones "
        "no están explícitamente enlazadas a la pregunta guía del proyecto.",
        "",
    ]

    sin_hip = analisis["registros_sin_hipotesis"]
    if not sin_hip:
        lineas.append("✅ Todos los registros están conectados a la hipótesis.")
    else:
        lineas.append(f"⚠️ **{len(sin_hip)} registro(s)** sin conexión a hipótesis:")
        lineas.append("")
        for nid in sin_hip:
            info = g.nodos.get(nid, {})
            rid = info.get("datos", {}).get("registro_id", nid)
            etiqueta = info.get("etiqueta", nid)[:60]
            # Determinar nodo al que pertenece
            nodo_padre = next(
                (a["destino"] for a in g.aristas
                 if a["origen"] == nid and a["tipo"] == "pertenece_a"),
                None,
            )
            nodo_titulo = (
                g.nodos[nodo_padre]["etiqueta"][:30] if nodo_padre else "?"
            )
            lineas.append(f"- `{rid}` ({nodo_titulo}) — {etiqueta}")

    lineas += [
        "",
        "---",
        "",
        "## 4. Brechas epistemológicas: sin fuente verificable",
        "",
        "Registros que **no citan ninguna fuente**. Sin fuente, la afirmación "
        "no puede ser verificada ni refutada.",
        "",
    ]

    sin_fuente = analisis["registros_sin_fuente"]
    if not sin_fuente:
        lineas.append("✅ Todos los registros tienen al menos una fuente.")
    else:
        lineas.append(f"⚠️ **{len(sin_fuente)} registro(s)** sin fuente:")
        lineas.append("")
        for nid in sin_fuente:
            info = g.nodos.get(nid, {})
            rid = info.get("datos", {}).get("registro_id", nid)
            etiqueta = info.get("etiqueta", nid)[:60]
            lineas.append(f"- `{rid}` — {etiqueta}")

    lineas += [
        "",
        "---",
        "",
        "## 5. Registros sin etiquetas temáticas",
        "",
        "Los `tags` permiten crear aristas temáticas entre nodos. "
        "Registros sin tags quedan fuera del grafo de temas.",
        "",
    ]

    sin_tags = analisis["registros_sin_tags"]
    if not sin_tags:
        lineas.append("✅ Todos los registros tienen etiquetas temáticas.")
    else:
        lineas.append(f"ℹ️ **{len(sin_tags)} registro(s)** sin tags:")
        lineas.append("")
        for nid in sin_tags[:20]:  # máximo 20 para no saturar el reporte
            info = g.nodos.get(nid, {})
            rid = info.get("datos", {}).get("registro_id", nid)
            lineas.append(f"- `{rid}`")
        if len(sin_tags) > 20:
            lineas.append(f"  *(y {len(sin_tags) - 20} más)*")

    lineas += [
        "",
        "---",
        "",
        "## 6. Nodos históricos aislados",
        "",
        "Nodos históricos sin ninguna arista hacia otro nodo histórico "
        "(vía actores, tags o `continua_desde`). Un nodo aislado no contribuye "
        "al tejido relacional del grafo.",
        "",
    ]

    nh_aislados = analisis["nodos_historicos_aislados"]
    if not nh_aislados:
        lineas.append("✅ Todos los nodos históricos están conectados entre sí.")
    else:
        lineas.append(
            f"⚠️ **{len(nh_aislados)} nodo(s) histórico(s)** sin conexión inter-nodo:"
        )
        lineas.append("")
        for nid in nh_aislados:
            lineas.append(f"- {_etiqueta_breve(g, nid)}")

    lineas += [
        "",
        "---",
        "",
        "## 7. Preguntas pendientes",
        "",
        "Preguntas con estado `PENDIENTE` que aún no han sido respondidas.",
        "",
    ]

    pend = analisis["preguntas_pendientes"]
    if not pend:
        lineas.append("✅ No hay preguntas pendientes.")
    else:
        lineas.append(f"ℹ️ **{len(pend)} pregunta(s) pendiente(s)**:")
        lineas.append("")
        for nid in pend:
            info = g.nodos.get(nid, {})
            pid = info.get("datos", {}).get("pregunta_id", nid)
            prioridad = info.get("datos", {}).get("prioridad", "?")
            etiqueta = info.get("etiqueta", nid)[:70]
            lineas.append(f"- `{pid}` [{prioridad}] — {etiqueta}")

    lineas += [
        "",
        "---",
        "",
        "## 8. Conectividad inter-nodo",
        "",
        "Número de aristas que conectan cada nodo histórico con otros nodos "
        "(actores compartidos, tags compartidos, continuación temporal).",
        "",
        "| Nodo | Título | Aristas hacia otros nodos |",
        "|---|---|---|",
    ]

    for entrada in sorted(
        [e for e in g.nodos.values() if e["tipo"] == PREFIJO_NODO],
        key=lambda x: x["datos"].get("nodo_id", ""),
    ):
        nid_num = entrada["datos"].get("nodo_id", "")
        nid = f"{PREFIJO_NODO}:{nid_num}"
        titulo = TITULOS_NODOS.get(nid_num, entrada["etiqueta"][:30])
        aristas_a_nodos = sum(
            1 for a in g.aristas
            if a["origen"] == nid
            and g.nodos.get(a["destino"], {}).get("tipo") == PREFIJO_NODO
        )
        estado_icon = "✅" if aristas_a_nodos >= 2 else ("⚠️" if aristas_a_nodos == 1 else "❌")
        lineas.append(
            f"| {nid_num} | {titulo} | {estado_icon} {aristas_a_nodos} |"
        )

    lineas += [
        "",
        "---",
        "",
        "*Última actualización: generado automáticamente.*",
    ]

    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Construye el grafo epistemológico y analiza la robustez del sistema."
    )
    parser.add_argument(
        "--solo-reporte",
        action="store_true",
        help="Solo genera el reporte Markdown (no el JSON).",
    )
    parser.add_argument(
        "--solo-json",
        action="store_true",
        help="Solo genera el JSON del grafo (no el Markdown).",
    )
    args = parser.parse_args()

    print("🔍  Construyendo grafo epistemológico…")
    grafo = construir_grafo()

    print("📊  Analizando robustez…")
    analisis = grafo.analizar_robustez()
    m = analisis["metricas"]

    print(f"   {m['total_nodos']} nodos · {m['total_aristas']} aristas")
    print(
        f"   Cobertura hipótesis: {m['cobertura_hipotesis_pct']}%  |  "
        f"Cobertura fuente: {m['cobertura_fuente_pct']}%"
    )

    sin_hip = analisis["registros_sin_hipotesis"]
    sin_fuente = analisis["registros_sin_fuente"]
    n_aislados = analisis["nodos_historicos_aislados"]

    if sin_hip:
        print(f"   ⚠  {len(sin_hip)} registro(s) sin conexión a hipótesis")
    if sin_fuente:
        print(f"   ⚠  {len(sin_fuente)} registro(s) sin fuente")
    if n_aislados:
        print(f"   ⚠  {len(n_aislados)} nodo(s) histórico(s) aislado(s)")

    pendientes = analisis["preguntas_pendientes"]
    if pendientes:
        print(f"   ℹ  {len(pendientes)} pregunta(s) pendiente(s)")

    if not args.solo_json:
        reporte = generar_reporte(grafo, analisis)
        SALIDA_MD.parent.mkdir(parents=True, exist_ok=True)
        SALIDA_MD.write_text(reporte, encoding="utf-8")
        print(f"📄  Reporte guardado → {SALIDA_MD}")

    if not args.solo_reporte:
        grafo_json = grafo.exportar_json()
        grafo_json["generado"] = datetime.now(timezone.utc).isoformat()
        grafo_json["metricas"] = m
        SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
        SALIDA_JSON.write_text(
            json.dumps(grafo_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"💾  JSON guardado → {SALIDA_JSON}")

    # Código de salida: 0 si todo está OK, 1 si hay brechas críticas
    tiene_brechas = bool(sin_fuente or n_aislados)
    sys.exit(1 if tiene_brechas else 0)


if __name__ == "__main__":
    main()
