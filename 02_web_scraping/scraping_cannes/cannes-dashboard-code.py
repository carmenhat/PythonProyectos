# Continuación del código para el dashboard de Festival de Cannes
# Funcionalidades: Choropleth Map y Insight Highlighting

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

# Interfaz principal del dashboard (continuación)
def main():
    # Título y descripción
    st.markdown('<div class="main-title">🎬 Festival de Cannes: Análisis Internacional</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        Análisis de la participación internacional en el Festival de Cannes, con especial énfasis en la presencia española
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para filtros y opciones
    with st.sidebar:
        st.markdown("### Filtros y Opciones")
        
        # Cargar datos
        try:
            # Intentar cargar desde la ruta predeterminada
            file_path = "cannes_films_processed.csv"
            if not os.path.exists(file_path):
                # Si no existe, buscar en la carpeta actual
                files = [f for f in os.listdir() if f.endswith('.csv')]
                if files:
                    file_path = files[0]  # Tomar el primer CSV encontrado
                    st.info(f"Usando archivo: {file_path}")
                else:
                    st.error("No se encontraron archivos CSV para analizar.")
                    return
            
            # Cargar el dataset
            df = pd.read_csv(file_path)
            
            # Log información básica
            logger.info(f"Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Preprocesar datos (si es necesario)
            if 'num_countries' not in df.columns:
                # Crear columna con el número de países por película
                df['num_countries'] = df['countries_for_analysis'].apply(
                    lambda x: len(get_countries_from_string(x)) if pd.notna(x) else 0
                )
            
            # Crear columnas binarias para países principales
            for country in ['Spain', 'France', 'Italy', 'USA', 'United Kingdom', 'Germany']:
                if country not in df.columns:
                    df[country] = df['countries_for_analysis'].apply(
                        lambda x: 1 if pd.notna(x) and country in get_countries_from_string(x) else 0
                    )
            
            # Filtro de rango de años
            min_year = int(df['year'].min())
            max_year = int(df['year'].max())
            
            year_range = st.slider(
                "Seleccionar rango de años",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=1
            )
            
            # Filtrar el dataframe por años seleccionados
            filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
            
            # Información sobre el dataset filtrado
            st.markdown(f"**Datos filtrados:** {filtered_df.shape[0]} películas")
            
            # Opción para enfoque en España
            focus_spain = st.checkbox("Enfoque en participación española", value=True)
            
            # Selector de países para comparar
            all_countries = sorted(set([
                country for countries in df['countries_for_analysis'].dropna() 
                for country in get_countries_from_string(countries)
            ]))
            
            default_countries = ['Spain', 'France', 'Italy', 'USA']
            compare_countries = st.multiselect(
                "Países para comparar",
                options=all_countries,
                default=default_countries
            )
            
            # Opción para ajustar el peso mínimo en redes
            min_weight = st.slider(
                "Peso mínimo para conexiones en red",
                min_value=1,
                max_value=10,
                value=2,
                step=1,
                help="Número mínimo de co-producciones para mostrar una conexión en el gráfico de red"
            )
            
        except Exception as e:
            st.error(f"Error al cargar o procesar los datos: {str(e)}")
            logger.error(f"Error en la carga de datos: {str(e)}", exc_info=True)
            return
    
    # Contenido principal del dashboard
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen General", 
        "🇪🇸 Análisis de España", 
        "🌍 Distribución Mundial", 
        "🔍 Insights"
    ])
    
    # Pestaña 1: Resumen General
    with tab1:
        st.markdown('<div class="subtitle">Resumen General</div>', unsafe_allow_html=True)
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Total Películas</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{filtered_df.shape[0]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            total_countries = len(set([
                country for countries in filtered_df['countries_for_analysis'].dropna() 
                for country in get_countries_from_string(countries)
            ]))
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Países Participantes</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{total_countries}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            avg_countries = filtered_df['num_countries'].mean()
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Media de Países/Película</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{avg_countries:.2f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            coprod_pct = (filtered_df[filtered_df['num_countries'] > 1].shape[0] / filtered_df.shape[0]) * 100
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">% Co-producciones</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{coprod_pct:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top 10 países
        st.markdown("#### Top 10 Países con Mayor Participación")
        country_counts = count_countries(filtered_df, 'countries_for_analysis')
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Crear gráfico de barras para top países
        countries = [c[0] for c in top_countries]
        counts = [c[1] for c in top_countries]
        
        # Asignar colores basados en mapeo, destacando España
        colors = []
        for country in countries:
            if country == 'Spain':
                colors.append("#FFCC00")  # Amarillo España
            elif country in COUNTRY_MAPPING:
                colors.append(COUNTRY_MAPPING[country]["color"])
            else:
                colors.append("#1f77b4")  # Color por defecto
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=countries,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Países con mayor número de películas",
            xaxis_title="País",
            yaxis_title="Número de películas",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Red de co-producciones
        st.markdown("#### Red de Co-producciones Internacionales")
        
        # Crear gráfico de red utilizando la función
        network_fig = create_network_graph(
            filtered_df, 
            selected_countries=compare_countries if compare_countries else None,
            highlight_country='Spain' if focus_spain else None,
            min_weight=min_weight
        )
        
        st.plotly_chart(network_fig, use_container_width=True)
        
        st.markdown("""
        <div class="info-box">
            <b>Sobre este gráfico:</b> La red muestra las co-producciones entre países. 
            El tamaño de cada nodo representa el número total de películas de ese país.
            El grosor de las líneas representa el número de co-producciones entre países.
        </div>
        """, unsafe_allow_html=True)
    
    # Pestaña 2: Análisis de España
    with tab2:
        st.markdown('<div class="subtitle">Análisis de la Participación Española</div>', unsafe_allow_html=True)
        
        # KPIs de España
        spain_kpis = calculate_spain_kpis(df, year_range)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="kpi-container kpi-highlight">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Películas Españolas</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{spain_kpis["total"]}</div>', unsafe_allow_html=True)
            
            # Mostrar tendencia si está disponible
            if spain_kpis["trend"] is not None:
                trend_class = "trend-up" if spain_kpis["trend"] > 0 else "trend-down" if spain_kpis["trend"] < 0 else "trend-neutral"
                trend_arrow = "↑" if spain_kpis["trend"] > 0 else "↓" if spain_kpis["trend"] < 0 else "→"
                st.markdown(f'<div class="kpi-trend {trend_class}">{trend_arrow} {abs(spain_kpis["trend"]):.1f}%</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">% del Total</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{spain_kpis["percentage"]:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Ranking</div>', unsafe_allow_html=True)
            ranking_value = f"#{spain_kpis['ranking']}" if spain_kpis['ranking'] > 0 else "N/A"
            st.markdown(f'<div class="kpi-value">{ranking_value}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-title">Co-producciones</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{spain_kpis["coproductions"]}</div>', unsafe_allow_html=True)
            coprod_pct = spain_kpis["coprod_percentage"]
            st.markdown(f'<div class="kpi-trend">({coprod_pct:.1f}% del total español)</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Evolución temporal de la participación española
        st.markdown("#### Evolución de la Participación Española")
        
        # Obtener métricas anuales
        spain_yearly_metrics = get_spain_yearly_metrics(df, compare_countries)
        
        # Filtrar por rango seleccionado
        spain_yearly_metrics = spain_yearly_metrics[
            (spain_yearly_metrics['year'] >= year_range[0]) & 
            (spain_yearly_metrics['year'] <= year_range[1])
        ]
        
        # Crear gráfico de línea para evolución temporal
        fig = go.Figure()
        
        # Línea para películas españolas
        fig.add_trace(go.Scatter(
            x=spain_yearly_metrics['year'],
            y=spain_yearly_metrics['spain_films'],
            mode='lines+markers',
            name='Películas Españolas',
            line=dict(color='#FFCC00', width=3),
            marker=dict(size=8, color='#FFCC00', line=dict(width=1, color='#AA151B'))
        ))
        
        # Línea para co-producciones españolas
        fig.add_trace(go.Scatter(
            x=spain_yearly_metrics['year'],
            y=spain_yearly_metrics['spain_coprods'],
            mode='lines+markers',
            name='Co-producciones Españolas',
            line=dict(color='#AA151B', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Evolución de la Participación Española a