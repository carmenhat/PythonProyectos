# Proyecto de Scraping - Festival de Cannes 🎥

Este proyecto está diseñado para recopilar información sobre las películas de las secciones oficiales y no oficiales del Festival de Cannes, identificando países destacados como España, Francia y Estados Unidos, y generando datasets listos para análisis.

## Estructura del Proyecto

- **`documentación/`**: Contiene documentos con notas técnicas y pasos para depuración.
  - `README.md`: Descripción general del proyecto.
  - `temas_pendientes.md`: Tareas pendientes y visualizaciones por implementar.
  - `instrucciones_para_analizar_web.md`: Guía para inspeccionar páginas web.

- **`scripts_finalizados/`**: Scripts funcionales y completos.
  - `productoras.py`: Genera un notebook para analizar productoras por país.
  - `nuevo_intento_productoras.py`: Busca productoras en Wikipedia y actualiza un Excel.

- **`scripts_incompletos/`**: Scripts en desarrollo o con problemas.
  - `no_vale_scrape_cannes_no_oficiales.py`: Intenta scrapear secciones no oficiales usando una API, pero requiere revisión.

- **`visualizaciones/`**: Resultados de las visualizaciones generadas por los scripts (gráficos en HTML, PNG, etc.). Dashboard en STREAMLIT. 

- **`notebook/`**: Un notebook Jupyter que sirve como el resumen y ejecución principal del proyecto.

- **`datos_generados/`**: Contiene los datasets generados por los scripts.

## Objetivos del Proyecto

1. Scrapear datos de las secciones oficiales del Festival de Cannes (2015-2024). (O 2023, PORQUE 2024 ESTÁ INCOMPLETO)
2. Guardar los datos en archivos Excel con columnas como:
   - Año, Sección, Título, Director, Duración, Categoría, Países, etc.
3. Visualizaciones planeadas:
   - Barras apiladas por sección y país.
   - Evolución por año y país.
   - Top productoras de cada país destacado.
   COMPLETAR ESTO

## Cómo empezar

1. Asegúrate de instalar las dependencias necesarias:
   ```
   pip install -r requirements.txt
   ```
2. Ejecuta scripts desde la carpeta correspondiente según su estado.
3. Consulta `temas_pendientes.md` para revisar tareas en curso.

---