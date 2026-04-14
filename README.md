# Investigación Histórica — Hopelchén / Los Chenes

> **Dos Mil Años en Silencio** — Archivo vivo de investigación histórica  
> Autora: **Daniela Naraai Caamal Ake**  
> Municipio de Hopelchén, región de Los Chenes, Campeche, México  
> Estado: *en curso — proyecto abierto desde marzo 2026*

---

## Descripción del proyecto

Este repositorio es el archivo de trabajo de *Dos Mil Años en Silencio*, un libro de historia en desarrollo que recorre la historia del municipio de **Hopelchén** y la región de **Los Chenes** (Campeche, México) desde aproximadamente 300 a.C. hasta 2026.

El proyecto surge de un vacío bibliográfico concreto: no existe, hasta donde se ha podido documentar, un libro de historia comprehensivo dedicado a Hopelchén que integre su ocupación prehispánica, la conquista colonial, el período republicano, el ciclo chiclero, el siglo XX y el presente en un solo relato con rigor académico y fuentes rastreables.

La investigación está organizada como un **archivo vivo**: los datos se registran, corrigen y amplían en cada sesión de trabajo, y todos los cambios quedan fechados. El repositorio no es el producto final — es la carpintería del libro.

---

## Hipótesis central

> *"El control de Hopelchén — sobre el conocimiento, la tierra, el poder político y el cuerpo de las comunidades mayas — ha sido ejercido históricamente por élites de poder externas que cambian de forma en cada era pero mantienen la misma estructura de despojo. El linaje maya ha sido el objeto constante de ese control."*
>
> — Hipótesis v4 (versión canónica). Ver historial completo en [`HIPOTESIS.md`](HIPOTESIS.md).

La pregunta que atraviesa todo el libro: *¿de quién es esta tierra?*

---

## Objetivos

1. **Documentar** la historia de Hopelchén desde sus raíces mayas hasta el presente en un solo archivo coherente y con fuentes.
2. **Trazar el patrón** de control territorial y político a través de los siglos, identificando continuidades y rupturas.
3. **Registrar los vacíos** bibliográficos y de archivo con igual rigor que los datos confirmados.
4. **Producir un libro** accesible (*Dos Mil Años en Silencio*, 21 capítulos) que pueda estar en bibliotecas locales y llegar a lectores sin formación académica especializada.

---

## Alcance temporal y geográfico

| Dimensión | Descripción |
|---|---|
| **Período** | ~300 a.C. — 2026 d.C. (aprox. 2 300 años) |
| **Territorio principal** | Municipio de Hopelchén, Campeche |
| **Región ampliada** | Los Chenes (zona arqueológica y cultural que incluye Hochob, Dzibilnocac, Santa Rosa Xtampak) |
| **Contexto** | Sureste de México; referencias a Yucatán, Quintana Roo y Ciudad de México cuando afectan directamente la historia local |
| **Nodos documentados** | 8 nodos temáticos (ver tabla de períodos abajo) |
| **Fuentes catalogadas** | Ver [`fuentes/catalogo_fuentes.md`](fuentes/catalogo_fuentes.md) |
| **Preguntas abiertas** | 62 registradas en [`datos/VACIOS.md`](datos/VACIOS.md) |

---

## Metodología

### Principios generales

- **Fuente primaria antes que secundaria.** Siempre que es posible, la investigación trabaja con documentos originales: actas notariales, censos, mapas históricos, crónicas coloniales, expedientes judiciales. Las fuentes secundarias orientan pero no sustituyen.
- **Trazabilidad total.** Cada dato tiene un ID de fuente (`F001`, `F012`, etc.) registrado en el catálogo de fuentes. Cualquier afirmación es rastreable hasta su origen.
- **Distinción entre dato e interpretación.** Cada registro distingue entre lo que dice la fuente y lo que la investigadora concluye de ella.
- **Registro de vacíos.** Lo que no se sabe es tan importante como lo que se sabe. [`datos/VACIOS.md`](datos/VACIOS.md) documenta todas las preguntas abiertas con estado y prioridad.
- **Versión viva.** El proyecto no tiene fecha de cierre. Cada sesión puede agregar datos, corregir errores o reabrir preguntas. Los cambios quedan registrados.

### Sistema de citas

- Formato **Chicago**: `Apellido, Nombre. *Título*. Ciudad: Editorial, Año.`
- IDs de fuente: `[F001]`, `[F012]`, etc. → remiten a [`fuentes/catalogo_fuentes.md`](fuentes/catalogo_fuentes.md)
- Fuentes digitales: URL + fecha de consulta
- Memoria oral: identificada explícitamente como tal

### Organización por nodos temáticos

La historia no es lineal. El proyecto se organiza en **8 nodos temáticos** que pueden leerse en paralelo, todos conectados por la hipótesis central. Ver detalle en la sección de períodos.

### Posición de la autora

Daniela Naraai Caamal Ake es originaria de Hopelchén. Eso otorga acceso a memorias y perspectivas que una investigadora externa no tendría, y también implica puntos ciegos y afectos que se declaran abiertamente. Esta investigación no habla *por* las comunidades mayas: intenta construir un registro que ellas también puedan usar. Ver declaración completa en [`DOCUMENTO_FUNDACIONAL.md`](DOCUMENTO_FUNDACIONAL.md).

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
| [`DOCUMENTO_FUNDACIONAL.md`](DOCUMENTO_FUNDACIONAL.md) | **Declaración de origen** — por qué empezó este proyecto, vacío bibliográfico, hipótesis inicial, principios éticos y metodológicos |
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

### Validar citas y ampliar nodos con Firecrawl

Herramienta integral que valida las URLs del catálogo, busca fuentes para
registros sin cita y lanza búsquedas para ampliar los nodos:

```bash
# Requiere: FIRECRAWL_API_KEY en .env o variable de entorno
# Obtén una clave gratuita en https://www.firecrawl.dev

python tools/validar_citas_firecrawl.py               # Todo (validar + fuentes + ampliar)
python tools/validar_citas_firecrawl.py --modo validar # Solo validar URLs del catálogo
python tools/validar_citas_firecrawl.py --modo fuentes # Solo buscar fuentes faltantes
python tools/validar_citas_firecrawl.py --modo ampliar # Solo ampliar nodos con búsquedas
python tools/validar_citas_firecrawl.py --nodo 009     # Filtrar por nodo específico
python tools/validar_citas_firecrawl.py --limite 10    # Limitar a N búsquedas por modo
```

Salidas en `datos/investigacion/`:
- `firecrawl_validacion_YYYYMMDD.json` — Resultados completos
- `firecrawl_reporte_YYYYMMDD.md` — Reporte legible en Markdown

También disponible el rastreador de fuentes en archivos digitales públicos:

```bash
python tools/rastrear_fuentes.py               # Todos los módulos
python tools/rastrear_fuentes.py --modulo firecrawl
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Información de contacto y colaboración

**Autora:** Daniela Naraai Caamal Ake  
**Proyecto:** *Dos Mil Años en Silencio* — Investigación histórica de Hopelchén, Campeche  
**Repositorio:** [github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica](https://github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica)

### Cómo contribuir

Este es un proyecto de investigación personal, pero las colaboraciones son bienvenidas en las siguientes formas:

| Tipo de contribución | Cómo hacerlo |
|---|---|
| **Aportar fuentes** | Abre un *issue* con el título "Fuente: [descripción]" e incluye la referencia completa en formato Chicago |
| **Señalar errores** | Abre un *issue* con el título "Error: [descripción]" y la ubicación exacta del dato incorrecto |
| **Preguntas de investigación** | Abre un *issue* con el título "Pregunta: [nodo]" — se evalúa para agregar a [`datos/VACIOS.md`](datos/VACIOS.md) |
| **Correcciones de datos JSON** | Envía un *pull request* editando el archivo correspondiente en `datos/hopelchen/` |
| **Testimonios orales** | Contacto directo (ver abajo) — la memoria oral requiere contexto y consentimiento explícito |

### Principios para colaborar

- Toda contribución debe incluir fuente citable o ser identificada explícitamente como memoria oral.
- Las correcciones de datos deben señalar el origen del error y la fuente alternativa.
- Las aportaciones que afecten la hipótesis central deben argumentarse en relación con la evidencia existente.
- Este proyecto respeta la privacidad y dignidad de las personas y comunidades mencionadas. No se publican datos sensibles sin consentimiento.

### Uso del material

El contenido de este repositorio es trabajo de investigación en curso. Si utilizas datos, citas o estructura de este archivo en trabajos propios, cita el repositorio:

> Caamal Ake, Daniela Naraai. *Investigación histórica de Hopelchén / Los Chenes — Archivo vivo*. GitHub, 2026. https://github.com/Daniela-Naraai-Caamal-Ake/investigacion-historica

---

*Archivo vivo — iniciado en marzo de 2026. La historia de Hopelchén merece ser contada completa.*

