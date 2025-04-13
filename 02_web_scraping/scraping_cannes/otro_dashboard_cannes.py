import pandas as pd
import plotly.express as px
import streamlit as st
import os
from collections import Counter

# Obtener la ruta del directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "datos_generados/cannes_con_productoras_normalizadas.xlsx")

# Cargar el archivo Excel
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

# Unir los datos procesados con el DataFrame original
df = pd.concat([df, df_countries[["España", "Francia", "EEUU"]]], axis=1)

# Título y filtros
st.title("Participación internacional en el Festival de Cannes")
anio = st.slider("Selecciona año:", int(df["year"].min()), int(df["year"].max()), (2015, 2024))

# Filtro por año
df_filtered = df[(df["year"] >= anio[0]) & (df["year"] <= anio[1])]

# Gráfico de evolución absoluta
st.subheader("Evolución de películas por país")
df_line = df_filtered.groupby("year")[["España", "Francia", "EEUU"]].sum().reset_index()
fig1 = px.line(df_line, x="year", y=["España", "Francia", "EEUU"], markers=True,
               title="Evolución de películas por país")
st.plotly_chart(fig1)

# Gráfico de porcentaje
st.subheader("Proporción anual de participación")
df_percent = df_line.copy()
df_percent[["España", "Francia", "EEUU"]] = df_percent[["España", "Francia", "EEUU"]].div(
    df_percent[["España", "Francia", "EEUU"]].sum(axis=1), axis=0) * 100

df_melted = df_percent.melt(id_vars="year", var_name="País", value_name="Porcentaje")
fig2 = px.area(df_melted, x="year", y="Porcentaje", color="País",
               title="Proporción anual de participación por país", groupnorm="percent")
st.plotly_chart(fig2)

# Top productoras
st.subheader("Top productoras por país")

# Mensajes de depuración para verificar los datos
st.subheader("Depuración de datos")

# Verificar si la columna existe
if "productoras_consolidadas_normalized" in df.columns:
    st.write("Columna 'productoras_consolidadas_normalized' encontrada.")
    st.write("Ejemplo de datos:")
    st.write(df["productoras_consolidadas_normalized"].head())

    # Verificar datos filtrados
    st.write("Datos filtrados por año:")
    st.write(df_filtered.head())

    # Verificar datos de productoras
    df_top = df_filtered[df_filtered["productoras_consolidadas_normalized"].notna() & df_filtered[["España", "Francia", "EEUU"]].any(axis=1)].copy()
    st.write("Datos después de filtrar por productoras:")
    st.write(df_top.head())

    # Filtrar datos relevantes y crear lista de productoras
    df_top = df_filtered[df_filtered["productoras_consolidadas_normalized"].notna() & 
                         df_filtered[["España", "Francia", "EEUU"]].any(axis=1)].copy()
    df_top["Productoras lista"] = df_top["productoras_consolidadas_normalized"].str.split(", ")

    def top_productoras(df, pais):
        todas = []
        for _, row in df[df[pais] == 1].iterrows():
            todas.extend(row["Productoras lista"])
        return Counter(todas).most_common(10)

    for pais in ["España", "Francia", "EEUU"]:
        top = top_productoras(df_top, pais)
        st.write(f"**{pais}**")
        st.dataframe(pd.DataFrame(top, columns=["Productora", "Nº Películas"]))
else:
    st.write("La columna 'productoras_consolidadas_normalized' no está disponible en los datos.")
