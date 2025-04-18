# Análisis de Películas del Festival de Cannes (2015-2023) #
## Tabla de Contenidos ##
1. [Introducción](#introducción)
2. [Requisitos Técnicos](#requisitos-técnicos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Visualizaciones](#visualizaciones)
6. [Cómo Usar](#cómo-usar)
7. [Retos y Aprendizajes](#retos-y-aprendizajes)
8. [Próximos Pasos](#próximos-pasos)

 ## Introducción ##
Este proyecto recopila información sobre las películas de las secciones oficiales del Festival de Cannes (2015–2023). El objetivo es identificar si las películas pertenecen a España, Francia, Estados Unidos u otros países destacados, y almacenar los datos en un archivo Excel para su análisis.

### El trabajo incluye: ###

Extracción de datos desde Wikipedia e IMDB.
Identificación de las productoras involucradas en cada película.
Creación de un dashboard interactivo con la información recopilada, utilizando Streamlit.
Este proyecto tiene un enfoque educativo y práctico, ya que se desarrolló para practicar técnicas de scraping y organización de datos.

### Requisitos Técnicos ###

Lenguajes utilizados: Python (para scraping y procesamiento de datos).

Herramientas:

Scraping: Wikipedia e IMDB.

Visualización: Streamlit.

Almacenamiento: Archivo Excel (.xlsx).

APIs: Aunque se podrían haber utilizado APIs, el propósito fue practicar scraping manual.


### Estructura del Proyecto ###

Archivo Excel Final: cannes_dataset_unificado.xlsx

El archivo Excel contiene las siguientes columnas:

year: Año de estreno.

title: Título de la película.

director: Director de la película (columna aún sin procesar).

countries: Países involucrados.

section: Sección en el Festival (actualmente no utilizada).

country_esp_fra_usa: Clasificación por España, Francia y Estados Unidos.

film_wiki_url: URL de Wikipedia de la película.

imdb_id: Código IMDB de la película.

imdb_production_companies: Productoras según IMDB.

productoras_consolidadas: Productoras procesadas.

productoras_consolidadas_normalized: Nombres normalizados de las productoras.

country_expanded: Países adicionales incluidos para análisis.

#### Notas Importantes ####

Se han creado varias columnas relacionadas con las productoras para garantizar la precisión de los datos.
Las columnas director y section todavía no se están utilizando en el análisis.
Inicialmente, el proyecto se centró en comparar Francia, España y Estados Unidos, pero después se expandió a una docena de países.

### Flujo de Trabajo ###
El flujo de trabajo incluye:

Scraping:

Extracción inicial desde la página oficial del Festival (limitada información encontrada).

Recolección de datos desde Wikipedia (datos incompletos).

Complementación de datos con IMDB (obteniendo los códigos IMDB de las películas).


Procesamiento:

Normalización de nombres de productoras (problemas con variantes de escritura).

Consolidación de datos en un archivo Excel: cannes_dataset_unificado.xlsx

Visualización:

Creación de un dashboard interactivo con Streamlit.

Enfoque principal en España y comparativas internacionales.

### Visualizaciones ###

Se ha desarrollado un dashboard interactivo utilizando Streamlit, con el nombre provisional dashboard_cannes_mejorado. Este incluye:

Información recopilada de las películas.

Comparativas iniciales entre los países destacados.

Tareas pendientes:

Añadir más funcionalidades al dashboard.

Crear visualizaciones centradas en España y comparativas más detalladas.

### Cómo Usar ###

Clonar el repositorio:

```bash

git clone https://github.com/carmenhat/PythonProyectos.git
cd PythonProyectos/02_web_scraping/scraping_cannes 
```

Instalar dependencias: Asegúrate de tener Python instalado y ejecuta:

```bash

pip install -r requirements.txt 

```

Ejecutar el script de scraping: 

```bash

python cannes-scraper-unified.py (el unificado)
```
Abrir el dashboard:

```bash

streamlit run dashboard_cannes_mejorado.py
```
### Retos y Aprendizajes ###

Scraping:

Wikipedia e IMDB fueron fuentes clave, pero no todas las películas incluían información completa.

Decidí practicar scraping manual en lugar de usar APIs para reforzar habilidades.

Normalización:

Los nombres de las productoras presentaron muchas variantes, lo que complicó el análisis.

Flujo de trabajo:

Siendo mi primer proyecto de este tipo, el flujo de trabajo es algo redundante en algunas partes, creé varios scraper que he tenido que reunificar

### Próximos Pasos ###

Mejorar el dashboard con nuevas visualizaciones y funcionalidades.

Procesar las columnas director y section para incluirlas en el análisis.

Refinar la normalización de nombres de productoras.
corregir fallos en el dashboard: productoras sin paises, columna de director, etc
añadir comparativa ESpaña en dashboard
traducir al inglés
reusar partes del script para ver pelis premiadas y sacar estadísticas
