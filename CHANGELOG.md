# Changelog

*Registro de cambios del proyecto — Sistema de información histórica sobre Hopelchén, Campeche*  
Autora: Daniela Naraai Caamal Ake  
Formato: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

---

## [2026-04-18] — Sesión principal de construcción del sistema

### Añadido
- **Capa 4 del sistema (relaciones):** tres scripts y archivos generados en `analisis/`
  - `tools/generar_matriz_cruces.py` → `analisis/cruce_informacion.md` (actores, mecanismos y temas transversales entre nodos)
  - `tools/generar_contradicciones.py` → `analisis/contradicciones.md` (82 tensiones clasificadas)
  - `tools/generar_mapa_silencios.py` → `analisis/mapa_silencios.md` (voces ausentes, períodos sin registros, silencios temáticos)
- **Investigación web completa:** 39 vacíos PENDIENTE → 0; catálogo de fuentes 43 → 73 (F054–F069)
- **5 fuentes nuevas (F065–F069):**
  - F065: Chávez Gómez (2012) — batabilob Los Chenes, organización prehispánica
  - F066: SciELO/Mora (2019) — Guerra de Castas y Los Chenes 1847-1850
  - F067: INAH (2023) — Ocomtún, ciudad maya al sur de Los Chenes
  - F068: Carta en maya de Francisco Cimé, Capitán (Kancabchén, 1848)
  - F069: Vadillo Buenfil (2017) — La rebelión de los Cruzoob, análisis académico
- **Nuevo registro 001-H:** Ocomtún (2023) — primer registro en el nodo prehispánico sobre descubrimiento arqueológico reciente mediante LiDAR
- **NODO 010:** Archivo de preguntas `HOPELCHEN_PREGUNTAS_010_Conocimiento_Cultura.json` creado (148 tests)
- **INDICE_LIBRO.md:** mapa editorial completo — 24 capítulos, ~50,000 palabras, ~200 páginas, estado de cada borrador
- **README en datos/curated/:** mapa de fuentes de verdad por tipo de dato
- **MAPA_CAPAS:** Capa 2 (borradores), Capa 6 (docs/stats), Capa 8 (análisis) añadidas
- **`tools/validar_citas.py`** y **`tests/test_validar_citas.py`** (26 pruebas): validación de URLs y búsqueda de fuentes faltantes
- **`.env.example`:** plantilla de variables de entorno sin claves

### Cambiado
- **DOCUMENTO_FUNDACIONAL** reescrito como marco conceptual del sistema (4 capas: registro, contextualización, descomposición, relaciones); texto base de autoría de Daniela Naraai Caamal Ake
- **HIPOTESIS.md** reescrito a versión operativa v5 con enfoque concreto y generalizable
- **README.md** reescrito con tabla de estado del proyecto, estructura completa, todos los comandos, DOI
- **PRÓLOGO.md:** bloques C-H marcados como `(pendiente)` — A y B como `(en curso)`
- **DOCUMENTO_FUNDACIONAL sección 7:** tabla distingue estado al inicio (8 nodos, 21 capítulos) vs. estado actual (10 nodos, 24+ capítulos)

### Corregido
- **26 registros sin fuente → 0:** fuentes añadidas a nodos 004, 005, 006, 007, 008, 009, 010
- **14 estados mal formados:** texto embebido en campo `estado` separado a `hallazgos` + `registro_respuesta`
- **37 preguntas sin `registro_respuesta`:** campo sincronizado desde `hallazgos`
- **`generar_estadisticas.py`:** `EN PROCESO` ahora clasificado como "En curso" (antes contaba como Pendiente)
- **11 advertencias de fecha → 0:** `nota_cronologica` como mecanismo para fechas fuera de rango del nodo
- **FX007, FX008, FX009, FX019** añadidas a `datos/curated/fuentes.json` (estaban en el catálogo Markdown pero no en el JSON)
- Conflictos de merge con remoto resueltos (PR #43 — renombrado de Firecrawl a búsqueda web)

### Eliminado
- **Firecrawl completamente eliminado:** `tools/firecrawl_*.py`, `.env` del tracking, referencias en comentarios de código (−1,612 líneas)
- **4 archivos CORRUPTO:** `B8_CORRUPTO.md`, `B9_CORRUPTO.md`, `B10_CORRUPTO.md`, `B11_CORRUPTO.md`

### Seguridad
- `.env` eliminado del tracking de git; `.gitignore` actualizado
- Clave Firecrawl desvinculada del historial activo ⚠️ *Pendiente: revocar en https://www.firecrawl.dev/account*

---

## [2026-04-14] — Expansión de nodos y sistema de validación

### Añadido
- **15 registros nuevos** en nodos 003–010 — cobertura temática ampliada
- **Workflow `validar_datos.yml`:** validación automática de datos e integridad en cada push
- **Dashboard de estadísticas:** `docs/stats.json` con métricas del proyecto
- **Índice de búsqueda semántica:** `docs/search_index.json` (96 registros indexados)
- **GitHub Pages (`paginas.yml`):** portal de búsqueda web en `docs/index.html`
- **`tools/generar_estadisticas.py`:** genera métricas automáticas del proyecto
- **`tools/generar_indice_busqueda.py`:** genera índice para búsqueda web
- **`busqueda_web.yml`:** workflow CI para búsqueda automática de fuentes sin API key

### Cambiado
- Estructura de `datos/` reorganizada en subcarpetas (`hopelchen/`, `curated/`, `pdfs/`, `borradores/`)
- `src/analizador.py` y `src/utilidades.py` movidos a directorio `src/`
- PDFs movidos de raíz a `datos/pdfs/`
- README reescrito con descripción completa del proyecto, metodología y alcance

### Eliminado
- Herramientas de Firecrawl eliminadas (primera versión — completado el 2026-04-18)

---

## [2026-04-13] — Inicio del repositorio

### Añadido
- **Estructura inicial del proyecto** con scripts de análisis, datos de muestra, tests y documentación
- **`datos/curated/`:** repositorio bibliográfico inicial con 189 fuentes (`REPOSITORIO_BIBLIOGRAFICO.json`)
- **Nodos históricos iniciales** (001–008): JSONs de datos y preguntas abiertas
- **`src/analizador.py`:** analizador CLI para JSON, Markdown y PDF
- **`tools/generar_redaccion.py`:** genera redacción histórica estructurada por nodo
- **`tools/generar_sintesis.py`:** genera `SINTESIS_MAESTRA.md`
- **`tools/actualizar_vacios.py`:** genera `datos/VACIOS.md`
- **`tools/validar_datos.py`** y **`tools/validar_fechas.py`:** validación de integridad
- **`tools/buscar_fuentes_vacias.py`:** búsqueda web de fuentes (Wikipedia, DuckDuckGo, OpenLibrary)
- **`tools/rastrear_fuentes.py`:** rastreo en PARES, AGN, FamilySearch
- **`HIPOTESIS.md`:** hipótesis inicial del proyecto
- **`DOCUMENTO_FUNDACIONAL.md`:** registro del punto de origen
- **`MAPA_CAPAS.md`:** guía de navegación del repositorio
- **`ci.yml`:** CI con pruebas en Python 3.11 y 3.12
- **17 borradores aprobados** del libro en `datos/borradores/` (~38,420 palabras)

---

## Estado actual (2026-04-18)

| Indicador | Valor |
|---|---|
| Nodos históricos | 10 |
| Registros totales | 97 |
| Cobertura de fuentes | 100% |
| Fuentes catalogadas | 73 |
| Preguntas respondidas | 61 |
| Preguntas en proceso | 1 |
| Preguntas pendientes | 0 |
| Tests automáticos | 148 ✅ |
| Borradores aprobados | 17 (~154 páginas) |
