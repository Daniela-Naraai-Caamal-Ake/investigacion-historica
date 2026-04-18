# datos/curated/ — Guía de archivos

Este directorio contiene datos curados y repositorios bibliográficos del proyecto.
Algunos archivos son **activos** (usados por scripts) y otros son **archivos históricos**
(generados en sesiones anteriores, conservados como referencia).

---

## Fuente de verdad por tipo de dato

| Tipo | Archivo canónico | Quién lo usa |
|---|---|---|
| Fuentes bibliográficas | `fuentes.json` | Sistema de investigación (68 fuentes, IDs F### y FX###) |
| Personajes históricos | `01_personajes.json` | `tools/generar_redaccion.py` → `mapa/personajes.md` |
| Fuentes para scripts | `03_fuentes_bibliograficas.json` | `tools/generar_redaccion.py`, `src/analizador.py` |

---

## Archivos activos (usados por el código)

### `fuentes.json`
Catálogo JSON principal de fuentes. **68 entradas** con IDs `F001–F064` y `FX001–FX029`.
Es la referencia para trazabilidad de los nodos históricos.
→ Actualizar aquí cuando se agrega una fuente nueva.

### `01_personajes.json`
Base de datos de personajes históricos con linajes familiares.
Usado por `generar_redaccion.py` para generar `mapa/personajes.md`.
→ Actualizar aquí cuando se documenta un nuevo personaje.

### `03_fuentes_bibliograficas.json`
Fuentes organizadas por categoría (primarias, libros, PDFs, web, archivos pendientes).
Usado por `generar_redaccion.py` y `src/analizador.py` para el catálogo `fuentes/catalogo_fuentes.md`.
→ Actualizar aquí para agregar fuentes al catálogo generado automáticamente.

### `04_territorio_lengua_maya.json`
Toponimia maya, zonas arqueológicas, vocabulario verificado y registro legislativo 1861–2003.
Referencia para datos territoriales y lingüísticos.

### `05_hallazgos_investigacion.json`
Hallazgos y correcciones críticas verificadas. Incluye temas: menonitas, Leydy Pech,
política contemporánea. Útil para contrastar datos.

---

## Archivos de archivo histórico (no usados por scripts)

Conservados como referencia de sesiones de investigación anteriores.
**No modificar** — si se necesitan sus datos, incorporarlos a los archivos activos.

| Archivo | Contenido | Tamaño |
|---|---|---|
| `REPOSITORIO_BIBLIOGRAFICO.json` | Repositorio bibliográfico expandido | 111 KB |
| `REPOSITORIO_BIBLIOGRAFICO.md` | Versión Markdown del repositorio | 47 KB |
| `eventos3.json` | 61 eventos históricos con hilos narrativos | 66 KB |
| `02_cronologia_eventos.json` | Cronología de eventos (versión anterior) | 36 KB |
| `eventos_historicos.json` | Eventos históricos (versión mínima) | 2 KB |
| `personajes_eventos_expansion_v2.json` | Expansión de personajes y eventos (v2) | 22 KB |
| `personajes_historicos.json` | Personajes históricos (versión mínima) | 2 KB |
| `fuentes_bibliograficas.json` | Fuentes bibliográficas (versión mínima) | 2 KB |

---

## Flujo recomendado

```
Nueva fuente bibliográfica
  → Agregar a fuentes.json (para trazabilidad de nodos)
  → Agregar a 03_fuentes_bibliograficas.json (para catálogo generado)

Nuevo personaje histórico
  → Agregar a 01_personajes.json

Nueva evidencia de investigación
  → Agregar como registro en datos/hopelchen/HOPELCHEN_NODO_*.json
```
