# Mapa de capas del repositorio

Guía corta para navegar el proyecto sin perderse.

## Capa 0 — Propósito y contexto

- `README.md`
- `DOCUMENTO_FUNDACIONAL.md`
- `HIPOTESIS.md`

Úsala para entender **qué se investiga y por qué**.

---

## Capa 1 — Visión consolidada

- `SINTESIS_MAESTRA.md`

Úsala para ver el estado general del proyecto en un solo documento.

---

## Capa 2 — Redacción literaria (el libro)

- `datos/borradores/PRÓLOGO.md` y `datos/borradores/B*.md` / `A*.md`

Úsala para leer los capítulos del libro en preparación.

---

## Capa 3 — Redacción histórica estructurada

- `trabajo/indice.md`
- `trabajo/periodos/nodo-*.md`

Úsala para leer el contenido narrativo organizado por nodo/período.

---

## Capa 4 — Evidencia y vacíos

- `datos/hopelchen/HOPELCHEN_NODO_*.json`
- `datos/hopelchen/HOPELCHEN_PREGUNTAS_*.json`
- `datos/VACIOS.md`

Úsala para verificar **dato, fuente y preguntas abiertas**.

---

## Capa 5 — Fuentes

- `fuentes/catalogo_fuentes.md`
- `fuentes/mapa_citas.md`
- `datos/curated/fuentes.json`

Úsala para rastrear cada afirmación a su origen.

---

## Capa 6 — Estadísticas y búsqueda

- `docs/stats.json` → métricas del proyecto (96 registros, 100% con fuente)
- `docs/search_index.json` → índice de búsqueda de todos los registros
- `docs/index.html` → portal de búsqueda web

---

## Capa 7 — Herramientas técnicas

- `tools/` → generación, validación y búsqueda de fuentes
- `src/` → analizador CLI
- `tests/` → 122 pruebas automáticas

---

## Ruta recomendada (rápida)

1. `README.md`
2. `SINTESIS_MAESTRA.md`
3. `trabajo/indice.md`
4. `datos/VACIOS.md`
5. `fuentes/catalogo_fuentes.md`

---

## Comandos de un vistazo

```bash
# Ver el estado del proyecto
python tools/generar_estadisticas.py

# Regenerar todo
python tools/generar_redaccion.py && python tools/generar_sintesis.py && python tools/actualizar_vacios.py

# Validar integridad
python tools/validar_datos.py && python tools/validar_fechas.py

# Buscar fuentes para registros sin citar
python tools/buscar_fuentes_vacias.py

# Validar URLs del catálogo
python tools/validar_citas.py
```

---

## Capa 8 — Análisis de cruces y silencios *(nueva)*

- `analisis/cruce_informacion.md` → actores, mecanismos y temas que atraviesan múltiples nodos
- `analisis/contradicciones.md` → 82 tensiones entre fuentes (factuales, interpretativas, silencios)
- `analisis/mapa_silencios.md` → ausencias estructurales del archivo histórico disponible

```bash
# Regenerar los tres análisis
python tools/generar_matriz_cruces.py
python tools/generar_contradicciones.py
python tools/generar_mapa_silencios.py
```
