import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from .data_processing import get_countries_from_string, get_coproduction_matrix, get_country_production_companies
import pycountry

def create_country_evolution_chart(df, countries):
    """Crea un gráfico de líneas para la evolución de países a lo largo del tiempo"""
    if not countries:
        return go.Figure()
    
    # Preparar datos para evolución temporal
    df_line = df.groupby("year")[countries].sum().reset_index()
    
    fig = px.line(
        df_line, x="year", y=countries,
        markers=True, 
        title="Evolución de películas por país"
    )
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Número de películas",
        legend_title="País",
        height=400
    )
    
    return fig

def create_country_proportion_chart(df, countries):
    """Crea un gráfico de área para la proporción de países a lo largo del tiempo"""
    if not countries:
        return go.Figure()
    
    # Preparar datos para el gráfico de proporción
    df_line = df.groupby("year")[countries].sum().reset_index()
    
    # Calcular porcentajes
    df_percent = df_line.copy()
    row_sums = df_percent[countries].sum(axis=1)
    for country in countries:
        df_percent[country] = df_percent[country] / row_sums * 100
    
    df_melted = df_percent.melt(
        id_vars="year", 
        value_vars=countries,
        var_name="País", 
        value_name="Porcentaje"
    )
    
    fig = px.area(
        df_melted, 
        x="year", 
        y="Porcentaje", 
        color="País",
        title="Proporción anual por país", 
        groupnorm="percent"
    )
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Porcentaje",
        legend_title="País",
        height=400
    )
    
    return fig

def create_coproduction_distribution_chart(df):
    """Crea un gráfico de barras para la distribución de co-producciones"""
    # Contar películas por número de países involucrados
    coprod_counts = df['num_countries'].value_counts().sort_index()
    coprod_df = pd.DataFrame({
        'Número de países': coprod_counts.index,
        'Películas': coprod_counts.values
    })
    
    fig = px.bar(
        coprod_df,
        x='Número de países',
        y='Películas',
        title="Distribución de co-producciones",
        text_auto=True
    )
    fig.update_xaxes(type='category')
    fig.update_layout(height=400)
    
    return fig

def create_average_countries_chart(df):
    """Crea un gráfico de líneas para la evolución del promedio de países por película"""
    # Solo considerar películas con datos de país para el cálculo del promedio
    avg_countries = df[df['has_country_data']].groupby('year')['num_countries'].mean().reset_index()
    
    fig = px.line(
        avg_countries,
        x='year',
        y='num_countries',
        title="Evolución del promedio de países por película",
        markers=True
    )
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Promedio de países por película",
        height=400
    )
    
    return fig

def create_top_companies_chart(df, country, top_n=10):
    """Crea un gráfico de barras para las principales productoras de un país"""
    companies_df = get_country_production_companies(df, country, top_n)
    
    if companies_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No hay datos de productoras para {country}",
            height=400
        )
        return fig
    
    fig = px.bar(
        companies_df,
        y="Productora",
        x="Películas",
        orientation="h",
        title=f"Top productoras de {country}"
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=400
    )
    
    return fig

def create_choropleth_map(df):
    """Crea un mapa coroplético mostrando la cantidad de películas por país"""
    # Contar películas por país
    country_counts = df['countries_for_analysis'].apply(get_countries_from_string).explode().value_counts()
    
    # Crear DataFrame para visualización
    map_df = pd.DataFrame({
        'country': country_counts.index,
        'count': country_counts.values
    })
    
    # Mapear nombres de países a códigos ISO para el mapa
    country_codes = {}
    for country_name in map_df['country'].unique():
        try:
            # Intentar encontrar el país directamente
            country = pycountry.countries.get(name=country_name)
            if country:
                country_codes[country_name] = country.alpha_3
            else:
                # Buscar por nombre parcial
                found = False
                for country in pycountry.countries:
                    if country_name in country.name:
                        country_codes[country_name] = country.alpha_3
                        found = True
                        break
                
                if not found:
                    # Casos especiales
                    special_cases = {
                        'USA': 'USA',
                        'United States': 'USA',
                        'UK': 'GBR',
                        'United Kingdom': 'GBR',
                        'Russia': 'RUS',
                        'Czech Republic': 'CZE',
                    }
                    if country_name in special_cases:
                        country_codes[country_name] = special_cases[country_name]
                    else:
                        # No se encontró coincidencia
                        country_codes[country_name] = 'UNK'
        except Exception:
            country_codes[country_name] = 'UNK'
    
    map_df['iso_alpha'] = map_df['country'].map(country_codes)
    
    # Crear el mapa
    fig = px.choropleth(
        map_df,
        locations="iso_alpha",
        color="count",
        hover_name="country",
        color_continuous_scale=px.colors.sequential.Reds,
        title="Número de películas por país",
        projection="natural earth"
    )
    
    fig.update_layout(
        height=500,
        coloraxis_colorbar=dict(
            title="Películas"
        )
    )
    
    return fig

def create_coproduction_heatmap(df, countries):
    """Crea un heatmap de co-producciones entre países"""
    if not countries or len(countries) < 2:
        fig = go.Figure()
        fig.update_layout(
            title="Selecciona al menos 2 países para el heatmap",
            height=400
        )
        return fig
    
    # Obtener matriz de co-producciones
    coproduction_matrix = get_coproduction_matrix(df, countries)
    
    # Crear heatmap
    fig = px.imshow(
        coproduction_matrix,
        x=countries,
        y=countries,
        color_continuous_scale="Reds",
        title="Matriz de co-producciones",
        text_auto=True
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title="",
    )
    
    return fig

def create_network_graph(df, countries=None, focus_country=None):
    """
    Crea un gráfico de red para visualizar co-producciones entre países.
    
    Args:
        df: DataFrame con los datos de películas
        countries: Lista de países a incluir (opcional)
        focus_country: País para enfocar el análisis (opcional)
    
    Returns:
        Figura de Plotly con el gráfico de red
    """
    # Si se especifica un país de enfoque, obtener los países con los que co-produce
    if focus_country:
        # Filtrar películas que incluyen al país de enfoque
        country_films = df[df[focus_country] == 1]
        
        # Obtener todos los países que co-producen con el país de enfoque
        copr_countries = []
        for _, row in country_films.iterrows():
            countries_in_film = [c for c in df.columns if row[c] == 1 and c != focus_country]
            copr_countries.extend(countries_in_film)
        
        # Mantener solo países que tienen al menos una co-producción
        copr_countries = [c for c in set(copr_countries) if c in df.columns]
        
        # Establecer países a analizar
        if copr_countries:
            countries = [focus_country] + copr_countries
        else:
            countries = [focus_country]
    
    # Si no hay países especificados o son menos de 2, devolver figura vacía
    if not countries or len(countries) < 2:
        fig = go.Figure()
        fig.update_layout(
            title="No hay suficientes países para crear la red",
            height=500
        )
        return fig
    
    # Crear grafo dirigido
    G = nx.Graph()
    
    # Obtener matriz de co-producciones
    coproduction_matrix = get_coproduction_matrix(df, countries)
    
    # Añadir nodos y aristas al grafo
    for i, country1 in enumerate(countries):
        G.add_node(country1)
        for j, country2 in enumerate(countries):
            if i < j:  # Para evitar duplicados
                weight = coproduction_matrix.iloc[i, j]
                if weight > 0:
                    G.add_edge(country1, country2, weight=weight)
    
    # Eliminar nodos sin conexiones
    isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]
    for node in isolated_nodes:
        G.remove_node(node)
    
    # Si no hay aristas, devolver un mensaje
    if len(G.edges()) == 0:
        fig = go.Figure()
        fig.update_layout(
            title="No hay co-producciones entre los países seleccionados",
            height=500
        )
        return fig
    
    # Calcular posiciones de los nodos usando layout de resortes (spring layout)
    pos = nx.spring_layout(G, seed=42)
    
    # Normalizar pesos de aristas para grosor de líneas
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [3 * (weight / max_weight) + 1 for weight in edge_weights]
    
    # Determinar tamaño de nodos según su grado
    node_sizes = [30 * (G.degree(node) + 1) for node in G.nodes()]
    
    # Preparar datos para Plotly
    edge_x = []
    edge_y = []
    edge_texts = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        weight = G[edge[0]][edge[1]]['weight']
        edge_texts.append(f"{edge[0]} - {edge[1]}: {weight} co-producciones")
    
    # Crear trazado de aristas
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='rgba(150,150,150,0.7)'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Crear trazado de nodos
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}<br>Conexiones: {G.degree(node)}")
        # Colorear nodo de enfoque de rojo
        if focus_country and node == focus_country:
            node_color.append('red')
        else:
            node_color.append('royalblue')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=list(G.nodes()),
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            color=node_color,
            size=node_sizes,
            line=dict(width=2, color='white')
        )
    )
    
    # Crear figura
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=f'Red de co-producciones{"" if not focus_country else f" con {focus_country}"}',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600
                   ))
    
    return fig
