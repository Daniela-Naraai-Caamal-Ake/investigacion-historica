# Documento Fundacional
### Sistema de información histórica sobre Hopelchén y la región de Los Chenes, Campeche

> Autora: Daniela Naraai Caamal Ake  
> Proyecto: *Dos Mil Años en Silencio*  
> Estado: documento vivo — marco conceptual inicial  
> DOI: https://doi.org/10.5281/zenodo.19140910

---

## 1. Punto de partida

Desde su origen, el proyecto reconoce que la información histórica no se presenta de forma unificada ni uniforme. Por el contrario, existe distribuida entre múltiples tipos de fuentes —documentales, académicas, institucionales, digitales y de memoria oral— producidas en distintos momentos, con propósitos diversos y bajo marcos interpretativos no compatibles entre sí.

Este documento no describe una implementación técnica ni un sistema concluido. Su propósito es definir el marco estructural inicial que permitirá, posteriormente, diseñar un sistema coherente con la naturaleza del problema planteado.

---

## 2. Planteamiento del problema

El problema central que motiva este proyecto no es la inexistencia de información histórica, sino su **dispersión estructural**. La información disponible sobre un mismo territorio suele encontrarse fragmentada, desarticulada y organizada bajo criterios incompatibles, lo que dificulta su análisis comparativo y su comprensión como conjunto.

Las estructuras tradicionales de organización de información tienden a:

- jerarquizar fuentes de antemano,
- imponer cronologías rígidas,
- asumir homogeneidad en los datos,
- o reducir la complejidad narrativa a una sola versión de los hechos.

En contextos donde existen múltiples narrativas coexistentes —incluyendo contradicciones, silencios y versiones parciales—, estos enfoques resultan insuficientes. El problema, por tanto, es **cómo organizar información histórica heterogénea sin perder su contexto, su diversidad ni sus tensiones internas**.

---

## 3. Enfoque del proyecto

El proyecto se concibe desde una perspectiva tecnológica y sistémica. No busca producir una narrativa histórica definitiva ni validar una versión del pasado sobre otras, sino diseñar una herramienta estructural que permita registrar, organizar y comparar información histórica sin imponer interpretaciones anticipadas.

El sistema que se derive de este enfoque funcionará como un **soporte para el análisis**, no como un sustituto del criterio humano. Su tarea principal será facilitar la trazabilidad, la comparación y la visibilización de relaciones entre múltiples registros históricos.

Este enfoque se alinea con principios propios de la ingeniería en sistemas y la tecnología de la información, particularmente en problemas relacionados con:

- manejo de información no estructurada,
- diseño de estructuras flexibles,
- organización de conocimiento complejo,
- y tolerancia a la incompletitud y al cambio.

---

## 4. Principio rector del sistema

La estructura del sistema se organiza alrededor de una función central:

> **Registrar información histórica diversa y permitir su comparación sin perder el contexto de producción.**

Este principio actúa como criterio de diseño. Todo componente futuro del sistema deberá contribuir explícitamente a:

1. registrar información sin deformarla,
2. conservar el contexto en el que fue producida,
3. permitir su comparación con otros registros.

Cualquier elemento que no cumpla estas funciones no forma parte del núcleo del sistema.

---

## 5. Estructura conceptual propuesta

En esta etapa inicial, la estructura del sistema se describe en términos de **capas conceptuales**, entendidas como responsabilidades funcionales y no como componentes técnicos. Estas capas permiten avanzar en el diseño sin imponer una tecnología específica ni una forma cerrada.

### 5.1 Capa de registro de información

Esta capa constituye el punto de entrada de información al sistema. Su función es capturar información tal como existe en el mundo real, sin análisis ni validación previa.

Debe admitir:
- textos completos o fragmentos,
- transcripciones de memoria oral,
- citas documentales,
- notas descriptivas,
- referencias históricas diversas.

En este nivel no se jerarquiza ni se interpreta la información. Registrar es un acto técnico que busca evitar la pérdida o distorsión del contenido original.

*En el repositorio:* `datos/hopelchen/HOPELCHEN_NODO_*.json` — cada registro es una unidad de información con su contenido original preservado.

---

### 5.2 Capa de contextualización

Toda información adquiere significado a partir de su contexto de producción. Esta capa incorpora información que permite entender desde dónde se produce cada narración.

Incluye, de manera general:
- origen de la información,
- autoría o entidad productora,
- momento de producción,
- propósito aparente o marco discursivo.

Esta capa no evalúa la veracidad del contenido, pero evita que los registros se presenten como neutros o universales.

*En el repositorio:* campos `fuente`, `fuente_academica`, `tipo_dato` y `notas_contradiccion` en cada registro. El campo `tipo_dato` hace visible la posición epistemológica del dato (citado, inferido, estimado, analítico).

---

### 5.3 Capa de descomposición analítica

Dado que las narraciones extensas no son directamente comparables entre sí, el sistema debe permitir su descomposición en unidades más pequeñas, tales como afirmaciones, enunciados o ideas explícitas.

Este proceso no altera el contenido original, pero lo vuelve analíticamente manejable. Gracias a esta capa, distintas versiones sobre un mismo tema pueden ponerse en relación sin necesidad de homogeneizarlas.

*En el repositorio:* los registros individuales dentro de cada nodo son las unidades de análisis. `datos/VACIOS.md` documenta las preguntas abiertas — lo que no se sabe tiene el mismo peso estructural que lo que sí se sabe.

---

### 5.4 Capa de relaciones

La última capa permite registrar relaciones entre unidades de información previamente descompuestas. Estas relaciones no son automáticas ni generadas por el sistema, sino declaradas a partir del análisis humano.

Entre estas relaciones pueden existir:
- coincidencias,
- contradicciones,
- complementos,
- silencios,
- continuidades o rupturas.

La función de esta capa no es producir conclusiones, sino **hacer visibles patrones y tensiones entre narrativas**.

*En el repositorio:* campo `conexion_hipotesis` en cada registro — vincula el dato con la pregunta estructural sin cerrar su interpretación. `fuentes/mapa_citas.md` mapea relaciones entre fuentes y nodos.

---

## 6. Uso de la estructura como guía de desarrollo

La estructura propuesta no implica que todas las capas deban implementarse o utilizarse simultáneamente. El sistema puede operar parcialmente en cualquiera de ellas, según el estado del proyecto.

El orden lógico de trabajo sugerido es:

1. registrar información,
2. agregar contexto,
3. descomponer cuando sea necesario,
4. establecer relaciones cuando el análisis lo permita.

Este enfoque permite que el proyecto crezca de manera orgánica, sin forzar cierres prematuros ni interpretaciones definitivas.

---

## 7. Alcance del documento

Este documento define el marco conceptual inicial del sistema, no su implementación técnica. No presupone forma final, arquitectura, tecnología ni producto terminado. Su función es establecer un criterio estructural estable sobre el cual puedan tomarse decisiones futuras de diseño e implementación sin contradicciones conceptuales.

---

## 8. Caso de aplicación: Hopelchén, Campeche

El sistema se desarrolla sobre un caso concreto: la historia del municipio de Hopelchén y la región de Los Chenes, Campeche, México. Este territorio presenta las condiciones que el problema plantea — información dispersa entre archivos en Berlín, La Habana, Ciudad de México y el propio municipio; narrativas producidas desde posiciones radicalmente distintas (cronistas coloniales, académicos externos, comunidades mayas, prensa local); silencios estructurales sobre ciertos períodos y actores.

El caso no es el límite del sistema. Es su punto de prueba. Si la estructura funciona para organizar dos mil años de información heterogénea sobre un territorio como Hopelchén, el modelo es transferible a otros contextos con condiciones similares.

Los materiales producidos durante el desarrollo del sistema — nodos de datos, catálogo de fuentes, preguntas abiertas, análisis narrativos — constituyen a su vez el andamiaje documental que sustentará el libro *Dos Mil Años en Silencio*.

---

## 9. Estado del proyecto

El proyecto se encuentra en **fase de fundamentación y construcción simultánea**. La estructura conceptual aquí presentada orienta el desarrollo posterior del sistema y garantiza coherencia entre el problema identificado y las decisiones que se tomen más adelante.

| Componente | Estado actual |
|---|---|
| Marco conceptual | ✅ Definido (este documento) |
| Hipótesis de trabajo | ✅ Operativa — ver `HIPOTESIS.md` v5 |
| Nodos de información | ✅ 10 nodos · 96 registros · 100% con fuente |
| Catálogo de fuentes | ✅ 68 fuentes catalogadas (F### y FX###) |
| Preguntas abiertas | ✅ 62 preguntas · 0 pendientes · 1 en proceso |
| Capas implementadas | Capa 1 ✅ · Capa 2 ✅ · Capa 3 ✅ · Capa 4 parcial |
| Forma técnica final | 🔲 Por definir |

---

*Este documento es el criterio estructural del proyecto. No describe lo que el sistema es hoy en su totalidad, sino el principio que debe guiar cada decisión de diseño.*
