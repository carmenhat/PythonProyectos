Análisis y Conclusiones del Proyecto: Participación Internacional en el Festival de Cannes (2015–2024)
1. Contexto y objetivo del proyecto
Este proyecto nace del interés por explorar la dimensión internacional del Festival de Cannes, más allá de la Sección Oficial. A través de técnicas de scraping y análisis de datos, se han recopilado y visualizado películas presentadas tanto en secciones oficiales como no oficiales, con un enfoque especial en tres países clave: España, Francia y Estados Unidos. El objetivo ha sido observar su evolución, participación proporcional y las productoras más influyentes.

2. Metodología
Se ha utilizado web scraping desde wikipedia e IMDB

Los datos se han limpiado, enriquecido (extrayendo productoras y países) y exportado a Excel para facilitar su uso.

Las visualizaciones se han creado con Plotly y se ha construido un dashboard interactivo con Streamlit.

El análisis se ha dividido en dos conjuntos de datos: películas de la Sección Oficial 
#
########## 

####y películas de secciones no oficiales (como Quincena de Realizadores, Semana de la Crítica, ACID, etc.). #################

3. Conclusiones por eje de análisis
A. Participación Absoluta por País
Francia domina lógicamente la participación por volumen, tanto en oficial como no oficiales, dado que es el país anfitrión y cuenta con un ecosistema cinematográfico local muy activo.

España ha mostrado una presencia creciente

EEUU presenta una fuerte presencia en la Sección Oficial, especialmente en películas de alto presupuesto o con trayectoria festivalera previa, pero su presencia en secciones no oficiales es menor y más selectiva.  CONFIRMAR ESTO..

B. Participación Proporcional por Año
Mientras que Francia mantiene una cuota estable en ambas secciones, se observa una mayor diversidad internacional en los últimos años, con picos de participación extranjera (incluyendo a España) en ediciones recientes.

La presencia de España en años como 2019 o 2022 destaca proporcionalmente sobre el total de títulos seleccionados.

C. Comparativa Oficial vs. No Oficiales. ELIMINAR ESTO SEGURAMENTE. 
Las secciones no oficiales actúan como viveros de nuevas voces y cinematografías emergentes, lo que favorece a países como España, con una producción más modesta y arriesgada.

En cambio, la Sección Oficial está más alineada con grandes productoras y cineastas de renombre, lo cual se refleja en el dominio francés y estadounidense en esta sección.

D. Top de Productoras, CONFIRMAR CON DATOS 
En el top aparecen productoras estatales o de gran trayectoria en sus países, como TVE (España), Canal+ o Arte (Francia) y A24 o Netflix (EEUU).

Es relevante cómo algunas productoras independientes españolas han tenido múltiples participaciones en las secciones paralelas, reflejando el dinamismo del sector indie.

El análisis del top también revela colaboraciones internacionales, con coproducciones frecuentes entre Francia y otros países, como España, Bélgica o Alemania.

4. Potencial para próximos análisis
Analizar la presencia femenina en dirección o producción.

Clasificar los géneros de las películas (drama, documental, comedia...).

Ampliar el análisis a premios recibidos, tanto dentro como fuera de competición.

Incluir métricas externas: reseñas en IMDb, Rotten Tomatoes, o performance en taquilla.

5. Aplicación del proyecto
Este proyecto es un claro ejemplo de cómo el scraping ético, la limpieza de datos y la visualización interactiva pueden generar análisis cultural valioso. Además, demuestra competencias clave para roles de data analyst y data visualization, incluyendo:

Extracción automatizada de datos estructurados y semiestructurados

Normalización y análisis estadístico

Visualización narrativa y creación de dashboards

Orientación a storytelling de datos, especialmente con enfoque cultural

NOTAS:

C. es posible que tenga que dejarlo de momento ya que no estoy consiguiendo muchos datos de las secciones no oficiales.

NUEVAS IDEAS :

La relación entre las coproducciones y la participación (tanto proporcional como absoluta) de los países puede revelar tendencias y patrones muy interesantes sobre la industria cinematográfica en el contexto del Festival de Cannes. Algunas posibles relaciones y patrones que se podrían observar y destacar:

**Posibles Relaciones y Tendencias:**

1.  **Aumento de la Participación a través de Coproducciones:**
    * **Tendencia:**  Podrías observar que países que históricamente tenían una participación absoluta menor comienzan a aumentar su presencia en Cannes a través de coproducciones con países más grandes o con mayor tradición cinematográfica (como Francia).
    * **Patrón:** Un país podría mostrar una participación absoluta relativamente estable, pero su participación proporcional podría aumentar si coproduce con países cuya producción disminuye, o viceversa.

2.  **Influencia de las Coproducciones en la Dominancia Proporcional:**
    * **Tendencia:** La "dominancia" proporcional de un país históricamente fuerte (como Francia en los primeros años que mencionaste) podría disminuir no solo por un aumento en la producción nacional de otros países, sino también por un aumento en las coproducciones donde estos otros países tienen un papel significativo.
    * **Patrón:** Analizar si la disminución en la proporción de un país líder coincide con un aumento en las coproducciones donde otros países son socios principales podría ser revelador.

3.  **Patrones de Colaboración Regional o Temática:**
    * **Tendencia:** Podrías identificar patrones de coproducción regional (por ejemplo, entre países europeos, latinoamericanos o asiáticos). Esto podría indicar la existencia de lazos culturales, acuerdos de financiación o intereses temáticos compartidos.
    * **Patrón:** Ciertos géneros cinematográficos o temas podrían estar más asociados con coproducciones entre países específicos.

4.  **Impacto de las Políticas de Financiación y Acuerdos Internacionales:**
    * **Tendencia:** Cambios en las políticas de financiación cinematográfica a nivel nacional o la firma de acuerdos de coproducción bilaterales o multilaterales podrían reflejarse en un aumento o disminución de las coproducciones entre los países involucrados y, por lo tanto, en su participación en festivales como Cannes.
    * **Patrón:** Un aumento repentino en las coproducciones entre dos países podría coincidir con la implementación de un nuevo acuerdo de colaboración cinematográfica.

5.  **Rol de las Productoras en las Coproducciones y la Participación:**
    * **Tendencia:** Algunas productoras podrían especializarse en coproducciones internacionales, actuando como puente entre diferentes industrias cinematográficas y contribuyendo significativamente a la participación de múltiples países.
    * **Patrón:** Analizar si las productoras más activas en coproducciones también son las que tienen más películas seleccionadas en Cannes podría ser interesante.

6.  **Evolución de las Preferencias del Festival:**
    * **Tendencia:** La proporción de películas de ciertos países podría aumentar o disminuir con el tiempo debido a cambios en los gustos o prioridades del comité de selección del festival, lo cual podría o no estar relacionado con las tendencias de coproducción.
    * **Patrón:** Comparar la evolución de la participación absoluta y proporcional con los datos de coproducción podría ayudar a discernir si el aumento de la presencia de un país se debe principalmente a su producción nacional o a su actividad en coproducciones.

**Cómo Investigar estas Relaciones con mis Datos:**

1.  **Visualizaciones Combinadas:** En el dashboard de Streamlit, podría colocar gráficos de la evolución de la participación proporcional junto con gráficos de la frecuencia de las coproducciones más relevantes (donde uno de los países sea el de interés).

2.  **Tablas Comparativas:** Crear tablas que muestren la participación absoluta de un país y su número de coproducciones a lo largo de los años para ver si hay correlaciones.

3.  **Filtros Interactivos:** Permitir a los usuarios filtrar por país para ver sus tendencias de participación y sus socios de coproducción más frecuentes.

4.  **Anotaciones y Texto Explicativo:** añadir anotaciones a los gráficos o secciones de texto en el dashboard para destacar las tendencias o patrones que se observen.

**Al obtener y analizar los datos de coproducción, considerar las siguientes preguntas:**

* ¿Qué países coproducen con mayor frecuencia con España? ¿Ha cambiado esto con el tiempo?
* ¿La participación proporcional de España ha aumentado o disminuido en los últimos años? ¿Hay una correlación con sus coproducciones?
* ¿Hay países cuya participación ha aumentado significativamente gracias a las coproducciones?
* ¿Las coproducciones tienden a ser entre países geográficamente cercanos o con lazos culturales históricos?
* ¿Qué productoras están más involucradas en las coproducciones internacionales que llegan a Cannes?


