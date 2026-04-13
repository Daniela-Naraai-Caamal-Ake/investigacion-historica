# FICHAS DE EVIDENCIA — Con campo `hipotesis_que_afecta`

> Proyecto: *Dos Mil Años en Silencio* — Hopelchén: 2000 años de historia  
> Autora: Daniela Naraai Caamal  
> Este archivo muestra cómo se lee cada dato del repositorio en relación directa con la hipótesis central.  
> Para agregar el campo al JSON: ver `datos/hopelchen/HOPELCHEN_NODO_*.json` → campo `"conexion_hipotesis"` en cada registro.

---

## QUÉ ES UNA FICHA DE EVIDENCIA

Cada registro en los archivos `HOPELCHEN_NODO_*.json` es una ficha de evidencia. Tiene:

- **ID** — identificador único (`001-A`, `003-B`, etc.)
- **DATO** — qué ocurrió, qué dice la fuente
- **FUENTE** — quién lo documenta y con qué confiabilidad
- **PREGUNTA QUE RESPONDE** — a cuál ID del archivo `datos/VACIOS.md` responde (o parcialmente)
- **HIPÓTESIS QUE AFECTA** — cómo este dato mueve la aguja de la hipótesis central:
  - `CONFIRMA` — el dato es evidencia directa del patrón de despojo/control
  - `COMPLICA` — el dato no encaja limpiamente en la hipótesis y exige matizarla
  - `REFUTA` — el dato contradice directamente la hipótesis (caso raro — documentar con cuidado)
  - `NEUTRAL` — el dato es contexto necesario pero no incide en la hipótesis
- **PREGUNTAS QUE GENERA** — qué nuevas preguntas abre este dato

---

## FICHAS SELECCIONADAS — UN EJEMPLO POR NODO

---

### FICHA 001-A
**DATO:** Las primeras evidencias de ocupación humana en Hopelchén corresponden a cerámica del Preclásico Tardío en Santa Rosa Xtampak, fechada entre 300 y 250 a.C. Sin embargo, las primeras inscripciones jeroglíficas del mismo sitio datan de 646 d.C. — una brecha de ~900 años entre presencia física y registro escrito.

**FUENTE:** INAH (Sistema de Información Cultural, confiabilidad alta); Zapata Peraza, Renée Lorelei. "Santa Rosa Xtampak, Campeche: su patrón de asentamiento del Preclásico al Clásico." *Mayab* 18 (2005): 5-16.

**PREGUNTA QUE RESPONDE:** P001-03 (parcialmente — confirma que la ocupación existe desde 300 a.C. pero no empuja la fecha más atrás)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — y de manera sofisticada. La brecha de 900 años entre la presencia física (cerámica) y el registro escrito (estelas) no es un vacío neutral: o alguien no registró, o el registro no sobrevivió. Ambas explicaciones confirman la hipótesis de manipulación del conocimiento histórico. Las fuentes turísticas repiten el dato arqueológico sin diferenciar cerámica de epigrafía, lo que añade una capa contemporánea de confusión al mismo patrón.

**PREGUNTAS QUE GENERA:** ¿Por qué el registro epigráfico de Los Chenes empieza 900 años después de la primera ocupación documentada? ¿Hay sitios en la región con inscripciones anteriores a 646 d.C. que no han sido excavados?

---

### FICHA 002-G
**DATO:** En 1669 los bataboob (jefes principales mayas) de Hopelchén aún "repudiaban el control de los blancos" — 122 años después de que la conquista oficial de Yucatán se declarara completa (1547).

**FUENTE:** Citado con reserva crítica en múltiples fuentes secundarias (INDEFOS, Archivo Municipal, Guía Turística México) sin que ninguna cite la fuente primaria original. Fuente primaria probable: Cogolludo, Diego López de. *Historia de Yucatán* (1688).

**PREGUNTA QUE RESPONDE:** P001-01 (identifica el dato pero no los nombres — la pregunta sigue abierta)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — y revela resistencia activa. El dato de 1669 demuestra que el poder maya local no fue eliminado por la conquista sino *empujado hacia los márgenes* durante más de un siglo. Los bataboob son el eslabón entre el poder prehispánico y el poder colonial. Si sus apellidos aparecen en haciendas del siglo XIX o en la política del siglo XX, la continuidad del patrón es genética, no solo estructural.

**PREGUNTAS QUE GENERA:** ¿Cuáles eran los apellidos de esos bataboob? ¿Sus descendientes aparecen como aliados coloniales (como los Xiúes en Maní) o como víctimas del despojo del Porfiriato?

---

### FICHA 003-B
**DATO:** En 1843-1847, el gobierno liberal de Yucatán aprobó leyes de privatización de las tierras comunales mayas. Esas leyes despojaron directamente a los mayas de Los Chenes de sus tierras de subsistencia. Ese despojo específico es el evento que detonó la Guerra de Castas (1847).

**FUENTE:** Dato verificado en fuentes académicas; verificable con fuente primaria en AGEY (Archivo General del Estado de Yucatán).

**PREGUNTA QUE RESPONDE:** Cierra el contexto de P002-03 (el despojo de tierras comunales como continuación del sistema de encomienda)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — es el momento más explícito y documentable de confirmación de la hipótesis. Una élite política-económica (gobierno liberal de Yucatán + hacendados criollos) aprobó leyes específicamente diseñadas para transferir tierras comunales mayas a manos privadas. La narrativa oficial llama a lo que siguió "Guerra de Castas" — un nombre que reduce un conflicto estructural de despojo a una confrontación étnica, ocultando la causa económica. Este es el patrón mismo: los despojados resisten, y su resistencia es renombrada para hacer invisible el despojo original.

**PREGUNTAS QUE GENERA:** ¿Los ejidos que se dotaron bajo la Reforma Agraria de los años 30 (Nodo 004-B) cubrieron los mismos territorios que fueron privatizados en 1843-1847? ¿Hay continuidad catastral entre el despojo porfiriano y el despojo menonita?

---

### FICHA 003-E
**DATO:** La familia Baranda controló simultáneamente el poder político (diputados, gobernadores, ministros), la infraestructura de comunicación (telégrafo 1870), y la narrativa educativa de Campeche desde 1787 hasta 1909 — tres generaciones, cuatro instituciones, un apellido.

**FUENTE:** Alta fiabilidad para datos genealógicos. Citado en fuentes académicas y en el Digesto Constitucional Mexicano (SCJN 2010).

**PREGUNTA QUE RESPONDE:** Responde P006-01 (contexto del patrón genealógico que ese ID busca confirmar para el período actual)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — este es el caso de estudio más completo del patrón en un período con documentación suficiente. La familia Baranda es el nombre propio del Nodo 003: una familia que en tres generaciones controló política, infraestructura, educación y prensa. La narrativa oficial presenta a Joaquín Baranda como "promotor de la educación pública laica y gratuita" — pero el análisis estructural revela que esa educación era también el instrumento de hispanización y borramiento cultural de las comunidades mayas.

**PREGUNTAS QUE GENERA:** ¿El apellido Baranda reaparece en los presidentes municipales de Hopelchén del siglo XX? ¿El alcalde Hiram Aranda Calderón (2024-2027) tiene parentesco genealógico con la familia Baranda?

---

### FICHA 004-C
**DATO:** La industria chiclera en Los Chenes (1900-1950) replicó la estructura exacta de la hacienda azucarera: los mayas cortaban el chicle, los contratistas acumulaban la deuda, los exportadores extranjeros (Wrigley, Adams) controlaban el precio internacional. El sistema de *habilitación* (deuda anticipada) creó una servidumbre por contrato funcionalmente idéntica a la de las haciendas.

**FUENTE:** Citado académico, alta confiabilidad. Schüren (2003) y fuentes complementarias.

**PREGUNTA QUE RESPONDE:** Contexto de P006-08 (el presidente municipal de 1987-1992 hereda una región que salió del ciclo chiclero apenas 20 años antes)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — La industria chiclera reemplazó a la hacienda como mecanismo de extracción con la misma estructura: poder externo + trabajadores mayas + deuda como cadena. El cambio de régimen político (Revolución 1910) no rompió el patrón — lo reformuló. El recurso cambió (de azúcar a chicle) pero el esquema de extracción y dependencia es idéntico.

**PREGUNTAS QUE GENERA:** ¿Hay testimonios orales de chicleros de Los Chenes que nombren a los contratistas específicos? ¿Los apellidos de esos contratistas reaparecen en la política local de la segunda mitad del siglo XX?

---

### FICHA 005-C
**DATO:** Entre 2012 y 2017, las comunidades mayas de Los Chenes — con Leydy Pech como figura central — lograron la primera suspensión judicial de soya transgénica en México, ganando en tres instancias incluyendo la Suprema Corte. En 2020, Leydy Pech recibió el Goldman Environmental Prize (equivalente al Nobel del medio ambiente).

**FUENTE:** Fuentes legales primarias (expedientes judiciales) y periodísticas verificadas; perfil leydy_pech_perfil.json en el repositorio.

**PREGUNTA QUE RESPONDE:** No existe pregunta formal asignada — este registro *genera* preguntas nuevas

**HIPÓTESIS QUE AFECTA:** `COMPLICA` — y esto es lo más valioso que puede hacer un dato. La resistencia maya no solo existe: en este caso *gana* en el terreno jurídico del Estado que históricamente ha sido el instrumento del despojo. Esto no refuta la hipótesis — el ciclo extractivo intentó operar y la resistencia lo detuvo parcialmente. Pero sí obliga a incorporar la agencia maya como variable activa, no solo como víctima del patrón. La hipótesis en su V1-V3 no anticipaba este resultado. La V4 (versión canónica) lo integra explícitamente.

**PREGUNTAS QUE GENERA:** ¿Qué condiciones específicas — organizativas, jurídicas, internacionales — hicieron posible que Leydy Pech ganara en 2020 lo que las comunidades mayas no lograron en 500 años? ¿Hubo algún presidente municipal de Hopelchén que apoyara activamente la lucha de las comunidades contra la soya?

---

### FICHA 006-B
**DATO:** Los apellidos Lara, Calderón, Solís, Baqueiro y Barrera son descritos como "profundamente cheneros" y han generado "una serie de combinaciones familiares muy conocidas en toda la península". Las combinaciones documentadas incluyen: Lara Calderón, Calderón Lara, Lara Solís, Lara Barrera, Barrera Baqueiro, Lara y Lara. El apellido Lara aparece en posiciones de poder desde 1862 (Pedro Lara, diputado) hasta 2024 (Emilio Lara Calderón, diputado federal) — 162 años documentados.

**FUENTE:** PorEsto — "Recuerdos de Efraín Calderón Lara Charras" (11 feb 2019); Digesto Constitucional Mexicano — Campeche (SCJN 2010). Archivo: `sources/83536.pdf`.

**PREGUNTA QUE RESPONDE:** P006-07 (confirma que el apellido Lara tiene presencia en el poder durante 162 años — la pregunta de continuidad genealógica sigue abierta)

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — El poder político en Hopelchén no es solo una estructura institucional (PRI durante 62 años) sino también una red genealógica. Los mismos apellidos en el poder durante más de un siglo no son coincidencia estadística. Este registro es la evidencia más directa de que el patrón de control político es también hereditario — lo que cierra el círculo con el Nodo 003-E (familia Baranda en el siglo XIX) y confirma que la transmisión del poder en Los Chenes tiene apellido.

**PREGUNTAS QUE GENERA:** ¿Cuándo exactamente se formó la red matrimonial Lara-Calderón-Barrera? ¿Hay un momento fundacional (un matrimonio específico en el siglo XIX o principios del XX) que explique la densidad de esas combinaciones familiares?

---

### FICHA 007-I (CRUCE DE DATOS)
**DATO:** Las rutas de comunicación de Hopelchén en 500 años forman una secuencia que replica el patrón extractivo: Camino Real colonial (siglo XVI) para extraer tributo → Telégrafo (1870) para control político porfiriano → Campos de aterrizaje (1934-1950) para el chicle → Carretera Federal 261 (1960s-80s) para maíz, sorgo y soya → Brechas menonitas (1987-2026) para la soya transgénica.

**FUENTE:** Schüren, Ute (2003) — fuente primaria académica con citas directas de campo; datos institucionales verificados.

**PREGUNTA QUE RESPONDE:** Vacío sin ID — ¿La Carretera 261 fue construida antes o después de la llegada de los menonitas?

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — CONFIRMACIÓN ESPACIAL. El control del territorio de Hopelchén se ha ejercido históricamente construyendo primero la ruta de extracción y luego extrayendo el recurso disponible. No hay una sola ruta de comunicación en Hopelchén que no haya sido construida o aprovechada por el actor de poder de su era. Esto convierte la infraestructura en evidencia material del patrón: el mapa de caminos *es* el mapa del despojo.

**PREGUNTAS QUE GENERA:** ¿Las brechas abiertas por los menonitas en el municipio de Hopelchén fueron autorizadas por el ayuntamiento o abiertas de facto? ¿Existe documentación de permisos de apertura de brechas en los registros municipales?

---

### FICHA 008-D
**DATO:** En 2020, el 70.93% de la población del municipio de Hopelchén era indígena (maya). El 75.6% vivía en pobreza (CONEVAL). Hopelchén es el municipio con mayor porcentaje de población indígena en Campeche.

**FUENTE:** INEGI Censo 2020; CONEVAL 2020; datos institucionales verificados.

**PREGUNTA QUE RESPONDE:** Cierra el argumento cuantitativo de la hipótesis en su dimensión humana

**HIPÓTESIS QUE AFECTA:** `CONFIRMA` — con la frialdad más poderosa posible. El municipio donde ocurrió el despojo de 500 años documentado en este repositorio tiene hoy al 75.6% de su población en pobreza y al 70.93% siendo indígena (maya). No hay necesidad de argumento adicional: el resultado numérico del patrón extractivo es esa cifra. Los despojados siguen siendo mayoría. Los que controlan el recurso siguen siendo minoría externa. La demografía es la evidencia más fría y más contundente de la hipótesis.

**PREGUNTAS QUE GENERA:** ¿Cuál es el porcentaje de la población indígena de Hopelchén que tiene título de propiedad de la tierra donde vive? ¿Cuántos de los 42,140 habitantes del municipio son ejidatarios activos?

---

## PATRÓN ACUMULADO — CÓMO LEE CADA NODO LA HIPÓTESIS

| Nodo | Tipo de confirmación | Registro clave |
|------|---------------------|----------------|
| 001 | Confirma: brecha de conocimiento de 900 años = primera evidencia de supresión sistemática del registro histórico | 001-A, 001-F |
| 002 | Confirma: conquista + encomienda + auto de fe = control simultáneo de tierra, trabajo y conocimiento | 002-G, 002-H |
| 003 | Confirma (máxima evidencia): privatización 1843-47 + familia Baranda = mecanismo más documentado del patrón | 003-B, 003-E, 003-H |
| 004 | Confirma: ciclo chiclero = misma estructura de extracción con nombre distinto | 004-C, 004-G |
| 005 | **Complica productivamente**: resistencia maya gana en 2020 = primera fisura documentada del patrón | 005-C, 005-F |
| 006 | Confirma: 162 años de los mismos apellidos en el poder = el patrón tiene genealogía propia | 006-B, 006-G |
| 007 | Confirma: rutas = instrumentos de extracción = el mapa del despojo | 007-I |
| 008 | Confirma (evidencia más fría): 75.6% pobreza + 70.93% indígena = resultado medible del ciclo extractivo | 008-D, 008-G |

---

*Fuente de datos: `datos/hopelchen/HOPELCHEN_NODO_001-008.json`*  
*Referencia de preguntas: `datos/VACIOS.md`*  
*Hipótesis canónica: `HIPOTESIS.md`*
