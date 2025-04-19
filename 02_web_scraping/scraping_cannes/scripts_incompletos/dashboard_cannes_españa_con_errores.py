# dashboard_cannes_espana.py

# me falta la columna de España en el excel  cannes_dataset_unificado.xlsx
# tengo que ver como la proceso  porque he hecho muchos cambios en el excel original

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from collections import Counter
import re

# Configuración de la página
st.set_page_config(
    page_title="Festival de Cannes - Participación Española",
    page_icon="🇪🇸",
    layout="wide"
)

# -------------------- FUNCIONES AUXILIARES --------------------

def get_countries_from_string(country_string):
    if pd.isna(country_string) or country_string == "":
        return []
    return [c.strip() for c in country_string.split(',')]

def count_countries(df, country_column):
    all_countries = []
    for countries in df[country_column].dropna():
        all_countries.extend(get_countries_from_string(countries))
    return Counter(all_countries)

# -------------------- CARGA DE DATOS --------------------

@st.cache_data

def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    expanded_file = os.path.join(script_dir, "datos_generados/cannes_dataset_unificado.xlsx")
    original_file = os.path.join(script_dir, "datos_generados/cannes_con_productoras_normalizadas.xlsx")
    
    file_path = expanded_file if os.path.exists(expanded_file) else original_file
    df = pd.read_excel(file_path)

    df['countries_for_analysis'] = df['country_expanded'] if 'country_expanded' in df.columns else df['country_esp_fra_usa']
    df['year'] = df['year'].astype(int)

    unique_countries = set()
    for countries in df['countries_for_analysis'].dropna():
        unique_countries.update(get_countries_from_string(countries))

    for country in unique_countries:
        df[country] = df['countries_for_analysis'].apply(lambda x: 1 if pd.notna(x) and country in x else 0)

    df['num_countries'] = df['countries_for_analysis'].apply(lambda x: len(get_countries_from_string(x)))
    df['is_spanish_only'] = df.apply(lambda row: row['Spain'] == 1 and row['num_countries'] == 1, axis=1)
    return df, list(unique_countries)

# -------------------- INICIO APP --------------------

df, all_countries = load_data()

st.title("🌟 Participación Española en el Festival de Cannes")
st.markdown("""
Análisis visual e interactivo de la contribución española al Festival de Cannes, destacando su presencia anual,
colaboraciones internacionales y principales productoras.
""")

# -------------------- FILTROS --------------------

st.sidebar.header("Filtros")

min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("Rango de años:", min_year, max_year, (2000, max_year))
solo_espana = st.sidebar.checkbox("🇪🇸 Solo películas con participación española", value=True)
sin_coproducciones = st.sidebar.checkbox("🌐 Excluir coproducciones", value=False)

# Aplicar filtros
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])]
if solo_espana:
    filtered_df = filtered_df[filtered_df['Spain'] == 1]
if sin_coproducciones:
    filtered_df = filtered_df[filtered_df['is_spanish_only'] == True]

# -------------------- MÉTRICAS --------------------

col1, col2, col3 = st.columns(3)
col1.metric("Películas españolas", len(filtered_df))
col2.metric("Años de participación", filtered_df['year'].nunique())
col3.metric("Productoras distintas", filtered_df['productoras_consolidadas_normalized'].nunique() if 'productoras_consolidadas_normalized' in filtered_df else 0)

# -------------------- EVOLUCIÓN TEMPORAL --------------------

st.subheader("📊 Evolución anual de la participación española")
df_yearly = filtered_df.groupby('year').agg({"title": "count", "num_countries": "mean"}).reset_index()
df_yearly.rename(columns={"title": "peliculas", "num_countries": "promedio_paises"}, inplace=True)

fig = px.line(df_yearly, x="year", y="peliculas", markers=True,
              title="Películas con participación española por año")
st.plotly_chart(fig, use_container_width=True)

# -------------------- PRODUCTORAS --------------------

st.subheader("🏢 Principales productoras españolas")
if "productoras_consolidadas_normalized" in filtered_df.columns:
    filtered_df["productoras_lista"] = filtered_df["productoras_consolidadas_normalized"].apply(
        lambda x: [] if pd.isna(x) else [p.strip() for p in str(x).split(',')]
    )
    todas = []
    for lista in filtered_df["productoras_lista"]:
        todas.extend(lista)
    top = Counter(todas).most_common(15)
    df_top = pd.DataFrame(top, columns=["Productora", "Películas"])
    fig_prod = px.bar(df_top, x="Películas", y="Productora", orientation='h',
                      title="Top 15 productoras españolas")
    fig_prod.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_prod, use_container_width=True)

# -------------------- COPRODUCCIONES --------------------

st.subheader("🌐 Países con más coproducciones junto a España")

def top_coproducers(df, base_country="Spain"):
    copros = []
    for countries in df['countries_for_analysis']:
        paises = get_countries_from_string(countries)
        if base_country in paises:
            paises.remove(base_country)
            copros.extend(paises)
    return Counter(copros).most_common(10)

top_paises = top_coproducers(filtered_df)
df_copros = pd.DataFrame(top_paises, columns=["País", "Películas"])
fig_copros = px.bar(df_copros, x="Películas", y="País", orientation="h")
st.plotly_chart(fig_copros, use_container_width=True)

# -------------------- DATOS DETALLADOS --------------------

st.subheader("📊 Listado de películas")

cols_to_show = ["title", "director", "year", "section", "countries_for_analysis", "productoras_consolidadas_normalized"]
cols_presentes = [col for col in cols_to_show if col in filtered_df.columns]

st.dataframe(filtered_df[cols_presentes].sort_values(['year', 'title'], ascending=[False, True]), hide_index=True)

st.caption("Análisis centrado en la participación española en Cannes. Datos extraídos de IMDb y otras fuentes.")
