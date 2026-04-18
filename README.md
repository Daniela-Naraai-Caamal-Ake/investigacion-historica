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

Si solo vas a leer el proyecto, empieza por:

1. `README.md` (este archivo)
2. `SINTESIS_MAESTRA.md`
3. `trabajo/indice.md`

---

## Configuración inicial

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales (necesario solo para búsquedas con Firecrawl)
cp .env.example .env
# Edita .env y agrega tu FIRECRAWL_API_KEY
# Obtén una clave en https://www.firecrawl.dev
```

> ⚠ **Nunca subas el archivo `.env` al repositorio.** Ya está en `.gitignore`.
> Usa siempre `.env.example` como plantilla.

---

## Flujo mínimo de trabajo

### 1) Editar datos
Trabaja sobre JSON en `datos/hopelchen/`.

### 2) Regenerar redacción
```bash
python tools/generar_redaccion.py
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

# Actualizar vacíos
python tools/actualizar_vacios.py
```

---

## Estructura simplificada

```text
investigacion-historica/
├── datos/                  # Evidencia, nodos, preguntas, archivo vivo
├── trabajo/                # Redacción por períodos/nodos
├── fuentes/                # Catálogo y mapa de citas
├── tools/                  # Scripts de generación y validación
├── src/                    # Analizador CLI y utilidades
├── tests/                  # Pruebas automáticas
├── SINTESIS_MAESTRA.md
├── MAPA_CAPAS.md
└── README.md
```

---

## Criterio de calidad del proyecto

Un cambio “cumple” si:

- mejora la trazabilidad de una afirmación histórica,
- reduce un vacío de investigación,
- o mejora la claridad del texto final sin perder rigor.

---

## Documentos marco

- `DOCUMENTO_FUNDACIONAL.md` → origen, postura y principios del proyecto.
- `HIPOTESIS.md` → hipótesis central y evolución.
- `MAPA_CAPAS.md` → navegación rápida por niveles de profundidad.

---

## Autoría

**Daniela Naraai Caamal Ake**

Proyecto: *Dos Mil Años en Silencio* — Hopelchén, Campeche, México.
