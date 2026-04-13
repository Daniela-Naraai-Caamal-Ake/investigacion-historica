## PRIMERA ACCIÓN AL INICIAR

1. Anunciar: `🟢 [MODO AGENTE ACTIVO — Archivo Vivo v2.5]`
2. Leer los 7 archivos MD en /raw/ en orden
3. Cargar base de datos en /database/
4. Consultar registro de PDFs en /database/av_registro_pdfs.json
5. **Actualizar contadores en /logs/av_estado.json:**
   a. Listar archivos en /entradas/aprobadas/ → contar y registrar
   b. Listar archivos en /entradas/borradores/ → contar y registrar
   c. Comparar con la lista anterior en av_estado.json
   d. Si hay discrepancias con AV_MAPA.md → notificar a Dan en prosa
   e. Actualizar campo "actualizado" con timestamp
6. Reportar a Dan en prosa:
   - Estado actual del proyecto (números reales de av_estado.json)
   - Qué hay pendiente más urgente
   - Plan de trabajo sugerido
7. Esperar instrucción antes de proceder

---

## HISTORIAL DE VERSIONES

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 2.0 | marzo 2026 | Versión inicial con ciclo autónomo y Firecrawl |
| 2.1 | 24 marzo 2026 | Firecrawl desactivado → web_search nativa |
| 2.2 | 24 marzo 2026 | Riesgos eliminados de JSON → solo reportes .md |
| 2.3 | 24 marzo 2026 | Anuncios obligatorios de activación/desactivación |
| 2.4 | 24 marzo 2026 | Misión corregida. Territorio de archivos redefinido. PDFs bajo demanda. |
| 2.5 | 24 marzo 2026 | Contadores automáticos → /logs/av_estado.json. AV_MAPA.md sin números estáticos. |
