# Riesgos y pendientes — Archivo Vivo
# Fecha de creación: 24 marzo 2026
# Última actualización: 31 marzo 2026

---

## ESTADO GENERAL
- Total identificados: 9
- Nivel alto: 3 (R01, R02, R03)
- Nivel medio: 3 (R04, R05, R06)
- Nivel bajo: 3 (R07, R08, R09)
- Resueltos: R01, R02, R03, R04, R09 ✅
- Pendientes activos: 4

---

## ✅ RESUELTOS

**R01 — A6 sin título confirmado** ✅ RESUELTO 31 marzo 2026
Título confirmado: **"Hopelchén y sus guerras: dos mil años de un territorio que nunca ha dejado de ser disputado"**
Datos únicos en A6 no integrados anteriormente:
- 29 enero 1858: Hopelchén y sus pueblos se declararon por pertenecer al nuevo Estado de Campeche
- Antes de la Guerra de Castas: el distrito de Hopelchén tenía más de 25,000 habitantes (INAFED)
- De 92 haciendas y ranchos, solo sobrevivió el 60% tras la guerra
- El 45% de las 800,000 ha enajenadas 1843-1847 correspondía a regiones del sur y oriente incluyendo Hopelchén (Patch, SciELO)
- La clase hacendaria de Hopelchén fue "uno de los principales focos de lucha antiagraria" posrevolucionaria (Movimiento Antorchista Nacional)

**R02 — Atribución incorrecta B8** ✅ RESUELTO 24 marzo 2026
Corregido: "El Siglo de Torreón" → "Diario del Sureste, 20 mayo 2016"

**R03 — Seudónimo de Pantaleón Barrera inconsistente** ✅ RESUELTO 31 marzo 2026
CONFIRMADO DEFINITIVO: **Napoleón Trebarra** (no "Noel Á. Arrerab").
Trebarra = Barrera escrita al revés, con Napoleón como nombre de pila imperial.
Fuente: MAESTRO_FINAL (3).json + AV_PERSONAS.md activo (ambos dicen Napoleón Trebarra).
Fuente primaria para verificar: HathiTrust https://babel.hathitrust.org/cgi/pt?id=wu.89095721726

**R04 — B8, B9, B10, B11 pesos idénticos** ✅ RESUELTO 31 marzo 2026
Confirmado: los 4 archivos corruptos son volcados idénticos de la base de datos del 22 marzo 2026.
No contienen texto de entradas originales. B9, B10, B11 deben escribirse desde cero.

**R09 — ARCHIVO_VIVO_MAESTRO_FINAL.json en /raw/** ✅ RESUELTO 24 marzo 2026
Movido a /raw/_versiones_anteriores/

---

## 🔴 NIVEL ALTO — PENDIENTES

**R05 — Datos de B12 no integrados en JSONs activos**
Los datos de Kosichenko 2025 y de las novelas de Lara Zavala están en logs pero no todos en av_nucleo.json ni av_cronologia.json.
Datos pendientes de integrar (algunos ya en av_nucleo_extension.json v1.0):
- Los siete de Bolonchenticul: nombres exactos — AGEY caja 169, vol.119, exp.24
- José Chan: siervo deudor de María Jesús Herrera — debía 52 pesos
- Decreto 27 agosto 1847: retiro de derechos ciudadanos a indios — no en cronología activa
Acción: verificar que av_cronologia.json v1.1 tenga todo; completar con E069+ cuando se identifique solapamiento.

**R06 — Archivos prioritarios en _sesiones_anteriores no migrados**
Archivos que contienen datos únicos aún no integrados en base activa:
- legisladores_hopelchen_1861-2003.json — 42 legislaturas desde 1861
- leydy_pech_perfil.json — perfil completo Leydy Pech
- menonitas_hopelchen.json — historia, colonias, deforestación 2001-2025
- expansion_libro_web_2026-03-22.json — eventos E062-E083, personajes nuevos
Acción: leer y rescatar datos únicos en próxima sesión de actualización.

---

## 🟡 NIVEL MEDIO — PENDIENTES

**R07 — A5 y A6 sin revisión en este proyecto** 
A6 RESUELTO (ver R01). A5 pendiente de revisión de contenido.
Acción: leer A5.md para verificar datos y extractar cualquier dato único.

**R08 — Hilo Cuba — Archivo Nacional de Cuba sin consultar**
Los apellidos exactos de los ~2,000 mayas vendidos a Cuba están en fuentes externas.
Solo tres apellidos identificados: Che, Nagua, Cusán.
Fuentes a consultar prioritariamente:
- Rodríguez Piña, Javier (1990) — en UNAM, CIESAS, ResearchGate
- **Álvarez Cuartero (2007) — "De Tihosuco a La Habana", Studia Historica 25 — ACCESIBLE EN JSTOR** [NUEVA FUENTE]
- Archivo Nacional de Cuba (acceso digital pendiente)
Prioridad: ALTA.

---

## 🟢 NIVEL BAJO

(R09 resuelto, R07 parcialmente resuelto)

---

## DATOS NUEVOS ÚNICOS ENCONTRADOS EN REVISIÓN 31 MARZO 2026

### De la entrada A6 (antes sin título):
- A6 título: "Hopelchén y sus guerras: dos mil años de un territorio que nunca ha dejado de ser disputado"
- 25,000 habitantes antes de la Guerra de Castas
- 29 enero 1858: declaración formal de Hopelchén como parte del Estado de Campeche
- 90 haciendas antes de la guerra → 54 después (pérdida del 40%)
- La elección fraudulenta de Pantaleón Barrera como gobernador de Yucatán CAUSÓ la separación de Campeche

### Del capítulo XIV (El Charras) — datos únicos no en base activa:
- Pedro Quijano Uc: profesor secuestrado JUNTO con El Charras la noche del 13 febrero 1974 — SOBREVIVIÓ y dio testimonio
- Huelga duró del 14 febrero al 27 ABRIL 1974 = 73 días
- FEMOSPP (2002): más de 600 desapariciones + 275 casos tortura en "guerra sucia" 1968-1982 — El Charras está en esa cuenta
- Sindicato de gasolineros "Efraín Calderón" sigue funcionando (además de Jacinto Canek y trabajadores manuales UADY)
- Hoy la calle principal de Hopelchén = "Paseo Efraín Calderón" — la ironía
- Efraín tenía 26 años cuando fue asesinado

### De MAESTRO_FINAL (3).json — datos únicos:
- A6 existía como entrada aprobada con ese título
- Schüren publicaciones derivadas de su tesis: 4 artículos (1995, 1997, 2001, s/f)
- Uc Moreno (1993): única tesis de licenciatura sobre Hopelchén — UAC 7 enero 1993
- Zavala Ramos (1990): única compilación de plantas medicinales de Los Chenes — INI
- Álvarez Cuartero (2007): "De Tihosuco a La Habana" — Studia Historica 25 — JSTOR
- Blog URL original: dansaiudiaush324.blogspot.com → ahora archivovivo5h.blogspot.com
- DOI del libro: https://doi.org/10.5281/zenodo.19140910
- Libro publicado el 20 marzo 2026 en Zenodo

### De AV_MAYA.md — términos con significados confirmados/pendientes:
- EK = puede ser NEGRO o ESTRELLA (dos palabras homofonas distintas en maya)
- HOLCATZÍN = significado pendiente (hay hacienda, comunidad y ron Holcatzín)
- XCUPIL = significado pendiente  
- XTABENTÚN = "enredadera de agua" — planta (Turbina corymbosa), base del licor sagrado maya
- CHENCOH = comunidad del municipio mencionada en De Zitilchén

### De AV_PERSONAS.md — árbol genealógico ampliado:
- Familia Lara: Adda Lara (madre de El Charras), Mario Lara + Otto Lara (autobús 1939)
- Hernán Lara Zavala nació en 1947 según AV_PERSONAS.md (vs. 1946 en HISPADOC — discrepancia sin resolver)
- Familia Baqueiro: incluye Romualdo Baqueiro Lara (suplente Constituyente 1861) que "abandonó su escaño para tomar armas"
- Relación Humberto Lara y Lara → Hernán Lara y Lara → Hernán Lara Zavala (escritor)
- Samuel Cervera: cantinero real de Hopelchén, en la novela Charras p.18
- Jacinto: campesino que compuso el corrido sobre El Charras (personaje real en Charras)
