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
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Definir constantes para mayor mantenibilidad
COLOR_PRIMARY = "#E50914"  # Rojo Netflix
COLOR_SECONDARY = "#FFCC00"  # Amarillo España
COLOR_BACKGROUND = "#f8f9fa"  # Gris claro para fondos

# Definir mapeo de países para mantener consistencia
COUNTRY_MAPPING = {
    "Spain": {"name": "España", "emoji": "🇪🇸", "color": "#FFCC00", "badge_class": "badge-spain"},
    "France": {"name": "Francia", "emoji": "🇫🇷", "color": "#002654", "badge_class": "badge-france"},
    "Italy": {"name": "Italia", "emoji": "🇮🇹", "color": "#008C45", "badge_class": "badge-italy"},
    "USA": {"name": "EE.UU.", "emoji": "🇺🇸", "color": "#3C3B6E", "badge_class": "badge-usa"},
    "United Kingdom": {"name": "Reino Unido", "emoji": "🇬🇧", "color": "#00247D"},
    "Germany": {"name": "Alemania", "emoji": "🇩🇪", "color": "#FFCC00"}
}

# Funciones auxiliares
def extract_flag_emoji(country_text):
    """
    Extrae el emoji de bandera de un texto de país
    
    Args:
        country_text (str): Texto que puede contener emoji de bandera
    
    Returns:
        str: Emoji de bandera encontrado o cadena vacía
    """
    if pd.isna(country_text):
        return ""
    match = re.search(r'(\p{So}\p{So})', country_text, re.UNICODE)
    return match.group(1) if match else ""

def get_countries_from_string(country_string):
    """
    Divide una cadena de países en una lista
    
    Args:
        country_string (str): String con países separados por comas
        
    Returns:
        list: Lista de países individuales
    """
    if pd.isna(country_string) or country_string == "":
        return []
    return [c.strip() for c in country_string.split(',')]

def count_countries(df, country_column):
    """
    Cuenta la frecuencia de cada país en el DataFrame
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        country_column (str): Nombre de la columna con países
        
    Returns:
        Counter: Contador con frecuencia de cada país
    """
    all_countries = []
    for countries in df[country_column].dropna():
        all_countries.extend(get_countries_from_string(countries))
    return Counter(all_countries)

def get_coproduction_links(df, country_column):
    """
    Genera enlaces para gráfico de red de co-producciones
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        country_column (str): Nombre de la columna con países
        
    Returns:
        tuple: Listas de origen, destino y peso para cada enlace
    """
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
    """
    Calcula KPIs específicos para España
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        year_range (tuple): Rango de años (min, max)
        
    Returns:
        dict: Diccionario con KPIs calculados
    """
    results = {}
    
    # Filtrar por rango de años
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    # Total de películas españolas en el rango
    total_spain = filtered_df[filtered_df['Spain'] == 1].shape[0]
    results['total'] = total_spain
    
    # Porcentaje respecto al total
    total_movies = filtered_df.shape[0]
    results['percentage'] = (total_spain / total_movies) * 100 if total_movies > 0 else 0
    
    # Posición en el ranking de países
    country_counts = count_countries(filtered_df, 'countries_for_analysis')
    country_ranking = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    spain_position = -1
    for i, (country, _) in enumerate(country_ranking):
        if country == 'Spain':
            spain_position = i + 1
            break
    results['ranking'] = spain_position
    
    # Co-producciones con España
    spain_movies = filtered_df[filtered_df['Spain'] == 1]
    coprods_spain = spain_movies[spain_movies['num_countries'] > 1].shape[0]
    results['coproductions'] = coprods_spain
    results['coprod_percentage'] = (coprods_spain / total_spain) * 100 if total_spain > 0 else 0
    
    # Tendencia (comparando con periodo anterior si hay datos suficientes)
    if year_range[1] - year_range[0] >= 5:
        # Dividir el rango en dos periodos
        mid_year = (year_range[0] + year_range[1]) // 2
        first_period = filtered_df[(filtered_df['year'] >= year_range[0]) & (filtered_df['year'] <= mid_year)]
        second_period = filtered_df[(filtered_df['year'] > mid_year) & (filtered_df['year'] <= year_range[1])]
        
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
    if year_range[1] > year_range[0]:
        years_diff = year_range[1] - year_range[0]
        
        # Películas en el primer y último año
        start_year_films = filtered_df[filtered_df['year'] == year_range[0]][filtered_df['Spain'] == 1].shape[0]
        end_year_films = filtered_df[filtered_df['year'] == year_range[1]][filtered_df['Spain'] == 1].shape[0]
        
        # Evitar división por cero
        if start_year_films > 0 and years_diff > 0:
            cagr = ((end_year_films / start_year_films) ** (1 / years_diff) - 1) * 100
            results['cagr'] = cagr
        else:
            results['cagr'] = 0
    else:
        results['cagr'] = 0
    
    # Métrica de consistencia (desviación estándar de participación)
    yearly_spain = filtered_df.groupby('year')['Spain'].sum()
    results['consistency'] = yearly_spain.std() if len(yearly_spain) > 1 else 0
    
    return results

def get_top_coprod_countries_with_spain(df):
    """
    Obtiene los principales países co-productores con España
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        
    Returns:
        list: Lista de tuplas (país, frecuencia) ordenadas por frecuencia
    """
    spain_movies = df[df['Spain'] == 1]
    
    # Extraer países co-productores con España
    coprod_countries = []
    for countries in spain_movies['countries_for_analysis'].dropna():
        country_list = get_countries_from_string(countries)
        # Solo añadir países que no sean España
        coprod_countries.extend([c for c in country_list if c != 'Spain'])
    
    return Counter(coprod_countries).most_common(10)  # Ampliado a 10 para el mapa de calor

def generate_coproduction_heatmap_data(df, focus_country="Spain"):
    """
    Genera datos para el mapa de calor de co-producciones
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        focus_country (str): País en el que enfocar el análisis
        
    Returns:
        tuple: Array numpy para el mapa de calor y lista de países
    """
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

@st.cache_data
def calculate_yearly_rankings(df, countries):
    """
    Calcula el ranking de países por año
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        countries (list): Lista de países para incluir en el ranking
        
    Returns:
        dict: Diccionario con rankings por año
    """
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
    """
    Obtiene métricas anuales para España
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        countries (list): Lista de países para comparar
        
    Returns:
        DataFrame: DataFrame con métricas anuales
    """
    years = sorted(df['year'].unique())
    metrics = {
        'year': years,
        'total_films': [],
        'spain_films': [],
        'spain_percentage': [],
        'spain_ranking': [],
        'spain_coprods': []
    }
    
    # Rankings anuales (cacheado para mejor rendimiento)
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
    """
    Formatea números para mejor visualización
    
    Args:
        num (float): Número a formatear
        
    Returns:
        str: Número formateado
    """
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def create_network_graph(df, selected_countries=None, highlight_country=None, min_weight=1):
    """
    Crea un gráfico de red para co-producciones
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        selected_countries (list): Lista de países a incluir (opcional)
        highlight_country (str): País a destacar (opcional)
        min_weight (int): Peso mínimo para mostrar un enlace
        
    Returns:
        Figure: Objeto de figura de Plotly
    """
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
    
    # Si no hay enlaces después de filtrar, devolver gráfico vacío con mensaje
    if links_df.empty:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text="No hay suficientes co-producciones con el peso mínimo seleccionado",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )],
            height=600
        )
        return fig
    
    # Filtrar por países seleccionados si se especifica
    if selected_countries:
        links_df = links_df[
            (links_df['source'].isin(selected_countries)) & 
            (links_df['target'].isin(selected_countries))
        ]
        
        # Verificar si quedaron enlaces después de filtrar
        if links_df.empty:
            fig = go.Figure()
            fig.update_layout(
                annotations=[dict(
                    text="No hay co-producciones entre los países seleccionados",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )],
                height=600
            )
            return fig
    
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
    
    # Añadir colores a los nodos utilizando el mapeo
    nodes_df['color'] = 'rgba(31, 119, 180, 0.8)'  # Color por defecto
    for country, details in COUNTRY_MAPPING.items():
        if country in nodes_df['id'].values:
            nodes_df.loc[nodes_df['id'] == country, 'color'] = f"rgba({','.join(str(int(c)) for c in hex_to_rgb(details['color']))}, 0.8)"
    
    # Destacar país específico si se indica
    if highlight_country and highlight_country in nodes_df['id'].values:
        nodes_df.loc[nodes_df['id'] == highlight_country, 'color'] = 'rgba(214, 39, 40, 0.9)'  # Rojo para el país destacado
    
    try:
        # Crear grafo de NetworkX para el layout
        G = nx.Graph()
        
        # Añadir nodos
        for _, row in nodes_df.iterrows():
            G.add_node(row['id'], name=row['name'], size=row['size'])
        
        # Añadir enlaces con pesos
        for _, row in links_df.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['weight'])
        
        # Calcular posiciones con layout de NetworkX (Fruchterman-Reingold)
        # Usar k más pequeño para grafos grandes
        k_value = 0.4 if len(G.nodes) < 50 else 0.2
        pos = nx.spring_layout(G, k=k_value, iterations=50, seed=42)
        
        # Crear gráfico de red con Plotly
        fig = go.Figure()
        
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