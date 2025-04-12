import pandas as pd
import plotly.express as px
import os

# Obtener la ruta del directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "cannes_seccion_oficial_wiki_con_paises_y_enlaces.xlsx")

# Cargar el Excel
df = pd.read_excel(file_path)

# Procesar la columna 'country_esp_fra_usa' para contar películas por país
df_countries = df["country_esp_fra_usa"].str.get_dummies(sep=",")
df_countries["year"] = df["year"]

# Renombrar columnas para incluir las banderas
column_mapping = {
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
}
df_countries.rename(columns=column_mapping, inplace=True)

# Agrupar por año
df_total = df_countries.groupby("year")[["España", "Francia", "EEUU"]].sum()

# Calcular total de películas por año (todas las nacionalidades)
df_total["Total año"] = df_total.sum(axis=1)

# Calcular porcentaje por país
df_percent = df_total[["España", "Francia", "EEUU"]].div(df_total["Total año"], axis=0) * 100
df_percent = df_percent.reset_index()

# Transformar formato para plotly
df_melt = df_percent.melt(id_vars="year", var_name="País", value_name="Porcentaje")

# Crear gráfico de líneas apiladas (stacked area chart)
fig = px.area(
    df_melt,
    x="year",
    y="Porcentaje",
    color="País",
    title="Porcentaje de participación por país (España, Francia, EEUU) en Cannes",
    groupnorm="percent"
)

fig.update_layout(
    title_font_size=20,
    yaxis_title="Porcentaje (%)",
    template="plotly_white",
    legend_title="País"
)

fig.show()
fig.write_image("grafico_peso_proporcional_pais.png")
