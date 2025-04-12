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

# Agrupar por país y año
df_total = df_countries.groupby("year")[["España", "Francia", "EEUU"]].sum().reset_index()

# Transformar el DataFrame para Plotly
df_melt = df_total.melt(id_vars="year", var_name="País", value_name="Número de películas")

# Crear gráfico interactivo
fig = px.line(
    df_melt,
    x="year",
    y="Número de películas",
    color="País",
    markers=True,
    title="Participación de España, Francia y EEUU en Cannes (sección oficial)",
    line_shape="spline"
)

fig.update_layout(
    title_font_size=20,
    legend_title="País",
    hovermode="x unified",
    template="plotly_white"
)

# Mostrar el gráfico
fig.show()

# Guardar el gráfico como archivo PNG
fig.write_image("grafico_cannes.png")
