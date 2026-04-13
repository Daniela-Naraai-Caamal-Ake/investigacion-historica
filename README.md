# Investigación Histórica — Hopelchén / Los Chenes

*Archivo Vivo — Investigación histórica de Hopelchén, Campeche.*  
*Autora: Daniela Naraai Caamal Ake*

---

## Navegación principal

| Carpeta / Archivo | Contenido |
|---|---|
| [`trabajo/indice.md`](trabajo/indice.md) | **Índice de períodos históricos** — empieza aquí |
| [`fuentes/catalogo_fuentes.md`](fuentes/catalogo_fuentes.md) | Catálogo Chicago completo con IDs `F001…` |
| [`mapa/personajes.md`](mapa/personajes.md) | Mapa de personajes con fuentes rastreables |
| [`datos/`](datos/) | Datos fuente originales (JSON, MD, PDF) — no modificar |

### Flujo de investigación (archivos del marco teórico)

| Archivo | Qué es |
|---|---|
| [`HIPOTESIS.md`](HIPOTESIS.md) | Hipótesis canónica del proyecto + versiones históricas V1→V4 + patrón documentado por nodo |
| [`datos/VACIOS.md`](datos/VACIOS.md) | Mapa unificado de preguntas abiertas — todas las preguntas de los 8 nodos en una tabla con estado y prioridad |
| [`datos/FICHAS_EJEMPLO.md`](datos/FICHAS_EJEMPLO.md) | Fichas de evidencia con campo `hipotesis_que_afecta` — un ejemplo completo por nodo |

### Períodos históricos (`trabajo/periodos/`)

| Archivo | Período |
|---|---|
| [Nodo 001 — Ocupación Prehispánica](trabajo/periodos/nodo-001-ocupacion-prehispanica-del-territorio-de.md) | ~300 a.C. — 1517 d.C. |
| [Nodo 002 — Conquista Colonial](trabajo/periodos/nodo-002-la-conquista-espanola-en-los-chenes-y-la.md) | 1517 — 1669 |
| [Nodo 003 — Colonia Tardía / Porfiriato](trabajo/periodos/nodo-003-colonia-tardia-independencia-guerra-de.md) | 1670 — 1910 |
| [Nodo 004 — Revolución y Chicle](trabajo/periodos/nodo-004-revolucion-lucha-antiagraria-reforma-a.md) | 1910 — 1970 |
| [Nodo 005 — Contemporáneo](trabajo/periodos/nodo-005-hopelchen-contemporaneo-1970-2026-men.md) | 1970 — 2026 |
| [Nodo 006 — Poder Político Local](trabajo/periodos/nodo-006-la-genealogia-del-poder-politico-local-e.md) | 1959 — 2026 |
| [Nodo 007 — Rutas y Territorio](trabajo/periodos/nodo-007-rutas-territorio-y-control-del-espacio.md) | 1517 — 2026 |
| [Nodo 008 — Demografía](trabajo/periodos/nodo-008-demografia-e-historia-de-la-poblacion-en.md) | 300 a.C. — 2026 |

---

## Cómo agregar información nueva

### Opción A — Actualizar datos JSON y regenerar (recomendado)

1. Edita o crea un archivo en `datos/hopelchen/` (ej. `datos/hopelchen/HOPELCHEN_NODO_001_Ocupacion_Prehispanica.json`).
2. Ejecuta:
   ```bash
   python tools/generar_redaccion.py
   ```
3. Los archivos en `trabajo/periodos/`, `fuentes/catalogo_fuentes.md` y `mapa/personajes.md` se regeneran automáticamente.

### Opción B — Agregar un bloque manualmente

Copia esta plantilla en cualquier archivo de `trabajo/periodos/`:

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

### Cómo citar fuentes

- Usa IDs `[F001]`, `[F012]`, etc. que remiten a [`fuentes/catalogo_fuentes.md`](fuentes/catalogo_fuentes.md).
- Formato Chicago: `Apellido, Nombre. *Título*. Ciudad: Editorial, Año.`
- Para fuentes web: incluye URL y fecha de consulta.

---

## Estructura del repositorio

```
investigacion-historica/
├── src/
│   ├── analizador.py                # Analizador CLI (buscar, filtrar, reportar)
│   └── utilidades.py                # Funciones auxiliares compartidas
├── trabajo/
│   ├── indice.md                    # Índice de períodos — empieza aquí
│   └── periodos/                    # Un archivo .md por período/nodo
├── fuentes/
│   ├── catalogo_fuentes.md          # Catálogo Chicago con IDs F###
│   └── pdf/                         # PDFs fuente (locales)
├── mapa/
│   └── personajes.md                # Personajes con fuentes rastreables
├── tools/
│   └── generar_redaccion.py         # Script generador (idempotente)
├── datos/                           # Fuentes originales (no modificar)
│   ├── curated/                     # Datos canónicos: personajes, eventos, fuentes
│   │   ├── 01_personajes.json
│   │   ├── 02_cronologia_eventos.json
│   │   ├── 03_fuentes_bibliograficas.json
│   │   ├── REPOSITORIO_BIBLIOGRAFICO.json / .md
│   │   └── *.json
│   ├── hopelchen/                   # Nodos y preguntas históricas de Hopelchén
│   │   ├── HOPELCHEN_NODO_001-008.json
│   │   ├── HOPELCHEN_PREGUNTAS_001-008.json
│   │   └── *.json
│   ├── borradores/                  # Borradores de capítulos (A*.md, B*.md)
│   ├── archivo_vivo/                # Archivos AV_*, ARCHIVO_VIVO_*, av_*
│   ├── investigacion/               # Reportes de sesiones de investigación
│   ├── logs/                        # Logs de sesión y reportes de proceso
│   └── pdfs/                        # PDFs fuente en datos/
├── tests/
├── requirements.txt
└── README.md
```

---

## Herramientas Python

### Regenerar redacción anotada

```bash
python tools/generar_redaccion.py
```

### Analizar archivos de datos

```bash
python src/analizador.py
python src/analizador.py datos/curated/01_personajes.json
python src/analizador.py --buscar "Hopelchén"
python src/analizador.py --reporte
```

### Ejecutar pruebas

```bash
python -m unittest tests/test_analizador.py -v
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

