# Continuación del código para el dashboard de Cannes
# Funciones para el mapa de coropletas y destacado de patrones

def hex_to_rgb(hex_color):
    """
    Convierte color hexadecimal a RGB
    
    Args:
        hex_color (str): Color en formato hexadecimal (ej: "#FFCC00")
        
    Returns:
        tuple: Tupla con valores RGB (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_choropleth_map(df, year_range=None):
    """
    Crea un mapa de coropletas mostrando el número de películas por país
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        year_range (tuple): Rango de años para filtrar (opcional)
        
    Returns:
        Figure: Objeto de figura de Plotly
    """
    # Filtrar por rango de años si se especifica
    if year_range:
        filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    else:
        filtered_df = df
    
    # Contar películas por país
    country_counts = {}
    main_countries = filtered_df.columns[filtered_df.dtypes == 'int64']
    
    for country in main_countries:
        # Omitir columnas numéricas que no sean países
        if country in ['year', 'num_countries']:
            continue
        country_counts[country] = filtered_df[country].sum()
    
    # Preparar datos para el mapa
    data = []
    for country, count in country_counts.items():
        # Mapear nombres de países para compatibilidad con Plotly
        plotly_country = country
        if country == "USA":
            plotly_country = "United States"
        elif country == "UK":
            plotly_country = "United Kingdom"
        
        data.append({
            "country": plotly_country,
            "count": count,
            "original_name": country
        })
    
    # Crear DataFrame para el mapa
    choropleth_df = pd.DataFrame(data)
    
    # Crear mapa de coropletas
    fig = px.choropleth(
        choropleth_df,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        color_continuous_scale=px.colors.sequential.Reds,
        title=f"Películas por país en el Festival de Cannes ({year_range[0]}-{year_range[1] if year_range else 'Actualidad'})",
        labels={"count": "Número de películas"},
        hover_data={
            "country": False,
            "count": True,
            "original_name": False
        }
    )
    
    # Personalizar diseño
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        coloraxis_colorbar=dict(
            title="Películas",
            thicknessmode="pixels",
            thickness=20,
            lenmode="pixels",
            len=300
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
    )
    
    # Destacar España en el mapa
    fig.add_scattergeo(
        locations=["Spain"],
        locationmode="country names",
        marker=dict(
            size=12,
            color=COLOR_SECONDARY,
            line=dict(width=2, color="black")
        ),
        name="España",
        showlegend=True
    )
    
    return fig

def detect_insights(df, focus_country="Spain"):
    """
    Detecta automáticamente patrones interesantes en los datos
    
    Args:
        df (DataFrame): DataFrame con datos de películas
        focus_country (str): País en el que enfocar el análisis
        
    Returns:
        list: Lista de insights detectados
    """
    insights = []
    years = sorted(df['year'].unique())
    
    if len(years) < 2:
        return ["No hay suficientes años para detectar patrones."]
    
    # Agrupar por año
    yearly_data = df.groupby('year')
    
    # Calcular métricas anuales para el país de enfoque
    yearly_counts = yearly_data[focus_country].sum()
    yearly_totals = yearly_data.size()
    yearly_percentages = (yearly_counts / yearly_totals * 100).round(1)
    
    # 1. Tendencia general
    first_year, last_year = years[0], years[-1]
    first_count = yearly_counts[first_year]
    last_count = yearly_counts[last_year]
    
    if last_count > first_count:
        increase_pct = ((last_count - first_count) / first_count * 100).round(1) if first_count > 0 else 100
        insights.append(f"🔼 {focus_country} ha aumentado su presencia un {increase_pct}% desde {first_year} hasta {last_year}.")
    elif last_count < first_count:
        decrease_pct = ((first_count - last_count) / first_count * 100).round(1)
        insights.append(f"🔽 {focus_country} ha reducido su presencia un {decrease_pct}% desde {first_year} hasta {last_year}.")
    else:
        insights.append(f"➡️ {focus_country} mantiene estable su presencia entre {first_year} y {last_year}.")
    
    # 2. Año pico
    peak_year = yearly_counts.idxmax()
    peak_count = yearly_counts[peak_year]
    insights.append(f"🏆 El año con mayor presencia de {focus_country} fue {peak_year} con {peak_count} películas.")
    
    # 3. Comparativa con año anterior (si hay datos del año más reciente)
    if len(years) >= 2:
        current_year = years[-1]
        previous_year = years[-2]
        
        current_count = yearly_counts[current_year]
        previous_count = yearly_counts[previous_year]
        
        if current_count > previous_count:
            change_pct = ((current_count - previous_count) / previous_count * 100).round(1) if previous_count > 0 else 100
            insights.append(f"📈 {focus_country} tuvo un {change_pct}% más de películas en {current_year} en comparación con {previous_year}.")
        elif current_count < previous_count:
            change_pct = ((previous_count - current_count) / previous_count * 100).round(1)
            insights.append(f"📉 {focus_country} tuvo un {change_pct}% menos de películas en {current_year} en comparación con {previous_year}.")
        else:
            insights.append(f"🔄 {focus_country} mantuvo el mismo número de películas en {current_year} que en {previous_year}.")
    
    # 4. Patrones especiales (años consecutivos de crecimiento/decrecimiento)
    trend_count = 0
    trend_direction = None
    
    for i in range(1, len(years)):
        current = yearly_counts[years[i]]
        previous = yearly_counts[years[i-1]]
        
        if current > previous:
            current_direction = "up"
        elif current < previous:
            current_direction = "down"
        else:
            current_direction = "same"
            
        if trend_direction is None:
            trend_direction = current_direction
            trend_count = 1
        elif current_direction == trend_direction:
            trend_count += 1
        else:
            if trend_count >= 3:  # Considerar significativo 3+ años
                trend_text = "crecimiento" if trend_direction == "up" else "decrecimiento"
                insights.append(f"📊 {focus_country} experimentó {trend_count} años consecutivos de {trend_text} entre {years[i-trend_count]} y {years[i-1]}.")
            
            trend_direction = current_direction
            trend_count = 1
    
    # Comprobar el último período
    if trend_count >= 3:
        trend_text = "crecimiento" if trend_direction == "up" else "decrecimiento"
        insights.append(f"📊 {focus_country} experimentó {trend_count} años consecutivos de {trend_text} entre {years[-trend_count]} y {years[-1]}.")
    
    # 5. Mejor posición en el ranking
    country_rankings = calculate_yearly_rankings(df, df.columns[df.dtypes == 'int64'])
    best_ranking = float('inf')
    best_ranking_year = None
    
    for year, ranking in country_rankings.items():
        if focus_country in ranking and ranking[focus_country] < best_ranking:
            best_ranking = ranking[focus_country]
            best_ranking_year = year
    
    if best_ranking_year:
        insights.append(f"🥇 La mejor posición de {focus_country} fue #{best_ranking} en el año {best_ranking_year}.")
    
    # 6. Comparar con la media del festival
    avg_percentage = yearly_percentages.mean().round(1)
    insights.append(f"📊 En promedio, {focus_country} representa el {avg_percentage}% de las películas del festival.")
    
    # 7. Co-producciones destacadas
    spain_movies = df[df[focus_country] == 1]
    coprod_spain = spain_movies[spain_movies['num_countries'] > 1]
    coprod_percentage = (len(coprod_spain) / len(spain_movies) * 100).round(1) if len(spain_movies) > 0 else 0
    
    insights.append(f"🤝 El {coprod_percentage}% de las películas de {focus_country} son co-producciones.")
    
    # 8. Principales socios
    top_partners = get_top_coprod_countries_with_spain(df)
    if top_partners:
        top_partner, count = top_partners[0]
        insights.append(f"🌍 El principal socio de co-producción de {focus_country} es {top_partner} con {count} películas.")
    
    return insights

# Principal componente del dashboard para integrar en el código principal
def main_dashboard_extension(df):
    """
    Sección principal con las nuevas funcionalidades del dashboard
    
    Args:
        df (DataFrame): DataFrame con datos de películas
    """
    # Sección para el mapa de coropletas
    st.markdown('<div class="subtitle">Mapa Internacional de Películas</div>', unsafe_allow_html=True)
    
    # Selector de rango de años para el mapa
    col1, col2 = st.columns(2)
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    
    with col1:
        start_year = st.slider("Año inicial:", min_year, max_year, min_year)
    
    with col2:
        end_year = st.slider("Año final:", start_year, max_year, max_year)
    
    # Crear y mostrar el mapa de coropletas
    choropleth_fig = create_choropleth_map(df, year_range=(start_year, end_year))
    st.plotly_chart(choropleth_fig, use_container_width=True)
    
    # Sección para destacar insights
    st.markdown('<div class="subtitle">Insights Destacados sobre España</div>', unsafe_allow_html=True)
    
    # Filtrar por rango de años seleccionado
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    # Detectar insights automáticamente
    insights = detect_insights(filtered_df, focus_country="Spain")
    
    # Mostrar insights en tarjetas
    cols = st.columns(2)
    for i, insight in enumerate(insights):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="kpi-container kpi-highlight">
                {insight}
            </div>
            """, unsafe_allow_html=True)
            st.write("")  # Espacio entre tarjetas
    
    # Panel de comparación con otros países
    st.markdown('<div class="subtitle">Comparativa España vs. Otros Países</div>', unsafe_allow_html=True)
    
    # Selector de países para comparar
    countries_to_compare = st.multiselect(
        "Selecciona países para comparar con España:",
        options=[c for c in df.columns if c in COUNTRY_MAPPING and c != "Spain"],
        default=["France", "Italy"],
        max_selections=3
    )
    
    if countries_to_compare:
        # Preparar datos para la comparación
        comparison_data = []
        years = sorted(filtered_df['year'].unique())
        
        for year in years:
            year_data = {'year': year}
            year_df = filtered_df[filtered_df['year'] == year]
            
            # Añadir España
            year_data['Spain'] = year_df['Spain'].sum()
            
            # Añadir países seleccionados
            for country in countries_to_compare:
                year_data[country] = year_df[country].sum()
            
            comparison_data.append(year_data)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Gráfico de líneas comparativo
        fig = px.line(
            comparison_df, 
            x='year', 
            y=['Spain'] + countries_to_compare,
            title='Evolución de películas por país',
            labels={'value': 'Número de películas', 'variable': 'País'},
            markers=True,
            color_discrete_map={
                'Spain': COLOR_SECONDARY,
                'France': COUNTRY_MAPPING['France']['color'],
                'Italy': COUNTRY_MAPPING['Italy']['color'],
                'USA': COUNTRY_MAPPING['USA']['color'],
                'United Kingdom': COUNTRY_MAPPING['United Kingdom']['color'],
                'Germany': COUNTRY_MAPPING['Germany']['color']
            }
        )
        
        # Personalizar diseño
        fig.update_layout(
            xaxis_title='Año',
            yaxis_title='Películas',
            legend_title='País',
            hovermode='x unified',
            height=400
        )
        
        # Mostrar gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Añadir tabla comparativa con métricas clave
        st.markdown("### Métricas comparativas")
        
        # Calcular métricas para cada país
        metrics_data = []
        
        # Añadir España primero
        spain_total = filtered_df['Spain'].sum()
        spain_coprods = filtered_df[(filtered_df['Spain'] == 1) & (filtered_df['num_countries'] > 1)].shape[0]
        spain_coprod_pct = (spain_coprods / spain_total * 100).round(1) if spain_total > 0 else 0
        
        metrics_data.append({
            'País': f"🇪🇸 España",
            'Total películas': spain_total,
            'Co-producciones': spain_coprods,
            '% Co-producciones': spain_coprod_pct,
            'Tendencia': '+' if insights[0].startswith('🔼') else ('-' if insights[0].startswith('🔽') else '=')
        })
        
        # Añadir los demás países
        for country in countries_to_compare:
            country_emoji = COUNTRY_MAPPING[country]['emoji']
            country_name = COUNTRY_MAPPING[country]['name']
            
            country_total = filtered_df[country].sum()
            country_coprods = filtered_df[(filtered_df[country] == 1) & (filtered_df['num_countries'] > 1)].shape[0]
            country_coprod_pct = (country_coprods / country_total * 100).round(1) if country_total > 0 else 0
            
            # Calcular tendencia
            yearly_counts = filtered_df.groupby('year')[country].sum()
            if len(yearly_counts) >= 2:
                first_year, last_year = yearly_counts.index[0], yearly_counts.index[-1]
                if yearly_counts[last_year] > yearly_counts[first_year]:
                    trend = '+'
                elif yearly_counts[last_year] < yearly_counts[first_year]:
                    trend = '-'
                else:
                    trend = '='
            else:
                trend = 'N/A'
            
            metrics_data.append({
                'País': f"{country_emoji} {country_name}",
                'Total películas': country_total,
                'Co-producciones': country_coprods,
                '% Co-producciones': country_coprod_pct,
                'Tendencia': trend
            })
        
        # Convertir a DataFrame y mostrar
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, hide_index=True, use_container_width=True)

# Código para integrar en la aplicación principal
# Este es el código que deberías añadir al final de tu script principal

def integrated_main():
    """
    Función principal integrada que añade las nuevas funcionalidades
    """
    try:
        # Tu código existente para cargar datos
        # ...
        
        # Suponiendo que df ya está cargado y procesado
        
        # Añadir la nueva pestaña en tu interfaz de pestañas existente
        tab1, tab2, tab3, tab4 = st.tabs(["Visión General", "Análisis de España", "Red de Co-producciones", "Mapa Internacional"])
        
        with tab1:
            # Tu código existente para la visión general
            pass
            
        with tab2:
            # Tu código existente para análisis de España
            pass
            
        with tab3:
            # Tu código existente para red de co-producciones
            pass
            
        with tab4:
            # Nuevas funcionalidades
            main_dashboard_extension(df)
            
    except Exception as e:
        st.error(f"Ha ocurrido un error: {e}")
        logger.error(f"Error en la aplicación: {e}", exc_info=True)

# Al final del archivo
if __name__ == "__main__":
    integrated_main()
