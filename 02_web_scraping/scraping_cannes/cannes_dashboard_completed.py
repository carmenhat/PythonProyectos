import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from collections import Counter
import re
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Festival de Cannes - Análisis Internacional",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS personalizado para mejorar la interfaz
st.markdown("""
<style>
    /* Estilo para el título principal */
    .main-title {
        color: #E50914;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Estilo para subtítulos */
    .subtitle {
        color: #333;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #E50914;
        padding-bottom: 0.3rem;
    }
    
    /* Estilo para tarjetas de métricas */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
        border-left: 4px solid #E50914;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Mejora del diseño de pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        background-color: #f1f3f4;
        border-radius: 4px 4px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E50914 !important;
        color: white !important;
    }
    
    /* Estilo para la leyenda de gráficos */
    .custom-legend {
        font-size: 0.8rem;
        background-color: rgba(255,255,255,0.8);
        border-radius: 3px;
        padding: 5px;
    }
    
    /* Estilo para tooltips */
    div[data-testid="stTooltipIcon"] {
        color: #E50914;
    }
    
    /* Estilo para la barra lateral */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Estilo para badges/etiquetas */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-spain {
        background-color: #FFCC00;
        color: #AA151B;
    }
    
    .badge-france {
        background-color: #002654;
        color: white;
    }
    
    .badge-italy {
        background-color: #008C45;
        color: white;
    }
    
    .badge-usa {
        background-color: #3C3B6E;
        color: white;
    }
    
    /* Estilo para los indicadores de KPI */
    .kpi-container {
        display: flex;
        flex-direction: column;
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .kpi-title {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #E50914;
    }
    
    .kpi-trend {
        font-size: 0.8rem;
        margin-top: 5px;
    }
    
    .trend-up {
        color: green;
    }
    
    .trend-down {
        color: red;
    }
    
    .trend-neutral {
        color: orange;
    }
    
    /* Nuevos estilos para mejoras */
    .kpi-highlight {
        border-left: 4px solid #FFCC00;
        background: linear-gradient(to right, rgba(255,204,0,0.1), rgba(255,255,255,0));
    }
    
    .tooltip-icon {
        color: #E50914;
        font-size: 16px;
        cursor: help;
    }
    
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    /* Estilos para el mapa de calor */
    .heatmap-container {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Mejoras para la red de co-producciones */
    .network-tooltip {
        background-color: rgba(255,255,255,0.9);
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Funciones auxiliares
def extract_flag_emoji(country_text):
    """Extrae el emoji de bandera de un texto de país"""
    if pd.isna(country_text):
        return ""
    match = re.search(r'(\p{So}\p{So})', country_text, re.UNICODE)
    return match.group(1) if match else ""

def get_countries_from_string(country_string):
    """Divide una cadena de países en una lista"""
    if pd.isna(country_string) or country_string == "":
        return []
    return [c.strip() for c in country_string.split(',')]

def count_countries(df, country_column):
    """Cuenta la frecuencia de cada país en el DataFrame"""
    all_countries = []
    for countries in df[country_column].dropna():
        all_countries.extend(get_countries_from_string(countries))
    return Counter(all_countries)

def get_coproduction_links(df, country_column):
    """Genera enlaces para gráfico de red de co-producciones"""
    links = []
    for _, row in df.iterrows():
        if pd.isna(row[country_column]):
            continue
        
        countries = get_countries_from_string(row[country_column])
        if len(countries) > 1:  # Es una co-producción
            # Generar todas las combinaciones de países
            for i in range(len(countries)):
                for j in range(i+1, len(countries)):
                    links.append((countries[i], countries[j]))
    
    # Contar frecuencia de cada enlace
    link_counter = Counter(links)
    
    # Convertir a formato para gráfico de red
    source = []
    target = []
    weight = []
    
    for (src, tgt), count in link_counter.items():
        source.append(src)
        target.append(tgt)
        weight.append(count)
    
    return source, target, weight

def calculate_spain_kpis(df, year_range):
    """Calcula KPIs específicos para España"""
    results = {}
    
    # Total de películas españolas en el rango
    total_spain = df[df['Spain'] == 1].shape[0]
    results['total'] = total_spain
    
    # Porcentaje respecto al total
    total_movies = df.shape[0]
    results['percentage'] = (total_spain / total_movies) * 100 if total_movies > 0 else 0
    
    # Posición en el ranking de países
    country_counts = count_countries(df, 'countries_for_analysis')
    country_ranking = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    spain_position = -1
    for i, (country, _) in enumerate(country_ranking):
        if country == 'Spain':
            spain_position = i + 1
            break
    results['ranking'] = spain_position
    
    # Co-producciones con España
    spain_movies = df[df['Spain'] == 1]
    coprods_spain = spain_movies[spain_movies['num_countries'] > 1].shape[0]
    results['coproductions'] = coprods_spain
    results['coprod_percentage'] = (coprods_spain / total_spain) * 100 if total_spain > 0 else 0
    
    # Tendencia (comparando con periodo anterior si hay datos suficientes)
    if year_range[1] - year_range[0] >= 5:
        # Dividir el rango en dos periodos
        mid_year = (year_range[0] + year_range[1]) // 2
        first_period = df[(df['year'] >= year_range[0]) & (df['year'] <= mid_year)]
        second_period = df[(df['year'] > mid_year) & (df['year'] <= year_range[1])]
        
        # Calcular películas en cada periodo
        spain_first = first_period[first_period['Spain'] == 1].shape[0]
        spain_second = second_period[second_period['Spain'] == 1].shape[0]
        
        # Calcular tendencia (porcentaje de cambio)
        if spain_first > 0:
            trend_pct = ((spain_second - spain_first) / spain_first) * 100
            results['trend'] = trend_pct
        else:
            results['trend'] = 0
    else:
        results['trend'] = None
    
    # Tasa de crecimiento anual compuesto (CAGR)
    # NUEVA MÉTRICA
    if year_range[1] > year_range[0]:
        years_diff = year_range[1] - year_range[0]
        
        # Películas en el primer y último año
        start_year_films = df[df['year'] == year_range[0]][df['Spain'] == 1].shape[0]
        end_year_films = df[df['year'] == year_range[1]][df['Spain'] == 1].shape[0]
        
        # Evitar división por cero
        if start_year_films > 0 and years_diff > 0:
            cagr = ((end_year_films / start_year_films) ** (1 / years_diff) - 1) * 100
            results['cagr'] = cagr
        else:
            results['cagr'] = 0
    else:
        results['cagr'] = 0
    
    # Métrica de consistencia (desviación estándar de participación)
    # NUEVA MÉTRICA
    yearly_spain = df.groupby('year')['Spain'].sum()
    results['consistency'] = yearly_spain.std()
    
    return results

def get_top_coprod_countries_with_spain(df):
    """Obtiene los principales países co-productores con España"""
    spain_movies = df[df['Spain'] == 1]
    
    # Extraer países co-productores con España
    coprod_countries = []
    for countries in spain_movies['countries_for_analysis'].dropna():
        country_list = get_countries_from_string(countries)
        # Solo añadir países que no sean España
        coprod_countries.extend([c for c in country_list if c != 'Spain'])
    
    return Counter(coprod_countries).most_common(10)  # Ampliado a 10 para el mapa de calor

def generate_coproduction_heatmap_data(df, focus_country="Spain"):
    """Genera datos para el mapa de calor de co-producciones"""
    focus_movies = df[df[focus_country] == 1]
    
    # Obtener todos los países que co-producen con el país de enfoque
    coprod_countries = set()
    for countries in focus_movies['countries_for_analysis'].dropna():
        country_list = get_countries_from_string(countries)
        # Añadir países que no sean el de enfoque
        coprod_countries.update([c for c in country_list if c != focus_country])
    
    # Convertir a lista ordenada
    coprod_countries = sorted(list(coprod_countries))
    
    # Crear matriz para el mapa de calor
    heatmap_data = np.zeros((len(coprod_countries), len(coprod_countries)))
    
    # Para cada película, contar co-producciones entre países
    for _, row in focus_movies.iterrows():
        if pd.isna(row['countries_for_analysis']):
            continue
            
        countries = [c for c in get_countries_from_string(row['countries_for_analysis']) if c != focus_country]
        
        # Para cada par de países en esta película
        for i, country1 in enumerate(countries):
            if country1 not in coprod_countries:
                continue
                
            idx1 = coprod_countries.index(country1)
            
            # Diagonal (solo el país)
            heatmap_data[idx1, idx1] += 1
            
            # Conexiones entre países
            for j, country2 in enumerate(countries[i+1:], i+1):
                if country2 not in coprod_countries:
                    continue
                    
                idx2 = coprod_countries.index(country2)
                heatmap_data[idx1, idx2] += 1
                heatmap_data[idx2, idx1] += 1  # Simétrico
    
    return heatmap_data, coprod_countries

def calculate_yearly_rankings(df, countries):
    """Calcula el ranking de países por año"""
    rankings = {}
    
    # Para cada año en el dataset
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        
        # Contar películas por país en este año
        country_counts = {}
        for country in countries:
            country_counts[country] = year_df[country].sum()
        
        # Ordenar países por número de películas
        sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Guardar ranking para este año
        rankings[year] = {country: rank+1 for rank, (country, _) in enumerate(sorted_countries)}
    
    return rankings

def get_spain_yearly_metrics(df, countries):
    """Obtiene métricas anuales para España"""
    years = sorted(df['year'].unique())
    metrics = {
        'year': years,
        'total_films': [],
        'spain_films': [],
        'spain_percentage': [],
        'spain_ranking': [],
        'spain_coprods': []
    }
    
    # Rankings anuales
    yearly_rankings = calculate_yearly_rankings(df, countries)
    
    for year in years:
        year_df = df[df['year'] == year]
        
        # Total de películas este año
        total = len(year_df)
        metrics['total_films'].append(total)
        
        # Películas españolas
        spain_films = year_df[year_df['Spain'] == 1].shape[0]
        metrics['spain_films'].append(spain_films)
        
        # Porcentaje español
        spain_pct = (spain_films / total) * 100 if total > 0 else 0
        metrics['spain_percentage'].append(spain_pct)
        
        # Ranking de España este año
        spain_ranking = yearly_rankings[year].get('Spain', 0)
        metrics['spain_ranking'].append(spain_ranking)
        
        # Co-producciones con España
        spain_coprods = year_df[(year_df['Spain'] == 1) & (year_df['num_countries'] > 1)].shape[0]
        metrics['spain_coprods'].append(spain_coprods)
    
    return pd.DataFrame(metrics)

def human_format(num):
    """Formatea números para mejor visualización"""
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def create_network_graph(df, selected_countries=None, highlight_country=None, min_weight=1):
    """Crea un gráfico de red para co-producciones"""
    # Obtener enlaces de co-producción
    source, target, weight = get_coproduction_links(df, 'countries_for_analysis')
    
    # Crear DataFrame con los enlaces
    links_df = pd.DataFrame({
        'source': source,
        'target': target,
        'weight': weight
    })
    
    # Filtrar por peso mínimo
    links_df = links_df[links_df['weight'] >= min_weight]
    
    # Filtrar por países seleccionados si se especifica
    if selected_countries:
        links_df = links_df[
            (links_df['source'].isin(selected_countries)) & 
            (links_df['target'].isin(selected_countries))
        ]
    
    # Crear lista de nodos únicos
    all_nodes = set(links_df['source'].tolist() + links_df['target'].tolist())
    
    # Contar películas por país
    country_counts = count_countries(df, 'countries_for_analysis')
    
    # Crear DataFrame de nodos
    nodes_df = pd.DataFrame({
        'id': list(all_nodes),
        'name': list(all_nodes),
        'size': [country_counts.get(country, 0) for country in all_nodes]
    })
    
    # Añadir colores a los nodos
    nodes_df['color'] = 'rgba(31, 119, 180, 0.8)'  # Color por defecto
    
    # Destacar país específico si se indica
    if highlight_country and highlight_country in nodes_df['id'].values:
        nodes_df.loc[nodes_df['id'] == highlight_country, 'color'] = 'rgba(214, 39, 40, 0.9)'  # Rojo para el país destacado
    
    # Crear gráfico de red con Plotly
    fig = go.Figure()
    
    # Crear grafo de NetworkX para el layout
    G = nx.Graph()
    
    # Añadir nodos
    for _, row in nodes_df.iterrows():
        G.add_node(row['id'], name=row['name'], size=row['size'])
    
    # Añadir enlaces con pesos
    for _, row in links_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    # Calcular posiciones con layout de NetworkX (Fruchterman-Reingold)
    pos = nx.spring_layout(G, k=0.4, iterations=50, seed=42)
    
    # Añadir enlaces (edges)
    for _, row in links_df.iterrows():
        source_pos = pos[row['source']]
        target_pos = pos[row['target']]
        
        # Escalar el grosor de la línea según el peso
        width = 1 + (row['weight'] / links_df['weight'].max() * 8)
        
        # Color especial si conecta con el país destacado
        if highlight_country and (row['source'] == highlight_country or row['target'] == highlight_country):
            edge_color = 'rgba(214, 39, 40, 0.5)'  # Rojo semi-transparente
        else:
            edge_color = 'rgba(180, 180, 180, 0.3)'
        
        fig.add_trace(
            go.Scatter(
                x=[source_pos[0], target_pos[0], None],
                y=[source_pos[1], target_pos[1], None],
                mode='lines',
                line=dict(width=width, color=edge_color),
                hoverinfo='none',
                showlegend=False
            )
        )
    
    # Añadir nodos
    for _, row in nodes_df.iterrows():
        node_pos = pos[row['id']]
        
        # Tamaño del nodo basado en número de películas, pero con límites
        size = 10 + (row['size'] / nodes_df['size'].max() * 30)
        
        # Texto para hover
        hover_text = f"{row['name']}<br>Películas: {row['size']}"
        
        # Añadir conexiones en hover si es el país destacado
        if highlight_country and row['id'] == highlight_country:
            connections = links_df[(links_df['source'] == row['id']) | (links_df['target'] == row['id'])]
            
            if not connections.empty:
                hover_text += "<br><br>Principales co-producciones:"
                
                # Encontrar los países relacionados
                related_countries = []
                for _, link in connections.iterrows():
                    if link['source'] == row['id']:
                        related_countries.append((link['target'], link['weight']))
                    else:
                        related_countries.append((link['source'], link['weight']))
                
                # Ordenar por frecuencia y mostrar los top 5
                related_countries.sort(key=lambda x: x[1], reverse=True)
                for country, count in related_countries[:5]:
                    hover_text += f"<br>• {country}: {count}"
        
        fig.add_trace(
            go.Scatter(
                x=[node_pos[0]],
                y=[node_pos[1]],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color=row['color'],
                    line=dict(width=1, color='#000000')
                ),
                text=row['name'],
                textposition="middle center" if row['size'] > nodes_df['size'].max() * 0.3 else "top center",
                textfont=dict(
                    size=8 if row['size'] <= nodes_df['size'].max() * 0.3 else 10,
                    color='black'
                ),
                hovertext=hover_text,
                hoverinfo='text',
                name=row['name'],
                showlegend=False
            )
        )
    
    # Configurar layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        title={
            'text': f"Red de Co-producciones {f'(foco en {highlight_country})' if highlight_country else ''}",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

# Cargar datos
@st.cache_data
def load_data():
    # Intentar cargar el archivo con datos expandidos, si no existe usar el anterior
    script_dir = os.path.dirname(os.path.abspath(__file__))
    expanded_file = os.path.join(script_dir, "datos_generados/cannes_con_paises_expandidos.xlsx")
    original_file = os.path.join(script_dir, "datos_generados/cannes_con_productoras_normalizadas.xlsx")
    
    if os.path.exists(expanded_file):
        file_path = expanded_file
        st.sidebar.success("✅ Usando datos expandidos con información adicional de países")
    else:
        file_path = original_file
        st.sidebar.warning("⚠️ Archivo de datos expandidos no encontrado. Usando datos originales.")
    
    # Cargar el DataFrame
    df = pd.read_excel(file_path)
    
    # Crear columna para usar en análisis (usar country_expanded si existe, sino usar country_esp_fra_usa)
    if 'country_expanded' in df.columns:
        df['countries_for_analysis'] = df['country_expanded']
    else:
        df['countries_for_analysis'] = df['country_esp_fra_usa']
    
    # Extraer año como entero
    df['year'] = df['year'].astype(int)
    
    # Generar columnas dummy para cada país
    unique_countries = set()
    for countries in df['countries_for_analysis'].dropna():
        unique_countries.update(get_countries_from_string(countries))
    
    # Crear columnas binarias para cada país
    for country in unique_countries:
        df[country] = df['countries_for_analysis'].apply(
            lambda x: 1 if pd.notna(x) and country in x else 0
        )
    
    # Contar películas por número de países involucrados
    df['num_countries'] = df['countries_for_analysis'].apply(
        lambda x: 0 if pd.isna(x) else len(get_countries_from_string(x))
    )
    
    return df, list(unique_countries)

# Cargar los datos
df, all_countries = load_data()

# Encabezado personalizado y mejorado
st.markdown('<div class="main-title">🎬 Festival de Cannes: Análisis Internacional</div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 0.5rem; margin-bottom: 1.5rem; font-style: italic;">
    Dashboard analítico de la participación internacional en el Festival de Cannes,
    con foco en la presencia española y las dinámicas de co-producción.
</div>
""", unsafe_allow_html=True)

# Barra lateral - Filtros con diseño mejorado
st.sidebar.markdown('<div class="subtitle">Filtros de Análisis</div>', unsafe_allow_html=True)

# Filtro de año con mejora visual
min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Rango de años:",
    min_year, max_year, 
    (max(min_year, max_year-10), max_year),  # Por defecto últimos 10 años
    help="Selecciona el período de años para analizar"
)

# Añadir presets rápidos para años
st.sidebar.markdown("##### Presets de periodos")
col1, col2, col3 = st.sidebar.columns(3)

if col1.button("Último año"):
    year_range = (max_year, max_year)
    st.experimental_rerun()
    
if col2.button("Última década"):
    year_range = (max(min_year, max_year-9), max_year)
    st.experimental_rerun()
    
if col3.button("Todo"):
    year_range = (min_year, max_year)
    st.experimental_rerun()

# Selección de países para análisis con colores para España
st.sidebar.markdown('<div style="margin-top: 1rem;">Países a incluir en análisis:</div>', unsafe_allow_html=True)

# Añadir países de referencia predefinidos
paises_referencia = ["Spain", "France", "Italy", "USA", "United Kingdom", "Germany"]

# Asegurar que España está seleccionada por defecto y destacada
col1, col2 = st.sidebar.columns(2)

with col1:
    spain_selected = st.checkbox("🇪🇸 España", value=True, 
                            help="España siempre debe estar seleccionada para este análisis")

with col2:
    france_selected = st.checkbox("🇫🇷 Francia", value=True)

col3, col4 = st.sidebar.columns(2)

with col3:
    italy_selected = st.checkbox("🇮🇹 Italia", value=True)

with col4:
    usa_selected = st.checkbox("🇺🇸 EE.UU.", value=True)

col5, col6 = st.sidebar.columns(2)

with col5:
    uk_selected = st.checkbox("🇬🇧 Reino Unido", value=True)

with col6:
    germany_selected = st.checkbox("🇩🇪 Alemania", value=True)

# Construir lista de países seleccionados
selected_countries = []
if spain_selected:
    selected_countries.append("Spain")
if france_selected:
    selected_countries.