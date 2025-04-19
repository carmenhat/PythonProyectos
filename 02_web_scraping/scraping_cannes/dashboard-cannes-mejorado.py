import pandas as pd
import streamlit as st
import os
import sys

# Añadir la carpeta de módulos al path
script_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(script_dir, "modules")
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)
sys.path.append(modules_dir)

# Importar módulos
from modules.data_processing import load_data, filter_data, get_countries_from_string
from modules.visualizations import (
    create_country_evolution_chart, 
    create_country_proportion_chart,
    create_coproduction_distribution_chart, 
    create_average_countries_chart,
    create_top_companies_chart,
    create_choropleth_map,
    create_coproduction_heatmap,
    create_network_graph
)
from modules.kpis import calculate_kpis

# Configuración de la página
st.set_page_config(
    page_title="Festival de Cannes - Análisis Internacional",
    page_icon="🎬",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
<style>
    .kpi-box {
        background-color: #f0f2f6;
        border-radius: 7px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        color: #FF4B4B;
    }
    .kpi-label {
        font-size: 14px;
        color: #555;
    }
    .spain-highlight {
        background-color: #ffe6e6;
        border-left: 4px solid #FF4B4B;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado
st.title("🎬 Análisis Internacional del Festival de Cannes")
st.markdown("""
Este dashboard analiza la participación internacional en el Festival de Cannes, 
mostrando tendencias a lo largo del tiempo, con un enfoque especial en la participación española.
""")

# Cargar los datos
df, all_countries = load_data()

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
        default=["Spain", "France", "USA", "Italy", "United Kingdom", "Germany"]
    )
    
    # Filtro por sección si existe la columna
    if 'section' in df.columns:
        sections = ['Todas'] + sorted(df['section'].dropna().unique().tolist())
        selected_section = st.selectbox("Sección:", sections)
    else:
        selected_section = "Todas"

# Aplicar filtros
filtered_df = filter_data(df, year_range, selected_section)

# Pestaña de KPIs con enfoque en España
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 KPIs y Resumen", 
    "🇪🇸 España en Cannes",
    "📈 Evolución Temporal", 
    "🌍 Distribución Geográfica", 
    "🔄 Co-producciones",
    "📋 Datos Detallados"
])

# Tab 1: KPIs y Resumen
with tab1:
    st.header("Principales métricas")
    
    # Cálculo de KPIs
    kpis = calculate_kpis(filtered_df, selected_countries)
    
    # Mostrar KPIs en una fila
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{kpis['total_films']}</div>
            <div class="kpi-label">Total películas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{kpis['total_countries']}</div>
            <div class="kpi-label">Países participantes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{kpis['avg_countries_per_film']:.2f}</div>
            <div class="kpi-label">Media países/película</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{kpis['coproduction_percentage']:.1f}%</div>
            <div class="kpi-label">% Co-producciones</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mapa coroplético
    st.subheader("Mapa de participación global")
    choropleth_map = create_choropleth_map(filtered_df)
    st.plotly_chart(choropleth_map, use_container_width=True)
    
    # Heatmap de co-producciones
    st.subheader("Heatmap de co-producciones")
    if selected_countries:
        coproduction_heatmap = create_coproduction_heatmap(filtered_df, selected_countries)
        st.plotly_chart(coproduction_heatmap, use_container_width=True)
    else:
        st.info("Selecciona países en los filtros para ver el heatmap de co-producciones")

# Tab 2: España en Cannes
with tab2:
    st.header("Análisis de la participación española")
    
    # Verificar si España está en los datos
    if "Spain" in all_countries:
        # KPIs específicos de España
        spain_kpis = calculate_kpis(filtered_df, ["Spain"], focus_country="Spain")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-value">{spain_kpis['country_films']}</div>
                <div class="kpi-label">Películas con participación española</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-value">{spain_kpis['country_percentage']:.1f}%</div>
                <div class="kpi-label">% del total de películas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-value">{spain_kpis['country_coproductions']}</div>
                <div class="kpi-label">Co-producciones con otros países</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Evolución temporal de España
        st.subheader("Evolución de la participación española")
        spain_evolution = create_country_evolution_chart(filtered_df, ["Spain"])
        st.plotly_chart(spain_evolution, use_container_width=True)
        
        # Principales co-productores con España
        st.subheader("Principales países co-productores con España")
        
        # Red de co-producciones
        st.subheader("Red de co-producciones con España")
        network_graph = create_network_graph(filtered_df, focus_country="Spain")
        st.plotly_chart(network_graph, use_container_width=True)
        
        # Productoras españolas
        st.subheader("Principales productoras españolas")
        if "productoras_consolidadas_normalized" in filtered_df.columns:
            spain_companies = create_top_companies_chart(filtered_df, "Spain")
            st.plotly_chart(spain_companies, use_container_width=True)
        else:
            st.warning("No se encontraron datos de productoras en el dataset")
    else:
        st.warning("No se encontraron datos para España en el período seleccionado")

# Tab 3: Evolución Temporal
with tab3:
    st.header("Evolución de participación por país a lo largo del tiempo")
    
    # Preparar datos para evolución temporal
    if selected_countries:
        col1, col2 = st.columns(2)
        
        with col1:
            evolution_chart = create_country_evolution_chart(filtered_df, selected_countries)
            st.plotly_chart(evolution_chart, use_container_width=True)
        
        with col2:
            proportion_chart = create_country_proportion_chart(filtered_df, selected_countries)
            st.plotly_chart(proportion_chart, use_container_width=True)
    
    else:
        st.warning("🔍 Por favor selecciona al menos un país para visualizar la evolución temporal.")

# Tab 4: Distribución Geográfica
with tab4:
    st.header("Representación geográfica")
    
    # Mapa coroplético de todos los países
    choropleth_map = create_choropleth_map(filtered_df)
    st.plotly_chart(choropleth_map, use_container_width=True)
    
    # Top países en formato tabla
    country_counts = filtered_df['countries_for_analysis'].apply(get_countries_from_string).explode().value_counts()
    top_countries_df = pd.DataFrame({
        'País': country_counts.index,
        'Películas': country_counts.values
    })
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader(f"Top países en el Festival de Cannes ({year_range[0]}-{year_range[1]})")
        st.dataframe(
            top_countries_df.head(15),
            column_config={
                "País": st.column_config.TextColumn("País"),
                "Películas": st.column_config.NumberColumn("Películas", format="%d")
            },
            hide_index=True
        )
    
    with col2:
        st.subheader("Distribución continental")
        # Aquí iría un gráfico de distribución por continentes
        # (requiere mapeo de países a continentes, lo cual sería parte de un módulo)
        st.info("Visualización de distribución por continentes - Pendiente de implementar")

# Tab 5: Co-producciones
with tab5:
    st.header("Análisis de Co-producciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        coproduction_distribution = create_coproduction_distribution_chart(filtered_df)
        st.plotly_chart(coproduction_distribution, use_container_width=True)
    
    with col2:
        avg_countries_chart = create_average_countries_chart(filtered_df)
        st.plotly_chart(avg_countries_chart, use_container_width=True)
    
    # Red de co-producciones entre países seleccionados
    st.subheader("Red de co-producciones")
    
    if selected_countries and len(selected_countries) > 1:
        network_graph = create_network_graph(filtered_df, countries=selected_countries)
        st.plotly_chart(network_graph, use_container_width=True)
    else:
        st.info("Selecciona al menos 2 países para visualizar la red de co-producciones")
    
    # Heatmap de co-producciones
    st.subheader("Matriz de co-producciones")
    if selected_countries and len(selected_countries) > 1:
        coproduction_heatmap = create_coproduction_heatmap(filtered_df, selected_countries)
        st.plotly_chart(coproduction_heatmap, use_container_width=True)
    else:
        st.info("Selecciona al menos 2 países para visualizar la matriz de co-producciones")

# Tab 6: Datos Detallados
with tab6:
    st.header("Películas en la selección")
    
    # Seleccionar columnas relevantes para mostrar
    display_columns = ['title', 'director', 'year', 'countries_for_analysis']
    
    # Añadir sección si está disponible
    if 'section' in filtered_df.columns:
        display_columns.insert(3, 'section')
    
    # Añadir productoras si están disponibles
    if 'productoras_consolidadas_normalized' in filtered_df.columns:
        display_columns.append('productoras_consolidadas_normalized')
    
    # Filtro específico para buscar películas
    search_term = st.text_input("Buscar película por título o director:")
    if search_term:
        search_results = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) | 
            filtered_df['director'].str.contains(search_term, case=False, na=False)
        ]
        st.dataframe(
            search_results[display_columns].sort_values(['year', 'title'], ascending=[False, True]),
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
    else:
        # Mostrar todos los datos filtrados
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
st.caption("Datos extraídos de IMDb y otras fuentes. Análisis de películas en el Festival de Cannes.")
