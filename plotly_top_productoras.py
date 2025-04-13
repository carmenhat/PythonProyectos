import pandas as pd
import plotly.express as px
from collections import Counter

# Cargar los datos con productoras
df = pd.read_excel("datos_generados/datos_generados/cannes_oficial_wiki_con_productoras.xlsx")

# Filtrar y preparar los datos
df = df[df["productoras"].notna() & df["country_esp_fra_usa"].notna()].copy()

# Normalizar países
df["pais"] = df["country_esp_fra_usa"].map({
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
})

df = df[df["pais"].notna()]
df["productoras_lista"] = df["productoras"].str.split(",\s*")

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
fig.write_html("visualizaciones/top_productoras.html")
print("✅ Gráfico guardado como 'visualizaciones/top_productoras.html'")
