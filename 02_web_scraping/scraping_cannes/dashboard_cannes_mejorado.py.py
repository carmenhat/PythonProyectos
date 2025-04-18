import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from collections import Counter
import re

# Configuración de la página
st.set_page_config(
    page_title="Festival de Cannes - Análisis Internacional",
    page_icon="🎬",
    layout="wide"
)

# Funciones auxiliares
def extract_flag_emoji(country_text):
    """Extrae el emoji de bandera de un texto de país"""
    if pd.isna(country_text):
        return ""
    match = re.search(r'(\p{So}\p{So})', country_text, re.UNICODE)
    return match.group(1) if match else ""

def get_countries_from_string(country_string):
    """Convierte una cadena como 'France, USA' en ['France', 'USA']"""
    if pd.isna(country_string) or country_string.strip() == "":
        return []
    return [c.strip().title() for c in country_string.split(',') if c.strip()]


def count_countries(df, country_column):
    """Cuenta la frecuencia de cada país en el DataFrame"""
    all_countries = []
    for countries in df[country_column].dropna():
        all_countries.extend(get_countries_from_string(countries))
    return Counter(all_countries)

# Cargar datos
@st.cache_data
def load_data():
    # Intentar cargar el archivo con datos expandidos, si no existe usar el anterior
    script_dir = os.path.dirname(os.path.abspath(__file__))
    expanded_file = os.path.join(script_dir, "datos_generados/cannes_dataset_unificado.xlsx")
    original_file = os.path.join(script_dir, "datos_generados/cannes_con_productoras_normalizadas.xlsx")
    
    if os.path.exists(expanded_file):
        file_path = expanded_file
        st.sidebar.success("✅ Usando datos expandidos con información adicional de países")
    else:
        file_path = original_file
        st.sidebar.warning("⚠️ Archivo de datos expandidos no encontrado. Usando datos originales.")
    
    # Cargar el DataFrame
    df = pd.read_excel(file_path)
    
    # Crear columna para análisis basada en los datos disponibles
    if 'country_expanded' in df.columns:
        df['countries_for_analysis'] = df['country_expanded']
    elif 'countries' in df.columns:
        df['countries_for_analysis'] = df['countries']
    else:
        st.error("❌ No se encontró ninguna columna válida de países. Añade 'country_expanded' o 'countries'.")
        st.stop()


    
    # Extraer año como entero
    df['year'] = df['year'].astype(int)
    
    # Generar columnas dummy para cada país
    unique_countries = set()
    for countries in df['countries_for_analysis'].dropna():
        unique_countries.update(get_countries_from_string(countries))
    
    # Crear columnas binarias para cada país
    for country in unique_countries:
        df[country] = df['countries_for_analysis'].apply(
            lambda x: 1 if country in get_countries_from_string(x) else 0
        )


    df['total_movies'] = df[list(unique_countries)].sum(axis=1)

    
    return df, list(unique_countries)

# Cargar los datos
df, all_countries = load_data()


# Encabezado
st.title("🎬 Análisis Internacional del Festival de Cannes")
st.markdown("""
Este dashboard analiza la participación internacional en el Festival de Cannes, 
mostrando tendencias a lo largo del tiempo y las productoras más activas por país.
""")

# Barra lateral - Filtros
st.sidebar.header("Filtros")

# Filtro de año
min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Rango de años:",
    min_year, max_year, 
    (max(min_year, max_year-10), max_year)  # Por defecto últimos 10 años
)

# Filtros avanzados en un expander
with st.sidebar.expander("Filtros avanzados"):
    # Selección de países para análisis
    selected_countries = st.multiselect(
        "Países a incluir en análisis:",
        sorted(all_countries),
        default=[c for c in all_countries if any(x in c for x in ["Spain", "France", "USA", "Italy", "United Kingdom", "Germany"])]
    )
    
    # Filtro por sección si existe la columna
    if 'section' in df.columns:
        sections = ['Todas'] + sorted(df['section'].dropna().unique().tolist())
        selected_section = st.selectbox("Sección:", sections)
    else:
        selected_section = "Todas"

# Aplicar filtros
filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

# Filtrar por sección si se seleccionó una específica
if 'section' in df.columns and selected_section != "Todas":
    filtered_df = filtered_df[filtered_df['section'] == selected_section]

# Inicializar tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Evolución Temporal", 
    "🌍 Distribución Geográfica", 
    "🏢 Productoras por País",
    "📋 Datos Detallados"
])

# Tab 1: Evolución Temporal
with tab1:
    st.header("Evolución de participación por país a lo largo del tiempo")
    
    # Preparar datos para evolución temporal
    if selected_countries:
        df_line = filtered_df.groupby("year")[selected_countries].sum().reset_index()
        
        # Gráfico de evolución absoluta
        col1, col2 = st.columns(2)
        
        with col1:
            fig_line = px.line(
                df_line, x="year", y=selected_countries,
                markers=True, 
                title="Evolución de películas por país"
            )
            fig_line.update_layout(
                xaxis_title="Año",
                yaxis_title="Número de películas",
                legend_title="País"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Gráfico de proporción
        with col2:
            # Calcular porcentajes
            df_percent = df_line.copy()
            row_sums = df_percent[selected_countries].sum(axis=1)
            for country in selected_countries:
                df_percent[country] = df_percent[country] / row_sums * 100
            
            df_melted = df_percent.melt(
                id_vars="year", 
                value_vars=selected_countries,
                var_name="País", 
                value_name="Porcentaje"
            )
            
            fig_area = px.area(
                df_melted, 
                x="year", 
                y="Porcentaje", 
                color="País",
                title="Proporción anual por país", 
                groupnorm="percent"
            )
            fig_area.update_layout(
                xaxis_title="Año",
                yaxis_title="Porcentaje",
                legend_title="País"
            )
            st.plotly_chart(fig_area, use_container_width=True)
    
    else:
        st.warning("🔍 Por favor selecciona al menos un país para visualizar la evolución temporal.")

# Tab 2: Distribución Geográfica
with tab2:
    st.header("Representación geográfica")
    
    # Conteo total de películas por país
    country_counts = count_countries(filtered_df, 'countries_for_analysis')
    
    # Crear DataFrame para visualización
    df_counts = pd.DataFrame({
        'País': list(country_counts.keys()),
        'Películas': list(country_counts.values())
    })
    
    # Ordenar por cantidad de películas
    df_counts = df_counts.sort_values('Películas', ascending=False)
    
    # Top países
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Gráfico de barras horizontal
        fig_bars = px.bar(
            df_counts.head(15),  # Top 15 países
            y='País',
            x='Películas',
            orientation='h',
            title=f"Top países en el Festival de Cannes ({year_range[0]}-{year_range[1]})"
        )
        fig_bars.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bars, use_container_width=True)
    
    with col2:
        # Tabla con todos los países
        st.subheader("Total de películas por país")
        st.dataframe(
            df_counts,
            column_config={
                "País": st.column_config.TextColumn("País"),
                "Películas": st.column_config.NumberColumn("Películas", format="%d")
            },
            hide_index=True,
            height=400
        )
    
    # Co-producciones
    st.subheader("Análisis de Co-producciones")
    
    # Contar películas por número de países involucrados
    filtered_df['num_countries'] = filtered_df['countries_for_analysis'].apply(
        lambda x: 0 if pd.isna(x) else len(get_countries_from_string(x))
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución de co-producciones
        coprod_counts = filtered_df['num_countries'].value_counts().sort_index()
        coprod_df = pd.DataFrame({
            'Número de países': coprod_counts.index,
            'Películas': coprod_counts.values
        })
        
        fig_coprod = px.bar(
            coprod_df,
            x='Número de países',
            y='Películas',
            title="Distribución de co-producciones",
            text_auto=True
        )
        fig_coprod.update_xaxes(type='category')
        st.plotly_chart(fig_coprod, use_container_width=True)
    
    with col2:
        # Evolución de co-producciones a lo largo del tiempo
        avg_countries = filtered_df.groupby('year')['num_countries'].mean().reset_index()
        
        fig_avg = px.line(
            avg_countries,
            x='year',
            y='num_countries',
            title="Evolución del promedio de países por película",
            markers=True
        )
        fig_avg.update_layout(
            xaxis_title="Año",
            yaxis_title="Promedio de países por película"
        )
        st.plotly_chart(fig_avg, use_container_width=True)

# Tab 3: Productoras por País
with tab3:
    st.header("Principales productoras por país")
    
    if "productoras_consolidadas_normalized" in filtered_df.columns:
        # Crear lista de productoras para cada película
        filtered_df["productoras_lista"] = filtered_df["productoras_consolidadas_normalized"].apply(
            lambda x: [] if pd.isna(x) else [p.strip() for p in str(x).split(',')]
        )
        
        # Función para obtener top productoras por país
        def get_top_productoras(df, country_column, country_value, n=10):
            country_movies = df[df[country_column] == 1]
            all_productoras = []
            for productoras in country_movies["productoras_lista"]:
                all_productoras.extend(productoras)
            
            # Contar y obtener las más frecuentes
            counter = Counter(all_productoras)
            return counter.most_common(n)
        
        # Filtro de país para productoras
        selected_country = st.selectbox(
            "Selecciona un país para ver sus principales productoras:",
            [c for c in all_countries if c in filtered_df.columns],
            index=0
        )
        
        # Mostrar top productoras para el país seleccionado
        top_productoras = get_top_productoras(filtered_df, selected_country, 1)
        
        if top_productoras:
            # Crear DataFrame para visualización
            df_productoras = pd.DataFrame(top_productoras, columns=["Productora", "Películas"])
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Gráfico de barras
                fig_prod = px.bar(
                    df_productoras,
                    y="Productora",
                    x="Películas",
                    orientation="h",
                    title=f"Top productoras de {selected_country}"
                )
                fig_prod.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_prod, use_container_width=True)
            
            with col2:
                # Tabla con datos
                st.dataframe(
                    df_productoras,
                    hide_index=True,
                    column_config={
                        "Productora": st.column_config.TextColumn("Productora"),
                        "Películas": st.column_config.NumberColumn("Películas", format="%d")
                    }
                )
        else:
            st.info(f"No hay datos de productoras para películas de {selected_country} en el período seleccionado.")
    else:
        st.warning("⚠️ No se encontró la columna 'productoras_consolidadas_normalized' en los datos.")

# Tab 4: Datos Detallados
with tab4:
    st.header("Películas en la selección")
    
    # Seleccionar columnas relevantes para mostrar
    display_columns = ['title', 'director', 'year', 'countries_for_analysis']
    
    # Añadir sección si está disponible
    if 'section' in filtered_df.columns:
        display_columns.insert(3, 'section')
    
    # Añadir productoras si están disponibles
    if 'productoras_consolidadas_normalized' in filtered_df.columns:
        display_columns.append('productoras_consolidadas_normalized')
    
    # Mostrar datos
    st.dataframe(
        filtered_df[display_columns].sort_values(['year', 'title'], ascending=[False, True]),
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Título"),
            "director": st.column_config.TextColumn("Director"),
            "year": st.column_config.NumberColumn("Año"),
            "section": st.column_config.TextColumn("Sección"),
            "countries_for_analysis": st.column_config.TextColumn("Países"),
            "productoras_consolidadas_normalized": st.column_config.TextColumn("Productoras")
        }
    )

# Footer
st.markdown("---")
st.caption("Datos extraídos de IMDb y otras fuentes. Análisis de películas en competición del Festival de Cannes.")
