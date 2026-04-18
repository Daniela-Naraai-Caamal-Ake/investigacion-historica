# Investigación histórica de Hopelchén (Los Chenes)

Este repositorio es el **archivo de trabajo** del proyecto *Dos Mil Años en Silencio* de Daniela Naraai Caamal Ake.

## Propósito central

Construir, con fuentes rastreables, una historia integral de Hopelchén y Los Chenes para convertirla en un libro accesible.

En términos simples, este repositorio existe para:

1. **Guardar evidencia histórica** (datos y fuentes).
2. **Ordenar preguntas abiertas** (vacíos de investigación).
3. **Transformar datos en redacción** (borradores por nodo/período).

---

## Qué encontrarás aquí

- `datos/hopelchen/` → base canónica (nodos y preguntas).
- `trabajo/periodos/` → redacción por nodo histórico.
- `fuentes/catalogo_fuentes.md` → catálogo bibliográfico con IDs `F###`.
- `datos/VACIOS.md` → preguntas pendientes y estado.
- `SINTESIS_MAESTRA.md` → consolidado general del proyecto.
- `datos/borradores/` → capítulos del libro en preparación.
- `docs/` → índice de búsqueda y estadísticas del proyecto.

Si solo vas a leer el proyecto, empieza por:

1. `README.md` (este archivo)
2. `SINTESIS_MAESTRA.md`
3. `trabajo/indice.md`

---

## Configuración inicial

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno (si es necesario)
cp .env.example .env
# Edita .env y agrega las variables que requieras
```

> ⚠ **Nunca subas el archivo `.env` al repositorio.** Ya está en `.gitignore`.

---

## Flujo mínimo de trabajo

### 1) Editar datos
Trabaja sobre los JSON en `datos/hopelchen/`.

### 2) Regenerar redacción y síntesis
```bash
python tools/generar_redaccion.py
python tools/generar_sintesis.py
python tools/actualizar_vacios.py
```

### 3) Validar
```bash
python tools/validar_datos.py
python tools/validar_fechas.py
python -m unittest discover -s tests -v
```

---

## Comandos esenciales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Analizador general (JSON/MD/PDF)
python src/analizador.py

# Síntesis maestra
python tools/generar_sintesis.py

# Actualizar vacíos de investigación
python tools/actualizar_vacios.py

# Estadísticas del proyecto
python tools/generar_estadisticas.py

# Índice de búsqueda web (docs/)
python tools/generar_indice_busqueda.py

# Buscar nuevas fuentes en la web
python tools/buscar_fuentes_vacias.py

# Validar y ampliar citas existentes
python tools/validar_citas.py

# Rastrear fuentes en archivos digitales (PARES, AGN, FamilySearch...)
python tools/rastrear_fuentes.py
```

---

## Estructura del repositorio

```text
investigacion-historica/
├── datos/
│   ├── hopelchen/          # Nodos y preguntas (JSON canónico)
│   ├── borradores/         # Capítulos del libro en preparación
│   ├── archivo_vivo/       # Contexto narrativo y personajes
│   ├── curated/            # Datos curados y bibliografía
│   └── pdfs/               # Fuentes primarias digitalizadas
├── trabajo/
│   ├── indice.md           # Índice general de la redacción
│   └── periodos/           # Un archivo .md por nodo histórico
├── fuentes/
│   ├── catalogo_fuentes.md # Catálogo completo con IDs F###
│   └── mapa_citas.md       # Mapa de uso de fuentes por nodo
├── docs/
│   ├── index.html          # Portal de búsqueda web
│   ├── search_index.json   # Índice de 96 registros
│   └── stats.json          # Estadísticas actualizadas
├── tools/                  # Scripts de generación y validación
├── src/                    # Analizador CLI y utilidades
├── tests/                  # 122 pruebas automáticas
├── SINTESIS_MAESTRA.md     # Consolidado general del proyecto
├── HIPOTESIS.md            # Hipótesis central (v5)
├── DOCUMENTO_FUNDACIONAL.md
└── MAPA_CAPAS.md           # Guía de navegación
```

---

## Estado actual del proyecto (2026-04-18)

| Indicador | Valor |
|---|---|
| Nodos históricos | 10 |
| Registros totales | 96 |
| Cobertura de fuentes | 100% |
| Preguntas respondidas | 61 |
| Preguntas en proceso | 1 |
| Preguntas pendientes | **0** |
| Fuentes catalogadas | 64 |
| Tests automáticos | 122 ✅ |

---

## Criterio de calidad del proyecto

Un cambio "cumple" si:

- mejora la trazabilidad de una afirmación histórica,
- reduce un vacío de investigación,
- o mejora la claridad del texto final sin perder rigor.

---

## Documentos marco

- `DOCUMENTO_FUNDACIONAL.md` → origen, postura y principios del proyecto.
- `HIPOTESIS.md` → hipótesis central (versión operativa v5).
- `MAPA_CAPAS.md` → navegación rápida por niveles de profundidad.

---

## Autoría

**Daniela Naraai Caamal Ake**

Proyecto: *Dos Mil Años en Silencio* — Hopelchén, Campeche, México.  
DOI: https://doi.org/10.5281/zenodo.19140910
