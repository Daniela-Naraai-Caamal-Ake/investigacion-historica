# MAPA DE CAPAS — Dos Mil Años en Silencio

> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  
> Autora: **Daniela Naraai Caamal Ake**  
> ⚙ Ver `tools/generar_sintesis.py` para regenerar la síntesis completa  
> Última actualización: 2026-04-14

---

## Cómo leer este mapa

El proyecto está organizado en **5 capas** de profundidad creciente.
Empieza por la Capa 0 para orientarte, y profundiza según lo que necesites.

```
CAPA 0 ── Orientación general (README + este archivo)
  │
  ├── CAPA 1 ── Síntesis completa (SINTESIS_MAESTRA.md)
  │               Todo en un lugar: nodos, cronología, personajes, vacíos
  │
  ├── CAPA 2 ── Por nodo temático (trabajo/periodos/)
  │               Redacción detallada de cada período histórico
  │
  ├── CAPA 3 ── Vacíos / preguntas abiertas (datos/VACIOS.md)
  │               62 preguntas: 41 pendientes, 19 parciales, 1 respondida
  │
  ├── CAPA 4 ── Fuentes bibliográficas (fuentes/catalogo_fuentes.md)
  │               Catálogo Chicago completo con IDs F###
  │
  └── CAPA 5 ── Datos brutos / archivo de trabajo
                  datos/hopelchen/, datos/archivo_vivo/, datos/borradores/
```

---

## CAPA 0 — Orientación General

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Descripción del proyecto, estado, cómo contribuir |
| `HIPOTESIS.md` | Hipótesis central de investigación |
| `DOCUMENTO_FUNDACIONAL.md` | Marco teórico y declaración de propósito |
| `datos/archivo_vivo/QUÉ ES ARCHIVO VIVO.md` | Manifiesto del proyecto |

---

## CAPA 1 — Síntesis Completa

**`SINTESIS_MAESTRA.md`** — el documento único que consolida todo.

Contiene:
- Hipótesis central
- Los 10 nodos con todos sus registros
- Cronología maestra (ordenada cronológicamente)
- Personajes clave y genealogías
- Mapa de vacíos con prioridades
- Catálogo de fuentes (extracto)
- Estado de los borradores

> Regenerar: `python tools/generar_sintesis.py`

---

## CAPA 2 — Por Nodo Temático

Estado de completitud de cada nodo (registros con fuente verificada):

| Nodo | Período | Completitud | Urgentes | Archivo de trabajo |
|------|---------|-------------|----------|--------------------|
| **001** | ~300 a.C. — 1517 | ████████████ 100% | 0 | [nodo-001](trabajo/periodos/nodo-001-ocupacion-prehispanica-del-territorio-de.md) |
| **002** | 1517 — 1669 | ████████████ 100% | 1 🚨 | [nodo-002](trabajo/periodos/nodo-002-la-conquista-espanola-en-los-chenes-y-la.md) |
| **003** | 1670 — 1910 | ████████████ 100% | 1 🚨 | [nodo-003](trabajo/periodos/nodo-003-colonia-tardia-independencia-guerra-de.md) |
| **004** | 1910 — 1970 | █████████░░░  80% | 1 🚨 | [nodo-004](trabajo/periodos/nodo-004-revolucion-lucha-antiagraria-reforma-a.md) |
| **005** | 1970 — 2026 | ███░░░░░░░░░  28% | 1 🚨 | [nodo-005](trabajo/periodos/nodo-005-hopelchen-contemporaneo-1970-2026-men.md) |
| **006** | 1959 — 2026 | █████████░░░  77% | 4 🚨 | [nodo-006](trabajo/periodos/nodo-006-la-genealogia-del-poder-politico-local-e.md) |
| **007** | 1517 — 2026 | ████░░░░░░░░  30% | 1 🚨 | [nodo-007](trabajo/periodos/nodo-007-rutas-territorio-y-control-del-espacio.md) |
| **008** | 300 a.C. — 2026 | ██████░░░░░░  45% | 1 🚨 | [nodo-008](trabajo/periodos/nodo-008-demografia-e-historia-de-la-poblacion-en.md) |
| **009** | 1669 — 2026 | ██████████░░  81% | 0 | [nodo-009](trabajo/periodos/nodo-009-resistencia-y-agencia-maya-en-hopelchen.md) |
| **010** | 300 a.C. — 2026 | ███████████░  88% | 0 | [nodo-010](trabajo/periodos/nodo-010-conocimiento-y-cultura-maya-en-los-chene.md) |

**Nodos prioritarios para completar:** 005 (28%) → 007 (30%) → 008 (45%)

### Datos de soporte por nodo

| Archivo | Contenido | Nodo relacionado |
|---------|-----------|-----------------|
| `datos/hopelchen/menonitas_hopelchen.json` | 11 colonias, deforestación, acuerdo Semarnat 2021 | 005 |
| `datos/hopelchen/legisladores_hopelchen_1861-2003.json` | 61 legisladores | 006 |
| `datos/hopelchen/leydy_pech_perfil.json` | Perfil completo: Maya Ka'an, Koolel-Kab, CIDH | 009 |
| `datos/hopelchen/base_historica_hopelchen.json` | Base consolidada | Todos |
| `datos/archivo_vivo/AV_PERSONAS.md` | Genealogías: Lara, Baqueiro, Barrera, Molina | 003/006 |
| `datos/archivo_vivo/AV_MAYA.md` | Cultura y conocimiento maya | 001/010 |
| `datos/archivo_vivo/AV_FUENTES.md` | Fuentes adicionales | Todos |
| `datos/archivo_vivo/AV_HILOS.md` | Hilos narrativos transversales | Todos |

---

## CAPA 3 — Vacíos / Preguntas Abiertas

**`datos/VACIOS.md`** — generado automáticamente desde los JSON de preguntas.

> Regenerar: `python tools/actualizar_vacios.py`

### Resumen del estado

| Estado | Cantidad | Significado |
|--------|----------|-------------|
| 🔴 PENDIENTE | **41** | Sin respuesta, sin fuente |
| 🟡 EN PROCESO | **1** | Investigación activa |
| 🟠 RESPONDIDA PARCIALMENTE | **19** | Datos parciales, falta confirmar |
| 🟢 RESPONDIDA | **1** | Completa con fuente primaria |
| **TOTAL** | **62** | |

### Preguntas URGENTES (cuellos de botella)

Estas 10 preguntas bloquean capítulos enteros si no se responden:

| ID | Nodo | Pregunta (resumen) | Dónde buscar |
|----|------|--------------------|--------------|
| **P002-01** | 002 | Documento original de fundación de Hopelchén 1621 | AGI Sevilla / AGN México |
| **P003-01** | 003 | Pedro Advíncula Lara: adquisición haciendas Holcatzin y Santa Rita | Registro Público Campeche |
| **P004-01** | 004 | Hacendados hopelcheneños en la 'lucha antiagraria' | Archivo Agrario Nacional |
| **P005-05** | 005 | Libro de Aranda González (1985) sobre historia política | Biblioteca Campeche |
| **P006-01** | 006 | Conexión genealógica Hiram Aranda ↔ Mario Aranda González | Registro Civil Campeche |
| **P006-08** | 006 | Presidente municipal 1987-1992 (período llegada menonitas) | Periódico Oficial Campeche |
| **P006-09** | 006 | Parentesco Julio Sansores Sansores ↔ Layda Sansores | Wikipedia / IEEC |
| **P006-10** | 006 | Cambios de uso de suelo autorizados 1987-2024 | RAN / Semarnat |
| **P007-01** | 007 | Obras de Pacheco Blanco (1928) y Peña (1942) sobre Hopelchén | Biblioteca UNAM / Campeche |
| **P007-03** | 007 | Archivo Municipal de Hopelchén — ¿existe? ¿dónde? | Municipio directamente |

---

## CAPA 4 — Fuentes Bibliográficas

**`fuentes/catalogo_fuentes.md`** — catálogo en formato Chicago con IDs `F###`.

**`fuentes/mapa_citas.md`** — mapa de qué fuentes se citan dónde.

Herramienta de rastreo: `python tools/rastrear_fuentes.py`

### Fuentes de alta prioridad (no consultadas aún)

| Fuente | Dónde | Relacionada con |
|--------|-------|-----------------|
| AGI — Audiencia de México, Ramo Congregaciones | pares.mcu.es | P002-01, P002-02 |
| AGN México — Ramo Indios, Ramo Mercedes | gob.mx/agn | P002-01, P003-01 |
| Registro Público de la Propiedad de Campeche | Campeche | P003-01 |
| Periódico Oficial del Estado de Campeche (1987-1993) | periodicooficial.campeche.gob.mx | P006-08 |
| IEEC — registros electorales municipales | ieec.org.mx | P006-02, P006-08 |
| FamilySearch — Censo 1930 Hopelchén | familysearch.org | P008-01, P008-02 |
| Schüren 2003 (libro completo) | IAI Berlín / préstamo UNAM | P007-04 |
| Aranda González 1985 (historia local Hopelchén) | Biblioteca Campeche | P005-05 |

---

## CAPA 5 — Datos Brutos y Archivo de Trabajo

### Estructura de datos canónicos (fuente de verdad)

```
datos/hopelchen/
  HOPELCHEN_NODO_001-010_*.json     ← 10 nodos temáticos (FUENTE CANÓNICA)
  HOPELCHEN_PREGUNTAS_001-009_*.json ← 62 preguntas de investigación
  base_historica_hopelchen.json
  hopelchen_cronologia_integrada.json
  legisladores_hopelchen_1861-2003.json
  leydy_pech_perfil.json
  menonitas_hopelchen.json
```

### Archivos de contexto (lectura, no modificar sin motivo)

```
datos/archivo_vivo/
  ARCHIVO_VIVO_MAESTRO_FINAL.json   ← master file (versión actual)
  AV_NUCLEO.md                       ← instrucciones operativas del agente
  AV_PERSONAS.md                     ← genealogías
  AV_MAYA.md                         ← cultura maya
  AV_FUENTES.md                      ← fuentes adicionales
  AV_HILOS.md                        ← hilos narrativos
  AV_CONTEXTO.md                     ← contexto editorial
  av_cronologia.json                 ← 87 eventos en cronología
  av_nucleo.json                     ← 20 personajes + familias
```

### Borradores (28 archivos)

```
datos/borradores/
  A1-A6.md         ← Bloque A (Introducción / primeros capítulos)
  B1-B12.md        ← Bloque B (capítulos principales)
  B-*.md           ← Borradores de personajes específicos
  PRÓLOGO.md
```

> ⚠ Algunos borradores (B8_CORRUPTO, B9_CORRUPTO, B10_CORRUPTO, B11_CORRUPTO)
> están marcados como corruptos. Ver `datos/investigacion/rescate_corruptos_2026-03-31.json`
> para el estado del rescate.

### Registros de investigación

```
datos/investigacion/
  firecrawl_reporte_20260413.md      ← reporte de búsquedas Firecrawl
  firecrawl_resultados_20260413.json ← resultados brutos
  fuentes_vacias_20260413.json       ← registros sin fuente detectados
  hallazgos_sesion_2026-03-30.json   ← hallazgos de sesión específica
  riesgos_pendientes.md              ← riesgos activos
```

---

## Próximas fases recomendadas

### Fase A — Completar datos faltantes (prioridad máxima)
1. **Nodo 005** (28%): Agregar fuentes a registros 005-A, 005-B, 005-C, 005-D, 005-E
2. **Nodo 007** (30%): Agregar fuentes a registros 007-A, 007-C, 007-D, 007-E, 007-F, 007-G
3. **Nodo 008** (45%): Agregar fuentes a registros 008-A, 008-B, 008-C, 008-H

### Fase B — Resolver vacíos urgentes
1. Buscar en Periódico Oficial Campeche: presidente municipal 1987-1992 (P006-08)
2. Consultar IEEC: continuidad genealógica Aranda (P006-01)
3. Localizar libro Aranda González 1985 (P005-05) — clave para todo el nodo 006

### Fase C — Rescate de borradores corruptos
1. Ver `datos/investigacion/rescate_corruptos_2026-03-31.json`
2. Intentar recuperar B8, B9, B10, B11

### Fase D — Redacción
1. Nodos 001, 002, 003 están al 100% — listos para redacción final
2. Nodo 009 (81%) y 010 (88%) — casi listos
3. Nodos 004 (80%), 006 (77%) — revisar preguntas urgentes antes de redactar

---

*Archivo Vivo — Hopelchén, Los Chenes, Campeche*  
*Daniela Naraai Caamal Ake — 2026*
