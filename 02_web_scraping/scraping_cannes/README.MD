El  cuaderno recopila películas de las secciones oficiales del Festival de Cannes (2015–2023), identifica si pertenecen a España, Francia o EEUU (he añadido más países), y guarda los datos en un Excel.
****Notas técnicas****
He creado un script para scrapear las películas seleccionadas para el Festival de Cannes entre 2015 y 2023 , guardar los resultados en un Excel e incluir columnas que destaquen
Comencé intentado scrapear la página del Festival pero no había mucha información. Me fui entonces a la wikipedia, recogí bastantes datos allí, pero no todas las películas tenían info. 
Entonces lo completé con la página de IMDB, primero obtuve el código IMDB de cada película. 
Se me ocurrió también averiguar las productoras de cada película para intentar hacer un top (solamente de los países destacados)
Primero la idea era hacer una comparativa entre Francia (país anfitrión), España (mi país) y USA , pero se quedaba un poco corto y decidí ampliar a una docena de países (buscando en general los que habían tenido más participación)
Con los cambios de idea, ampliaciones de proyecto y ser mi primera vez, el flujo de trabajo es un poco lioso (por ejemplo, he creado varios scrapers que a lo mejor son un poco redundantes): primero scrapeando wikipedia, creando un excel y sobre ese excel intentar enriquecerlo con nuevos scrapeos.
Por otro lado, soy consciente de que podía haber usado APIs de IMDB (encontré varias) pero quería esta vez practicar cómo se obtiene información de una web (y tanto wikipedia como IMDB son fáciles)
Otro problema que tuve fue que los nombres de las productoras no estaban normalizados (había muchísimas variantes para cada productora) 

El archivo .xlsx definitivo tiene las siguientes columnas: el nombre provisional e s
year,	title,	director,	countries,	section,	country_esp_fra_usa,	 film_wiki_url,	imdb_id, 	imdb_production_companies,	productoras_consolidadas,	productoras_consolidadas_normalized	country_expanded
hay 3 columnas para productoras hasta que esté segura de que todo va bien con la definitiva
Aún no he hecho nada con la columna de director . Y la de sección me sobra de momento , era para cuando iba a hacer comparativa entre oficiales y no oficiales
Mantengo las dos columnas de países seleccionados por si acaso 

visualizaciones: dashboard y alguna cosilla más
He creado un dashboard con toda la información recopilada (usando streamlit): nombre provisional dashboard_cannes_mejorado
me falta añadir bastantes cosas a ese dashboard o crear uno nuevo: principalmente quiero centrarme en España y hacer comparativas


