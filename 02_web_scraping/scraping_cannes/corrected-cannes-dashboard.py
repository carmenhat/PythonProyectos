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
import base64

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
def hex_to_rgb(hex_color):
    """
    Convierte un color hexadecimal a RGB
    
    Args:
        hex_color (str): Color en formato hexadecimal (#RRGGBB)
        
    Returns:
        tuple: Tupla con valores RGB (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def create_choropleth_map(df, year_range=None):
    """
    Crea un mapa coroplético mundial con el número de películas por país
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        year_range (tuple): Rango de años para filtrar (opcional)
        
    Returns:
        Figure: Figura de Plotly con el mapa coroplético
    """
    # Filtrar por rango de años si se especifica
    if year_range:
        filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    else:
        filtered_df = df
    
    # Contar películas por país
    country_counts = {}
    for _, row in filtered_df.iterrows():
        if pd.isna(row['countries_for_analysis']):
            continue
        
        countries = get_countries_from_string(row['countries_for_analysis'])
        for country in countries:
            country_counts[country] = country_counts.get(country, 0) + 1
    
    # Convertir a DataFrame para Plotly
    country_data = pd.DataFrame({
        'country': list(country_counts.keys()),
        'count': list(country_counts.values())
    })
    
    # Mapeo de países a códigos ISO-3 para el mapa
    # Añadir mapeo para países comunes en el dataset
    country_to_iso = {
        'Spain': 'ESP',
        'France': 'FRA',
        'Italy': 'ITA',
        'USA': 'USA',
        'United Kingdom': 'GBR',
        'Germany': 'DEU',
        'Japan': 'JPN',
        'Canada': 'CAN',
        'Mexico': 'MEX',
        'Brazil': 'BRA',
        'China': 'CHN',
        'Russia': 'RUS',
        'Australia': 'AUS',
        'India': 'IND',
        'Sweden': 'SWE',
        'Denmark': 'DNK',
        'Belgium': 'BEL',
        'Netherlands': 'NLD',
        'Switzerland': 'CHE',
        'Austria': 'AUT',
        'Poland': 'POL',
        'Ireland': 'IRL',
        'Greece': 'GRC',
        'Portugal': 'PRT',
        'Argentina': 'ARG',
        'Chile': 'CHL',
        'Colombia': 'COL',
        'South Korea': 'KOR',
        'Korea, South': 'KOR'  # Variante de nombre
    }
    
    # Añadir códigos ISO al DataFrame
    country_data['iso_alpha'] = country_data['country'].map(country_to_iso)
    
    # Eliminar países sin código ISO (evitar errores en el mapa)
    country_data = country_data.dropna(subset=['iso_alpha'])
    
    # Escala de color con énfasis en España
    colorscale = [
        [0, 'rgba(220, 220, 220, 0.8)'],          # Gris claro para países sin películas
        [0.2, 'rgba(102, 137, 255, 0.8)'],        # Azul claro
        [0.4, 'rgba(51, 102, 255, 0.8)'],         # Azul medio
        [0.6, 'rgba(0, 51, 153, 0.8)'],          # Azul oscuro
        [0.8, 'rgba(204, 0, 0, 0.8)'],           # Rojo claro
        [1.0, 'rgba(255, 204, 0, 0.8)']          # Amarillo España para máximo
    ]
    
    # Crear el mapa coroplético
    fig = go.Figure(data=go.Choropleth(
        locations=country_data['iso_alpha'],
        z=country_data['count'],
        text=country_data['country'],
        colorscale=colorscale,
        autocolorscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title='Número de<br>películas',
        colorbar=dict(
            thickness=15,
            len=0.7,
            x=0.9,
            y=0.7,
            outlinewidth=0
        ),
        hovertemplate='<b>%{text}</b><br>Películas: %{z}<extra></extra>'
    ))
    
    # Configurar el layout
    year_text = f"{year_range[0]}-{year_range[1]}" if year_range else "todos los años disponibles"
    fig.update_layout(
        title_text=f'Distribución mundial de películas en Cannes ({year_text})',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            landcolor='rgb(240, 240, 240)',
            coastlinecolor='rgba(200, 200, 200, 0.8)',
            countrycolor='rgba(200, 200, 200, 0.8)'
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        height=550
    )
    
    # Destacar España
    fig.add_trace(go.Choropleth(
        locations=['ESP'],
        z=[1],  # Valor ficticio, solo para destacar
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, '#FFCC00']],  # Transparente a amarillo España
        showscale=False,
        marker_line_color='black',
        marker_line_width=1.5,
        hoverinfo='skip'
    ))
    
    return fig
def generate_automatic_insights(df, year_range=None):
    """
    Genera insights automáticos sobre el dataset, con énfasis en España
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        year_range (tuple): Rango de años para filtrar (opcional)
        
    Returns:
        list: Lista de diccionarios con insights generados
    """
    insights = []
    
    # Filtrar por rango de años si se especifica
    if year_range:
        filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    else:
        filtered_df = df
        
    # Si no hay datos, devolver mensaje informativo
    if filtered_df.empty:
        return [{"title": "Sin datos", "description": "No hay datos disponibles para el rango seleccionado", "type": "warning"}]
    
    # --- Insights sobre España ---
    
    # 1. Tendencia de participación española
    spain_yearly = filtered_df.groupby('year')['Spain'].sum().reset_index()
    if len(spain_yearly) > 1:
        # Calcular pendiente de la tendencia
        x = spain_yearly['year'].values
        y = spain_yearly['Spain'].values
        if len(x) >= 2:  # Necesitamos al menos 2 puntos para la pendiente
            slope = np.polyfit(x, y, 1)[0]
            trend_text = "creciente" if slope > 0.1 else "decreciente" if slope < -0.1 else "estable"
            
            insights.append({
                "title": "Tendencia de participación española",
                "description": f"La presencia de España en Cannes muestra una tendencia {trend_text} en el período analizado.",
                "value": f"{slope:.2f} películas/año",
                "type": "trend",
                "highlight": True if abs(slope) > 0.2 else False
            })
    
    # 2. Comparativa con año anterior (si hay datos suficientes)
    years = sorted(filtered_df['year'].unique())
    if len(years) >= 2:
        last_year = years[-1]
        prev_year = years[-2]
        
        last_year_count = filtered_df[filtered_df['year'] == last_year]['Spain'].sum()
        prev_year_count = filtered_df[filtered_df['year'] == prev_year]['Spain'].sum()
        
        if prev_year_count > 0:
            percent_change = ((last_year_count - prev_year_count) / prev_year_count) * 100
            direction = "más" if percent_change > 0 else "menos"
            insights.append({
                "title": f"Comparativa {last_year} vs {prev_year}",
                "description": f"España tuvo {abs(percent_change):.1f}% {direction} películas en {last_year} comparado con {prev_year}.",
                "value": f"{last_year_count} vs {prev_year_count}",
                "type": "comparison",
                "highlight": True if abs(percent_change) > 20 else False
            })
    
    # 3. Posición en el ranking de países
    country_counts = count_countries(filtered_df, 'countries_for_analysis')
    country_ranking = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    spain_position = 999  # Valor predeterminado alto
    for i, (country, count) in enumerate(country_ranking):
        if country == 'Spain':
            spain_position = i + 1
            break
    
    if spain_position < 999:  # Si encontramos a España
        # Formatear texto según la posición
        if spain_position <= 3:
            position_text = f"top {spain_position}"
            highlight = True
        else:
            position_text = f"posición {spain_position}"
            highlight = False
            
        insights.append({
            "title": "Ranking de países",
            "description": f"España ocupa el {position_text} en número de películas en Cannes durante este período.",
            "value": f"#{spain_position}",
            "type": "ranking",
            "highlight": highlight
        })
    
    # 4. Co-producciones con España
    spain_movies = filtered_df[filtered_df['Spain'] == 1]
    total_spain = len(spain_movies)
    coprods_spain = spain_movies[spain_movies['num_countries'] > 1].shape[0]
    
    if total_spain > 0:
        coprod_percentage = (coprods_spain / total_spain) * 100
        insights.append({
            "title": "Co-producciones españolas",
            "description": f"El {coprod_percentage:.1f}% de las películas españolas son co-producciones internacionales.",
            "value": f"{coprods_spain}/{total_spain}",
            "type": "coproduction",
            "highlight": True if coprod_percentage > 50 else False
        })
        
        # 5. Principales países co-productores con España
        if coprods_spain > 0:
            top_coprods = get_top_coprod_countries_with_spain(filtered_df)
            if top_coprods:
                top_country, top_count = top_coprods[0]
                insights.append({
                    "title": "Principal socio de co-producción",
                    "description": f"{top_country} es el principal socio de co-producción de España con {top_count} películas conjuntas.",
                    "value": f"{top_country} ({top_count})",
                    "type": "partner",
                    "highlight": True if top_count > 3 else False
                })
    
    # 6. Año con más películas españolas
    if len(spain_yearly) > 2:
        max_year = spain_yearly.loc[spain_yearly['Spain'].idxmax()]
        insights.append({
            "title": "Año más productivo",
            "description": f"{max_year['year']} fue el año con mayor presencia española en Cannes con {int(max_year['Spain'])} películas.",
            "value": f"{int(max_year['Spain'])} en {max_year['year']}",
            "type": "peak",
            "highlight": True if max_year['Spain'] > spain_yearly['Spain'].mean() * 1.5 else False
        })
    
    # 7. Análisis de secciones (si está disponible en los datos)
    if 'section' in filtered_df.columns and not filtered_df['section'].isna().all():
        spain_sections = filtered_df[filtered_df['Spain'] == 1]['section'].value_counts()
        if not spain_sections.empty:
            main_section = spain_sections.index[0]
            main_section_count = spain_sections.iloc[0]
            insights.append({
                "title": "Sección principal",
                "description": f"La mayoría de películas españolas participaron en la sección '{main_section}' ({main_section_count} películas).",
                "value": main_section,
                "type": "section",
                "highlight": False
            })
    
    # --- Insights generales del festival ---
    
    # 8. Diversidad de países
    unique_countries = len(country_ranking)
    avg_countries_per_film = filtered_df['num_countries'].mean()
    
    insights.append({
        "title": "Diversidad internacional",
        "description": f"Cannes contó con películas de {unique_countries} países diferentes, con un promedio de {avg_countries_per_film:.1f} países por película.",
        "value": f"{unique_countries} países",
        "type": "diversity",
        "highlight": True if unique_countries > 50 else False
    })
    
    # 9. País dominante
    if country_ranking:
        top_country, top_count = country_ranking[0]
        total_films = len(filtered_df)
        top_percentage = (top_count / total_films) * 100
        
        insights.append({
            "title": "País dominante",
            "description": f"{top_country} lidera la participación en Cannes con {top_count} películas ({top_percentage:.1f}% del total).",
            "value": top_country,
            "type": "dominance",
            "highlight": True if top_percentage > 30 else False
        })
    
    # 10. Tendencia de co-producciones
    yearly_coprods = filtered_df.groupby('year').apply(lambda x: (x['num_countries'] > 1).sum() / len(x) * 100 if len(x) > 0 else 0)
    if len(yearly_coprods) > 1:
        first_year_coprod = yearly_coprods.iloc[0]
        last_year_coprod = yearly_coprods.iloc[-1]
        
        coprod_change = last_year_coprod - first_year_coprod
        direction = "aumento" if coprod_change > 0 else "descenso"
        
        insights.append({
            "title": "Evolución de co-producciones",
            "description": f"Hay un {direction} de {abs(coprod_change):.1f}% en co-producciones internacionales desde {years[0]} hasta {years[-1]}.",
            "value": f"{coprod_change:.1f}%",
            "type": "trend",
            "highlight": True if abs(coprod_change) > 15 else False
        })
    
    return insights

if not explorer_df.empty:

    st.markdown(get_table_download_link(explorer_df), unsafe_allow_html=True)
### me falta acabar esta función
def create_network_graph(df, selected_countries=None, highlight_country=None, min_weight=1):
    """
    Crea un gráfico de red de co-producciones entre países.

    Args:
        df (DataFrame): DataFrame con datos de películas.
        selected_countries (list, optional): Lista de países para incluir en el gráfico. Defaults to None.
        highlight_country (str, optional): País para resaltar en el gráfico. Defaults to None.
        min_weight (int, optional): Peso mínimo para mostrar una conexión. Defaults to 1.

    Returns:
        plotly.graph_objects.Figure: Objeto Figure de Plotly con el gráfico de red.
    """
    # 1. Preparar los datos de los enlaces (co-producciones)
    source, target, weight = get_coproduction_links(df, 'countries_for_analysis')
    links_df = pd.DataFrame({'source': source, 'target': target, 'weight': weight})
    # Filtrar por peso mínimo
    links_df = links_df[links_df['weight'] >= min_weight]

    # 2. Crear un DataFrame de nodos (países)
    all_countries = list(set(links_df['source'].unique()).union(set(links_df['target'].unique())))
    nodes_df = pd.DataFrame({'id': list(all_countries)})
    # Asignar nombres y colores basados en COUNTRY_MAPPING (si está definido)
    nodes_df['name'] = nodes_df['id'].map(lambda x: COUNTRY_MAPPING.get(x, {}).get('name', x))
    nodes_df['color'] = nodes_df['id'].map(lambda x: COUNTRY_MAPPING.get(x, {}).get('color', '#CCCCCC'))  # Gris por defecto

    # 3. Calcular el tamaño de los nodos basado en la cantidad de conexiones
    node_degree = pd.concat([links_df['source'], links_df['target']]).value_counts()
    nodes_df['size'] = nodes_df['id'].map(node_degree).fillna(0)  # Usar fillna(0) para países sin conexiones
    # Escalar el tamaño para mejor visualización
    max_size = 50  # Tamaño máximo del nodo
    nodes_df['size'] = nodes_df['size'] / nodes_df['size'].max() * max_size

    # 4. Crear el grafo de NetworkX
    G = nx.Graph()
    for i, row in nodes_df.iterrows():
        G.add_node(row['id'], name=row['name'], color=row['color'], size=row['size'])
    for i, row in links_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])

    # 5. Calcular el layout del grafo (posición de los nodos)
    pos = nx.spring_layout(G, k=0.5, seed=42)  # Usar un seed para reproducibilidad
    for node in G.nodes():
        G.nodes[node]['pos'] = pos[node]

    # 6. Crear trazas para los enlaces y nodos
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_trace = go.Scatter(
        x=[],
        y=[],
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=[],
            line=dict(width=0)
        )
    )

    # 7. Llenar las trazas con los datos del grafo
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['marker']['color'].append(G.nodes[node]['color'])
        node_trace['marker']['size'].append(G.nodes[node]['size'])

    # 8. Personalizar el hovertext para mostrar información relevante
    node_adjacencies = []
    node_text = []
    for node in G.nodes():
        adjacencies = list(G.adj[node])
        node_adjacencies.append(len(adjacencies))
        node_text.append(f"País: {node}\n# de conexiones: {len(adjacencies)}")
    node_trace['text'] = node_text

    # 9. Crear el layout de Plotly
    layout = go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    # 10. Crear la figura y añadir las trazas
    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig
# Interfaz principal del dashboard (sin acabar)

def main():
    try:
    
        df = load_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
        return  # Salir de la función       
        # Verificar si los datos se cargaron correctamente
        if df.empty:
            st.stop()
        
        # Calcular rango de años disponibles
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        # Sidebar para controles
        st.sidebar.header("Filtros y Controles")
        # Añadir un selector de tema
with st.sidebar:
    st.write("## Configuración del dashboard")
    theme = st.selectbox(
        "Tema de color",
        options=["Estándar", "Alto contraste", "Modo oscuro"],
        index=0
    )
    
    # Lógica para aplicar el tema seleccionado
    if theme == "Alto contraste":
        st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
        }
        h1, h2, h3 {
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "Modo oscuro":
        st.markdown("""
        <style>
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        h1, h2, h3 {
            color: #FFFFFF !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Selector de rango de años
        year_range = st.sidebar.slider(
            "Rango de años",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1
        )
        
        # Filtro de países
        countries_to_show = st.sidebar.multiselect(
            "Países a destacar",
            options=['Spain', 'France', 'Italy', 'USA', 'United Kingdom', 'Germany'],
            default=['Spain', 'France']
        )
        
        # Filtrar por rango de años seleccionado
        filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
        # Mostrar información general del período seleccionado
        st.markdown(f"## Resumen del período {year_range[0]}-{year_range[1]}")
        
        # KPIs en la parte superior
        kpi_cols = st.columns(4)
        
        # Total de películas
        total_films = len(filtered_df)
        kpi_cols[0].metric(
            "Total de películas",
            f"{total_films}",
            None
        )
        
        # Países participantes
        unique_countries = set()
        for countries in filtered_df['countries_for_analysis'].dropna():
            unique_countries.update(get_countries_from_string(countries))
        num_countries = len(unique_countries)
        kpi_cols[1].metric(
            "Países participantes",
            f"{num_countries}",
            None
        )
        
        # % Co-producciones
        coprods = filtered_df[filtered_df['num_countries'] > 1].shape[0]
        coprod_pct = (coprods / total_films) * 100 if total_films > 0 else 0
        kpi_cols[2].metric(
            "Co-producciones",
            f"{coprods} ({coprod_pct:.1f}%)",
            None
        )
        
        # Participación española
        spain_films = filtered_df[filtered_df['Spain'] == 1].shape[0]
        spain_pct = (spain_films / total_films) * 100 if total_films > 0 else 0
        kpi_cols[3].metric(
            "Películas españolas",
            f"{spain_films} ({spain_pct:.1f}%)",
            None
        )
        # Sección: Evolución temporal
        st.markdown("## Evolución temporal")
        
        # Pestaña para visualizaciones temporales
        time_tabs = st.tabs(["Películas por año", "Ranking de países", "Tendencias españolas"])
        
        with time_tabs[0]:
            st.markdown("### Películas por año y país")
            
            # Generar datos para cada país seleccionado
            yearly_country_data = pd.DataFrame({
                'year': [],
                'country': [],
                'count': []
            })
            
            for country in countries_to_show:
                country_yearly = filtered_df.groupby('year')[country].sum().reset_index()
                country_yearly['country'] = country
                country_yearly = country_yearly.rename(columns={country: 'count'})
                yearly_country_data = pd.concat([yearly_country_data, country_yearly])
            
            # Gráfico de líneas de evolución temporal
            fig_time = px.line(
                yearly_country_data,
                x='year',
                y='count',
                color='country',
                title='Evolución de películas por país y año',
                labels={'count': 'Número de películas', 'year': 'Año'},
                color_discrete_map={
                    country: COUNTRY_MAPPING.get(country, {}).get('color', '#BBBBBB') 
                    for country in countries_to_show
                }
            )
            
            fig_time.update_layout(
                xaxis=dict(tickmode='linear', dtick=5),
                legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
                height=450
            )
            
            st.plotly_chart(fig_time, use_container_width=True)
        # Sección: Análisis geográfico
        st.markdown("## Análisis geográfico")
        
        geo_tabs = st.tabs(["Mapa mundial", "Red de co-producciones"])
        
        with geo_tabs[0]:
            st.markdown("### Distribución mundial de películas")
            
            # Crear mapa coroplético
            fig_map = create_choropleth_map(filtered_df, year_range)
            
            st.plotly_chart(fig_map, use_container_width=True)
        
        with geo_tabs[1]:
            st.markdown("### Red de co-producciones internacionales")
            
            # Controles para la red
            col1, col2 = st.columns([2, 3])
            
            min_weight = col1.slider(
                "Mínimo de co-producciones para mostrar conexión",
                min_value=1,
                max_value=10,
                value=2
            )
            
            highlight_country = col1.selectbox(
                "País a destacar",
                options=['Ninguno'] + countries_to_show,
                index=0
            )
            
            if highlight_country == 'Ninguno':
                highlight_country = None
            
            # Obtener datos para la red
            source, target, weight = get_coproduction_links(filtered_df, 'countries_for_analysis')
            
            # Crear DataFrame con los enlaces
            links_df = pd.DataFrame({
                'source': source,
                'target': target,
                'weight': weight
            })
            
            # Filtrar por peso mínimo
            links_df = links_df[links_df['weight'] >= min_weight]
            if not links_df.empty:
                # Crear grafo
                G = nx.Graph()
                
                # Añadir nodos y enlaces
                for _, row in links_df.iterrows():
                    G.add_edge(row['source'], row['target'], weight=row['weight'])
                
                # Obtener países únicos (nodos)
                countries = set(links_df['source'].unique()) | set(links_df['target'].unique())
                
                # Calcular tamaño de nodos basado en grado
                node_sizes = {}
                for country in countries:
                    movies_count = filtered_df[filtered_df['countries_for_analysis'].apply(
                        lambda x: pd.notna(x) and country in get_countries_from_string(x)
                    )].shape[0]
                    node_sizes[country] = max(20, min(100, movies_count * 2))
                
                # Crear DataFrame para nodos
                nodes_df = pd.DataFrame({
                    'id': list(countries),
                    'name': [COUNTRY_MAPPING.get(c, {}).get('name', c) for c in countries],
                    'size': [node_sizes.get(c, 30) for c in countries],
                    'color': [COUNTRY_MAPPING.get(c, {}).get('color', '#BBBBBB') for c in countries]
                })
                
                # Calcular posiciones con layout de Fruchterman-Reingold
                pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
                
                # Crear gráfico de red
                fig_network = go.Figure()
                
                # Añadir enlaces
                for _, row in links_df.iterrows():
                    source_pos = pos[row['source']]
                    target_pos = pos[row['target']]
                    
                    # Determinar grosor basado en peso
                    width = max(1, min(10, row['weight'] / 2))
                    
                    # Determinar color
                    if highlight_country and (row['source'] == highlight_country or row['target'] == highlight_country):
                        line_color = COUNTRY_MAPPING.get(highlight_country, {}).get('color', '#FF0000')
                        opacity = 0.8
                    else:
                        line_color = '#CCCCCC'
                        opacity = 0.3 if highlight_country else 0.6
                    
                    # Añadir línea
                    fig_network.add_trace(
                        go.Scatter(
                            x=[source_pos[0], target_pos[0], None],
                            y=[source_pos[1], target_pos[1], None],
                            mode='lines',
                            line=dict(width=width, color=line_color, opacity=opacity),
                            hoverinfo='text',
                            hovertext=f"{row['source']} - {row['target']}: {row['weight']} co-producciones",
                            showlegend=False
                        )
                    )
                # Añadir nodos
                for _, row in nodes_df.iterrows():
                    node_pos = pos[row['id']]
                    size = row['size']
                    
                    # Resaltar nodo si es el país seleccionado
                    if highlight_country and row['id'] == highlight_country:
                        size *= 1.5
                    
                    # Texto para hover
                    hover_text = f"**{row['name']}**<br>Películas: {row['size']}"
                    
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
                    
                    fig_network.add_trace(
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
                            hoverinfo='text',
                            hovertext=hover_text,
                            showlegend=False
                        )
                    )
                
                # Configurar layout
                fig_network.update_layout(
                    title='Red de co-producciones internacionales',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=20, r=20, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600
                )
                    
                
                
                col2.plotly_chart(fig_network, use_container_width=True)
            else:
                col2.warning("No hay suficientes co-producciones para crear la red con los filtros actuales")
        # Sección: Explorador de películas
        st.markdown("## Explorador de películas")
        
        # Filtros para explorar películas
        explorer_cols = st.columns([1, 1, 2])
        
        country_filter = explorer_cols[0].multiselect(
            "Filtrar por país",
            options=list(COUNTRY_MAPPING.keys()),
            default=["Spain"]
        )
        
        year_filter = explorer_cols[1].slider(
            "Año",
            min_value=min_year,
            max_value=max_year,
            value=(year_range[0], year_range[1])
        )
        
        search_term = explorer_cols[2].text_input("Buscar por título", "")
        
        # Aplicar filtros
        explorer_df = df.copy()
        
        # Filtro de país
        if country_filter:
            country_mask = pd.Series(False, index=explorer_df.index)
            for country in country_filter:
                country_mask = country_mask | (explorer_df[country] == 1)
            explorer_df = explorer_df[country_mask]
        
        # Filtro de año
        explorer_df = explorer_df[(explorer_df['year'] >= year_filter[0]) & (explorer_df['year'] <= year_filter[1])]
        
        # Filtro de texto
        if search_term:
            explorer_df = explorer_df[explorer_df['title'].str.contains(search_term, case=False, na=False)]
        
        # Mostrar resultados
        if not explorer_df.empty:
            st.markdown(f"### Resultados ({len(explorer_df)} películas)")
            
            # Mostrar tabla con películas
            st.dataframe(
                explorer_df[['year', 'title', 'director', 'countries_for_analysis']].sort_values('year', ascending=False),
                column_config={
                    "year": st.column_config.NumberColumn("Año"),
                    "title": st.column_config.TextColumn("Título"),
                    "director": st.column_config.TextColumn("Director"),
                    "countries_for_analysis": st.column_config.TextColumn("Países")
                },
                use_container_width=True
            )
            
            # Si hay demasiadas películas, mostrar advertencia
            if len(explorer_df) > 100:
                st.warning("Se muestran demasiados resultados. Utilice los filtros para refinar la búsqueda.")
        else:
            st.info("No se encontraron películas con los filtros seleccionados")
        
        # Pie de página
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #888;">
            Dashboard creado para análisis de la presencia internacional en el Festival de Cannes.
            Datos actualizados hasta 2022.
            </div>
            """,
            unsafe_allow_html=True
        )
            
    except Exception as e:
        st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
        logger.error(f"Error en la aplicación: {str(e)}", exc_info=True)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()

    


# Implementar caching para funciones pesadas que no cambian frecuentemente
@st.cache_data(ttl=3600)  # Cache durante 1 hora
def get_coproduction_network_data(df, min_weight=1):
    """Genera datos para la red de co-producciones con cache"""
    source, target, weight = get_coproduction_links(df, 'countries_for_analysis')
    
    # Filtrar por peso mínimo
    filtered_source = []
    filtered_target = []
    filtered_weight = []
    
    for s, t, w in zip(source, target, weight):
        if w >= min_weight:
            filtered_source.append(s)
            filtered_target.append(t)
            filtered_weight.append(w)
    
    return filtered_source, filtered_target, filtered_weight

# Botón para descargar datos filtrados
def get_table_download_link(df, filename="datos_filtrados.csv"):
    """Genera un enlace de descarga para un DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar datos CSV</a>'
    return href


