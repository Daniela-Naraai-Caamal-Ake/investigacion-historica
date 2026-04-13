# Índice de Redacción Anotada — Hopelchén: 2000 años de historia

> Autora: Daniela Naraai Caamal Ake  
> Generado por: `tools/generar_redaccion.py`

Los archivos en `trabajo/periodos/` contienen la información extraída de los
datos fuente en bloques con **metadatos explícitos** (tipo, fecha, lugar,
personajes, cargos, fuentes rastreables).

Para agregar nueva información:
1. Edita el JSON en `datos/` o agrega un nuevo `HOPELCHEN_NODO_*.json`.
2. Ejecuta: `python tools/generar_redaccion.py`
3. El archivo de período correspondiente se regenera.

---

## Fuentes

| Archivo | Descripción |
|---|---|
| [`fuentes/catalogo_fuentes.md`](../fuentes/catalogo_fuentes.md) | Catálogo Chicago completo con IDs F### |

---

## Períodos históricos

| Archivo | Período | Fuente JSON |
|---|---|---|
| [Ocupación Prehispánica del Territorio de Hopelchén — Los Che](periodos/nodo-001-ocupacion-prehispanica-del-territorio-de.md) | ~300 a.C. — 1517 d.C. | `datos/HOPELCHEN_NODO_001_Ocupacion_Prehispanica.json` |
| [La Conquista Española en Los Chenes y la Fundación Colonial ](periodos/nodo-002-la-conquista-espanola-en-los-chenes-y-la.md) | 1517 — 1669 | `datos/HOPELCHEN_NODO_002_Conquista_Colonial.json` |
| [Colonia Tardía, Independencia, Guerra de Castas y el Porfiri](periodos/nodo-003-colonia-tardia-independencia-guerra-de.md) | 1670 — 1910 | `datos/HOPELCHEN_NODO_003_ColoniaTardia_Porfiriato.json` |
| [Revolución, Lucha Antiagraria, Reforma Agraria y la Economía](periodos/nodo-004-revolucion-lucha-antiagraria-reforma-a.md) | 1910 — 1970 | `datos/HOPELCHEN_NODO_004_Revolucion_Chicle.json` |
| [Hopelchén Contemporáneo (1970–2026): Menonitas, Agroindustri](periodos/nodo-005-hopelchen-contemporaneo-1970-2026-men.md) | 1970 — 2026 | `datos/HOPELCHEN_NODO_005_Contemporaneo.json` |
| [La Genealogía del Poder Político Local en Hopelchén (1959–20](periodos/nodo-006-la-genealogia-del-poder-politico-local-e.md) | 1959 — 2026 | `datos/HOPELCHEN_NODO_006_PoderPolitico_Local.json` |
| [Rutas, Territorio y Control del Espacio en Hopelchén (1517–2](periodos/nodo-007-rutas-territorio-y-control-del-espacio.md) | 1517 — 2026 | `datos/HOPELCHEN_NODO_007_Rutas_Territorio.json` |
| [Demografía e Historia de la Población en Hopelchén (300 a.C.](periodos/nodo-008-demografia-e-historia-de-la-poblacion-en.md) | 300 a.C. — 2026 | `datos/HOPELCHEN_NODO_008_Demografia.json` |

---

## Mapa de conexiones

| Archivo | Descripción |
|---|---|
| [`mapa/personajes.md`](../mapa/personajes.md) | Personajes históricos con fuentes rastreables |

---

## Agregar excerpts manualmente

Para agregar un bloque en un período existente, copia la plantilla:

```markdown
### Bloque XX — Título del bloque

| Campo | Valor |
|---|---|
| **Tipo** | evento / personaje / contexto / hilo |
| **Fecha / Período** | YYYY o rango |
| **Lugar** | Hopelchén, Campeche |
| **Personajes** | Nombre (Cargo) |
| **Cargos** | — |
| **Fuente(s)** | [F001](../fuentes/catalogo_fuentes.md#f001) |
| **Origen** | `datos/archivo.json` |

> "Cita textual o paráfrasis directa del texto fuente."

_Origen: Autor, Título. Ciudad: Editorial, Año._

---
```
