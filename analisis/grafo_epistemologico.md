# Grafo Epistemológico — *Dos Mil Años en Silencio*

> Autora: Daniela Naraai Caamal Ake  
> Generado: 2026-04-24 05:01 UTC  
> ⚙ Generado automáticamente por `tools/grafo_epistemologico.py`

Este documento analiza la **robustez epistemológica** del proyecto:
cada afirmación (registro) debe estar encadenada a:

```
Hipótesis → Nodo histórico → Registro → Fuente
```

Un registro que rompe esta cadena es una **brecha epistemológica**: puede ser válido pero no está integrado al sistema de conocimiento del proyecto.

---

## Índice

1. [Métricas del grafo](#1-métricas-del-grafo)
2. [Componentes conexos](#2-componentes-conexos)
3. [Brechas epistemológicas: sin conexión a hipótesis](#3-brechas-epistemológicas-sin-conexión-a-hipótesis)
4. [Brechas epistemológicas: sin fuente verificable](#4-brechas-epistemológicas-sin-fuente-verificable)
5. [Registros sin etiquetas temáticas](#5-registros-sin-etiquetas-temáticas)
6. [Nodos históricos aislados](#6-nodos-históricos-aislados)
7. [Preguntas pendientes](#7-preguntas-pendientes)
8. [Conectividad inter-nodo](#8-conectividad-inter-nodo)

---

## 1. Métricas del grafo

| Indicador | Valor |
|---|---|
| Nodos totales | 323 |
| Aristas totales | 595 |
| Nodos históricos | 10 |
| Registros | 99 |
| Fuentes | 174 |
| Preguntas | 39 |
| Componentes conexos | 1 |
| Cobertura de hipótesis | **100.0%** |
| Cobertura de fuente | **100.0%** |

---

## 2. Componentes conexos

Un componente conexo es un grupo de nodos que se pueden alcanzar entre sí (ignorando la dirección de las aristas).

Se detectaron **1 componente(s) conexo(s)**. 0 nodo(s) completamente aislado(s).

✅ Todos los nodos históricos y la hipótesis forman un único componente conectado.

---

## 3. Brechas epistemológicas: sin conexión a hipótesis

Registros que **no tienen** campo `conexion_hipotesis` — sus afirmaciones no están explícitamente enlazadas a la pregunta guía del proyecto.

✅ Todos los registros están conectados a la hipótesis.

---

## 4. Brechas epistemológicas: sin fuente verificable

Registros que **no citan ninguna fuente**. Sin fuente, la afirmación no puede ser verificada ni refutada.

✅ Todos los registros tienen al menos una fuente.

---

## 5. Registros sin etiquetas temáticas

Los `tags` permiten crear aristas temáticas entre nodos. Registros sin tags quedan fuera del grafo de temas.

✅ Todos los registros tienen etiquetas temáticas.

---

## 6. Nodos históricos aislados

Nodos históricos sin ninguna arista hacia otro nodo histórico (vía actores, tags o `continua_desde`). Un nodo aislado no contribuye al tejido relacional del grafo.

✅ Todos los nodos históricos están conectados entre sí.

---

## 7. Preguntas pendientes

Preguntas con estado `PENDIENTE` que aún no han sido respondidas.

ℹ️ **3 pregunta(s) pendiente(s)**:

- `P010-01` [Alta] — ¿Existen informes técnicos del INAH sobre los alineamientos astronómic
- `P010-03` [Alta] — ¿Cuántos hablantes de maya yucateco en Hopelchén son bilingües plenos 
- `P010-05` [Media] — ¿Las novelas de Hernán Lara Zavala (Charras, El lugar donde crece la h

---

## 8. Conectividad inter-nodo

Número de aristas que conectan cada nodo histórico con otros nodos (actores compartidos, tags compartidos, continuación temporal).

| Nodo | Título | Aristas hacia otros nodos |
|---|---|---|
| 001 | Prehispánico | ✅ 16 |
| 002 | Conquista Colonial | ✅ 16 |
| 003 | Colonia Tardía–Porfiriato | ✅ 28 |
| 004 | Revolución–Chicle | ✅ 32 |
| 005 | Contemporáneo | ✅ 29 |
| 006 | Poder Político Local | ✅ 3 |
| 007 | Rutas y Territorio | ✅ 8 |
| 008 | Demografía | ✅ 7 |
| 009 | Resistencia Maya | ✅ 7 |
| 010 | Conocimiento y Cultura | ✅ 2 |

---

*Última actualización: generado automáticamente.*