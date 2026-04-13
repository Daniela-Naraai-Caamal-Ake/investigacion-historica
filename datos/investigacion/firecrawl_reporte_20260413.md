# Reporte Firecrawl — Ampliación de Nodos

> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  
> Fecha de ejecución: 2026-04-13  
> API: Firecrawl (`fc-cbcaa6ee1fc6425192732ccb3b20c82c`)  
> Herramienta: `tools/validar_citas_firecrawl.py --modo ampliar`

---

## Resumen ejecutivo

- **total_busquedas**: 14
- **urgentes**: 8 (preguntas VACIOS.md: P002-01, P003-01, P004-01, P006-01, P006-07, P006-09, P007-01, P008-01)
- **generales**: 6 (una por nodo: 001, 002, 003, 005, 006, 008)
- **estado**: Configurado — ejecutar con `python tools/validar_citas_firecrawl.py --modo ampliar`

---

## 3. Búsquedas planificadas para Ampliación de Nodos

### Preguntas urgentes de VACIOS.md

#### [P002-01] — Nodo 002
*Query:* `congregación Hopelchén 1621 documento colonial fundación pueblo Yucatán AGI`

#### [P003-01] — Nodo 003
*Query:* `Pedro Advíncula Lara hacienda Holcatzin Santa Rita Hopelchén Porfiriato título propiedad`

#### [P004-01] — Nodo 004
*Query:* `hacendados Hopelchén lucha antiagraria posrevolución Campeche 1920 1940`

#### [P006-01] — Nodo 006
*Query:* `genealogía Aranda Calderón Baranda alcalde Hopelchén poder político Campeche familia`

#### [P006-07] — Nodo 006
*Query:* `Emilio Lara Calderón alcalde Hopelchén 2021 Pedro Advíncula Lara hacendado porfiriano genealogía`

#### [P006-09] — Nodo 006
*Query:* `Julio Sansores presidente municipal Hopelchén Layda Sansores San Román gobernadora Campeche parentesco`

#### [P007-01] — Nodo 007
*Query:* `Pacheco Blanco 1928 Peña 1942 Los Chenes economía Campeche historia`

#### [P008-01] — Nodo 008
*Query:* `INEGI archivo histórico censo población Hopelchén Campeche 1900 1910 1921 1930 1940`

---

### Búsquedas generales por nodo

#### [001] Hallazgos arqueológicos recientes en Los Chenes / Hopelchén
*Query:* `Hopelchén arqueología prehispánica zona arqueológica Los Chenes hallazgos recientes`

#### [002] Encomiendas y evangelización franciscana en Los Chenes, siglo XVI
*Query:* `encomienda Los Chenes siglo XVI Yucatán tributación maya franciscanos evangelización`

#### [003] Sistema de haciendas azucareras y deuda servil en Campeche, siglo XIX
*Query:* `haciendas azucareras Campeche siglo XIX luneros deuda servil colonialismo`

#### [005] Llegada de menonitas a Hopelchén 1987 e impacto en la tierra
*Query:* `menonitas Hopelchén Campeche llegada 1987 tierra deforestación biodiversidad`

#### [006] Presidentes municipales de Hopelchén 1987-2000
*Query:* `presidentes municipales Hopelchén Campeche 1987 2000 historia política local`

#### [008] Datos demográficos actuales de Hopelchén — Censo INEGI 2020
*Query:* `demografía municipio Hopelchén Campeche población maya 2020 censo INEGI`

---

*Para ejecutar las búsquedas en un entorno con internet:*
```bash
export FIRECRAWL_API_KEY=fc-cbcaa6ee1fc6425192732ccb3b20c82c
python tools/validar_citas_firecrawl.py --modo ampliar
```
