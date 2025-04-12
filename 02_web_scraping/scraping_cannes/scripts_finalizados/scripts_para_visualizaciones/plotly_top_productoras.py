import pandas as pd
import plotly.express as px
from collections import Counter
from pathlib import Path
# estoy automatizando el proceso de generación del gráfico interactivo: voy a crear un script que lo haga automáticamente
# y lo guardaré en el directorio actual
# así puedo crear más ficheros de este tipo y no perder el tiempo
# Importar los datos
# Cambia la ruta del archivo según sea necesario


file_path = Path("datos_generados/cannes_oficial_wiki_con_productoras.xlsx")
print(f"Ruta del archivo: {file_path.resolve()}")

df = pd.read_excel("/home/carmen/Documentos/repositorio_python/PythonProyectos/02_web_scraping/scraping_cannes/cannes_oficial_wiki_con_productoras.xlsx")

# Filtrar y preparar los datos
df = df[df["productoras"].notna() & df["country_esp_fra_usa"].notna()].copy()

# Normalizar países
df["pais"] = df["country_esp_fra_usa"].map({
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
})

df = df[df["pais"].notna()]
df["productoras_lista"] = df["productoras"].str.split(r",\s*")

# Extraer top 10 por país
resultados = []

for pais in ["España", "Francia", "EEUU"]:
    todas = []
    for items in df[df["pais"] == pais]["productoras_lista"]:
        todas.extend(items)
    
    top = Counter(todas).most_common(10)
    resultados.extend([{"País": pais, "Productora": p[0], "Apariciones": p[1]} for p in top])

df_top = pd.DataFrame(resultados)

# Crear gráfico interactivo
fig = px.bar(
    df_top,
    x="Apariciones",
    y="Productora",
    color="País",
    facet_col="País",
    title="Top 10 Productoras por País en la Sección Oficial (Wikipedia)",
    orientation="h",
    height=700
)

fig.update_layout(template="plotly_white", yaxis={"categoryorder": "total ascending"})
fig.show()
fig.write_html("top_productoras.html")
print("✅ Gráfico guardado como 'top_productoras.html'")
