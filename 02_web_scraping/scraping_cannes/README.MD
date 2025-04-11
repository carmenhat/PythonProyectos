el  cuaderno recopila películas de las secciones no oficiales del Festival de Cannes (2015–2024), identifica si pertenecen a España, Francia o EEUU, y guarda los datos en un Excel.
Notas técnicas
La Quincena de Realizadores y la Semana de la Crítica podrían no estar disponibles en la API oficial, ya que no están organizadas directamente por el festival, sino por otras entidades. Si no aparecen datos en esas secciones, lo confirmamos mirando con DevTools y quizá tengamos que hacer scraping tradicional para esas dos.

El archivo cannes_no_oficiales_con_paises.xlsx tendrá columnas como:

Año

Sección

Título

Director

Duración

Categoría

Países

España (True/False)

Francia (True/False)

EEUU (True/False)

Enlace

el script completo y actualizado para scrapear las secciones no oficiales del Festival de Cannes entre 2015 y 2024, guardar los resultados en un Excel e incluir columnas que destaquen si las películas provienen de España, Francia o Estados Unidos es scrape...no oficiales

visualizaciones:
Visualizaciones que destacan estos países
Con esta información ya puedes hacer cosas como:

Barras apiladas por sección y país destacado
→ ¿Qué sección da más espacio a cada país?

Evolución por año y país
→ ¿Crece o baja la representación de España, Francia o USA con los años?

Top directores de cada país destacado
→ ¿Qué cineastas españoles, franceses y estadounidenses aparecen más?

Proporción de películas por país
→ Gráfico de tarta o barras horizontales.

