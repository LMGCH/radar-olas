# 🌊 Radar de Olas

Radar de Olas es una aplicación desarrollada en Python y Streamlit para detectar **señales tempranas de actividad informativa**.

Su objetivo es localizar historias que están ganando presencia internacional y comparar su evolución con la cobertura disponible en el ecosistema informativo en español.

> **No intenta predecir qué noticia será viral. Detecta señales para que una persona pueda investigarlas.**

## 🎯 ¿Qué problema intenta resolver?

Cuando una historia empieza a crecer, puede existir un intervalo entre su aparición en medios internacionales y su posterior presencia en medios en español.

Radar de Olas intenta detectar ese momento mediante diferentes señales:

* número de publicaciones;
* número de fuentes;
* evolución temporal;
* actividad reciente;
* expansión de una historia;
* presencia o ausencia de cobertura equivalente en español.

El resultado no es una predicción, sino una **pista para investigar**.

## 🔎 ¿Cómo funciona?

El flujo principal del Radar es:

```text
Buscar
   ↓
Filtrar
   ↓
Agrupar
   ↓
Detectar conceptos relacionados
   ↓
Analizar evolución temporal
   ↓
Comparar cobertura internacional / española
   ↓
Detectar alertas
```

### 1. Búsqueda

La fuente principal de información es **Google News RSS**.

La aplicación realiza una búsqueda internacional y otra orientada al ecosistema informativo en español.

Para las consultas internacionales se utiliza Argos Translate cuando es necesario traducir el tema introducido por el usuario.

### 2. Filtrado

Las noticias se filtran para conservar únicamente aquellas relacionadas con el tema buscado.

El filtrado contempla términos y variantes conocidas para determinados conceptos.

### 3. Agrupación

Las noticias relacionadas se agrupan en historias utilizando similitud entre titulares.

El objetivo es evitar analizar cada publicación como un acontecimiento independiente cuando varias publicaciones hablan esencialmente de la misma historia.

### 4. Señales

Cada historia puede mostrar información como:

* publicaciones;
* fuentes;
* tendencia;
* difusión;
* actividad reciente.

Estas señales permiten observar cómo está creciendo una historia.

### 5. Evolución temporal

Radar de Olas analiza la distribución temporal de las publicaciones para identificar historias que mantienen actividad reciente o muestran aceleración.

Esta parte permite distinguir una historia activa de una que simplemente acumuló publicaciones en el pasado.

### 6. Comparación internacional / España

Las historias internacionales se comparan con las historias encontradas en la búsqueda en español.

La comparación permite observar:

* historias con presencia en ambos ámbitos;
* historias con mucha más actividad internacional;
* historias sin presencia detectada en la cobertura española.

La comparación debe interpretarse como una **señal aproximada**, no como una medición exhaustiva de todo el ecosistema informativo.

### 7. Alertas

Cuando una historia presenta determinadas condiciones de actividad reciente, Radar puede mostrarla como:

> 🏄 **ALERTA**

Las alertas están pensadas como puntos de partida para una investigación humana posterior.

## 🌍 Lo que se mueve ahora

La aplicación incluye un panel independiente basado en Google Trends que muestra tendencias actuales de diferentes regiones.

Puede consultar:

* 🌍 Global
* 🇪🇺 Europa
* 🇺🇸 EE. UU.
* 🇪🇸 España

Este panel funciona como **fuente de inspiración independiente** y no alimenta directamente el motor principal de detección de señales.

## 🧪 Laboratorio GDELT

El proyecto conserva una integración experimental con GDELT.

Se mantiene como laboratorio independiente para futuras pruebas y experimentación con fuentes alternativas.

**No forma parte del flujo principal actual del Radar.**

## 🛠️ Tecnologías

* Python
* Streamlit
* Google News RSS
* Google Trends RSS
* Requests
* Argos Translate

## 📁 Estructura del proyecto

```text
radar-olas/
│
├── app.py
├── radar.py
├── filtro.py
├── agrupador.py
├── senales.py
├── velocidad.py
├── conceptos.py
├── sinonimos.py
├── tendencias.py
│
├── prueba_agrupador.py
├── prueba_comparacion.py
├── prueba_conceptos.py
├── prueba_senales.py
│
├── requirements.txt
├── .gitignore
│
└── _historico/
```

### Módulos principales

| Archivo         | Función                                        |
| --------------- | ---------------------------------------------- |
| `app.py`        | Interfaz Streamlit y coordinación del flujo    |
| `radar.py`      | Búsqueda de noticias                           |
| `filtro.py`     | Normalización y filtrado                       |
| `agrupador.py`  | Agrupación de noticias en historias            |
| `senales.py`    | Relaciones y comparación internacional/español |
| `velocidad.py`  | Evolución temporal y detección de alertas      |
| `conceptos.py`  | Detección de conceptos relacionados            |
| `sinonimos.py`  | Variantes y términos relacionados              |
| `tendencias.py` | Panel independiente de tendencias              |

La carpeta `_historico/` contiene experimentos y versiones de prueba conservados como referencia durante el desarrollo.

## 🚀 Instalación

Se recomienda utilizar un entorno virtual.

```powershell
py -m venv .venv
```

Activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

## ▶️ Ejecución

Desde la carpeta del proyecto:

```powershell
py -m streamlit run .\app.py
```

Después, abrir la dirección local mostrada por Streamlit.

## 🧪 Pruebas

El proyecto conserva varios scripts independientes para comprobar partes concretas del sistema:

```text
prueba_agrupador.py
prueba_comparacion.py
prueba_conceptos.py
prueba_senales.py
```

Estos scripts se utilizaron durante el desarrollo para validar componentes sin modificar directamente el flujo principal.

## ⚠️ Limitaciones

Radar de Olas no pretende ofrecer una representación completa de toda la información publicada en Internet.

Sus resultados dependen de:

* las fuentes disponibles;
* los resultados proporcionados por los servicios consultados;
* la calidad de los titulares;
* la agrupación de historias;
* las traducciones utilizadas en las consultas internacionales;
* la ventana temporal seleccionada.

Una alerta significa que **se han encontrado señales que merecen atención**, no que una historia vaya a convertirse necesariamente en tendencia.

## 🧭 Filosofía del proyecto

Radar de Olas nace de una idea sencilla:

> **No necesitas saber qué será tendencia mañana. Necesitas detectar qué empieza a moverse hoy.**

El radar no sustituye el criterio humano.

Sirve para reducir el ruido, encontrar patrones y decidir qué merece una mirada más profunda.

## 📌 Estado del proyecto

**MVP funcional.**

El flujo principal está operativo y el proyecto se encuentra preparado para continuar evolucionando mediante experimentación y nuevas fuentes de información.

La prioridad del desarrollo es mantener un sistema:

* sencillo;
* modular;
* comprensible;
* reproducible;
* y útil antes que excesivamente complejo.

**MVP Prueba**
🌊 Radar de Olas
Aplicación en Python y Streamlit para detectar señales tempranas de actividad informativa y comparar su evolución entre fuentes internacionales y en español.

[Ver proyecto en GitHub] (https://github.com/LMGCH/radar-olas/) · [Probar Radar de Olas] (https://radar-olas.streamlit.app/)
---

**Radar de Olas · 2026**
