# Dashboard interactivo con Streamlit: 
# necesito el segundo dataset
# está pendiente de hacer pero esta es la idea

import pandas as pd
import plotly.express as px
import streamlit as st

# Cargar datos
no_of = pd.read_excel("cannes_no_oficiales_con_paises.xlsx")
of = pd.read_excel("cannes_oficial.xlsx")

# Añadir columna de tipo
no_of["Tipo"] = "No Oficiales"
of["Tipo"] = "Sección Oficial"

# Unir datos
cannes = pd.concat([no_of, of], ignore_index=True)

# Título y filtros
st.title("Participación internacional en el Festival de Cannes")

seccion = st.selectbox("Selecciona sección:", ["Todas", "Sección Oficial", "No Oficiales"])
anio = st.slider("Selecciona año:", int(cannes["Año"].min()), int(cannes["Año"].max()), (2015, 2024))

# Filtro por selección
if seccion != "Todas":
    df = cannes[cannes["Tipo"] == seccion]
else:
    df = cannes.copy()

# Filtro por año
df = df[(df["Año"] >= anio[0]) & (df["Año"] <= anio[1])]

# Gráfico de evolución absoluta
st.subheader("Evolución de películas por país")
df_line = df.groupby("Año")[["España", "Francia", "EEUU"]].sum().reset_index()
fig1 = px.line(df_line, x="Año", y=["España", "Francia", "EEUU"], markers=True)
st.plotly_chart(fig1)

# Gráfico de porcentaje
st.subheader("Proporción anual de participación")
df_percent = df_line.copy()
df_percent[["España", "Francia", "EEUU"]] = df_percent[["España", "Francia", "EEUU"]].div(df_percent[["España", "Francia", "EEUU"]].sum(axis=1), axis=0) * 100
df_melted = df_percent.melt(id_vars="Año", var_name="País", value_name="Porcentaje")
fig2 = px.area(df_melted, x="Año", y="Porcentaje", color="País", groupnorm="percent")
st.plotly_chart(fig2)

# Top productoras
st.subheader("Top productoras por país")
df_top = df[df["Productoras"].notna() & df[["España", "Francia", "EEUU"]].any(axis=1)].copy()
df_top["Productoras lista"] = df_top["Productoras"].str.split(", ")

from collections import Counter

def top_productoras(df, pais):
    todas = []
    for _, row in df[df[pais]].iterrows():
        todas.extend(row["Productoras lista"])
    return Counter(todas).most_common(10)

for pais in ["España", "Francia", "EEUU"]:
    top = top_productoras(df_top, pais)
    st.write(f"**{pais}**")
    st.dataframe(pd.DataFrame(top, columns=["Productora", "Nº Películas"]))
