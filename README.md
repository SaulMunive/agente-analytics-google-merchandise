# 🛒 Agente de Análisis Conversacional — Google Merchandise Store

**Agente de Análisis Conversacional con BigQuery y Cloud Run Functions**

Este proyecto implementa una solución web capaz de responder preguntas en lenguaje natural sobre el dataset público de e-commerce de Google Analytics (Google Merchandise Store), usando un Data Agent de BigQuery integrado con la **Conversational Analytics API**, expuesto mediante una **Cloud Run Function** y consumido desde una interfaz web simple.

## 🎯 Objetivo

Diseñar, implementar y desplegar una arquitectura de microservicios que permita a un usuario preguntar en lenguaje natural sobre datos de sesiones de e-commerce, y recibir respuestas analíticas con texto, tablas y gráficos generados automáticamente.

## 🏗️ Arquitectura

```
Usuario (index.html)
      │  fetch (POST /question)
      ▼
Cloud Run Function (main.py)
      │  Conversational Analytics API
      ▼
Data Agent de BigQuery (agente-saul-dmc)
      │  SQL generado automáticamente
      ▼
bigquery-public-data.google_analytics_sample.ga_sessions_*
(diciembre 2016 — 31 tablas)
```

## 📦 Componentes

| Archivo             | Descripción                                                                 |
|----------------------|------------------------------------------------------------------------------|
| `main.py`            | Cloud Run Function (Python) que recibe la pregunta, la envía al Data Agent, y devuelve texto, tabla de datos y especificación de gráfico (Vega-Lite). |
| `requirements.txt`   | Dependencias de Python.                                                     |
| `index.html`         | Interfaz web de chat con estética de "recibo de compra", que consume la Cloud Run Function y renderiza texto (Markdown), tablas y gráficos. |

## 🤖 Data Agent

- **Nombre:** `agente-saul-dmc`
- **Fuente de datos:** `bigquery-public-data.google_analytics_sample` — tablas `ga_sessions_20161201` a `ga_sessions_20161231` (diciembre 2016, ~79,124 sesiones)
- **Instrucciones del sistema:** analista de datos especializado en comportamiento de usuarios de e-commerce (tráfico, dispositivos, países, transacciones)

## 🚀 Tecnologías

- **Google Cloud BigQuery** — almacenamiento y consulta de datos
- **Conversational Analytics API (Gemini Data Analytics)** — interpretación de lenguaje natural y generación de SQL
- **Cloud Run Functions (2nd Gen, Python 3.14)** — backend serverless
- **Vega-Embed / Vega-Lite** — renderizado de gráficos en el navegador
- **Marked.js** — renderizado de Markdown en las respuestas del agente

## 💬 Ejemplos de preguntas

- ¿Cuántas sesiones hubo en total?
- Grafica las sesiones por país (top 10)
- ¿Qué dispositivo generó más tráfico?
- ¿Cuántas transacciones se realizaron?
- Grafica los ingresos por día del mes

## 🌐 Demo

- **Endpoint de la Cloud Run Function:** `https://agente-saul-analytics-api-133638131302.us-central1.run.app`
- **Frontend:** abre `index.html` en tu navegador, o accede vía GitHub Pages (si está habilitado en este repositorio).

## 👤 Autor

Saúl Munive — Diploma Advanced Data Engineer (DMC Institute)
