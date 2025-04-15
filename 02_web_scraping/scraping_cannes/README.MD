El  cuaderno recopila películas de las secciones oficiales del Festival de Cannes (2015–2023), identifica si pertenecen a España, Francia o EEUU (he añadido más países), y guarda los datos en un Excel.
*Notas técnicas+
He creado un script para scrapear las películas seleccionadas para el Festival de Cannes entre 2015 y 2023 , guardar los resultados en un Excel e incluir columnas que destaquen
Comencé intentado scrapear la página del Festival pero no había mucha información. Me fui entonces a la wikipedia, recogí bastantes datos allí, pero no todas las películas tenían info. 
Entonces lo completé con la página de IMDB, primero obtuve el código IMDB de cada película. 
Se me ocurrió también averiguar las productoras de cada película para intentar hacer un top (solamente de los países destacados)
Primero la idea era hacer una comparativa entre Francia (país anfitrión), España (mi país) y USA , pero se quedaba un poco corto y decidí ampliar a una docena de países (buscando en general los que habían tenido más participación)
Con los cambios de idea, ampliaciones de proyecto y ser mi primera vez, el flujo de trabajo es un poco lioso (por ejemplo, he creado varios scrapers que a lo mejor son un poco redundantes): primero scrapeando wikipedia, creando un excel y sobre ese excel intentar enriquecerlo con nuevos scrapeos.
Por otro lado, soy consciente de que podía haber usado APIs de IMDB (encontré varias) pero quería esta vez practicar cómo se obtiene información de una web (y tanto wikipedia como IMDB son fáciles)
Otro problema que tuve fue que los nombres de las productoras no estaban normalizados 

El archivo .xlsx definitivo tendrá columnas como:
Año
Título
Países
España (True/False)
Francia (True/False)
EEUU (True/False)
Enlace 
Productoras


visualizaciones: dashboard y alguna cosilla más
He creado un dashboard con toda la información recopilada (usando streamlit): nombre provisional dashboard_cannes_mejorado


