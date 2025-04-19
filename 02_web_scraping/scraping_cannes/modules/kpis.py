import pandas as pd
from typing import List, Dict, Any, Optional
from .data_processing import get_countries_from_string


def calculate_kpis(df: pd.DataFrame, countries: List[str], focus_country: Optional[str] = None) -> Dict[str, Any]:
    """
    Calcula los KPIs principales del análisis del Festival de Cannes.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos filtrados
        countries (List[str]): Lista de países seleccionados para el análisis
        focus_country (Optional[str]): País específico para calcular métricas adicionales
        
    Returns:
        Dict[str, Any]: Diccionario con los KPIs calculados
    """
    # Inicializar diccionario de KPIs
    kpis = {}
    
    # Total de películas en el dataset filtrado
    kpis['total_films'] = len(df)
    
    # Convertir los países a formato lista para facilitar análisis
    if not df.empty and 'countries_for_analysis' in df.columns:
        # Obtener todos los países únicos mencionados
        all_countries = set()
        for countries_str in df['countries_for_analysis'].dropna():
            countries_list = get_countries_from_string(countries_str)
            all_countries.update(countries_list)
        
        kpis['total_countries'] = len(all_countries)
        
        # Calcular número de países por película
        countries_per_film = df['countries_for_analysis'].dropna().apply(
            lambda x: len(get_countries_from_string(x))
        )
        
        # Media de países por película
        kpis['avg_countries_per_film'] = countries_per_film.mean() if not countries_per_film.empty else 0
        
        # Porcentaje de co-producciones (películas con más de un país)
        coproductions_count = (countries_per_film > 1).sum()
        kpis['coproduction_percentage'] = (coproductions_count / len(df) * 100) if len(df) > 0 else 0
    else:
        # Valores por defecto si no hay datos o columna
        kpis['total_countries'] = 0
        kpis['avg_countries_per_film'] = 0
        kpis['coproduction_percentage'] = 0
    
    # Si se especifica un país de enfoque, calcular KPIs adicionales
    if focus_country:
        # Películas que incluyen al país de enfoque
        country_films = df['countries_for_analysis'].dropna().apply(
            lambda x: focus_country in get_countries_from_string(x)
        ).sum()
        
        kpis['country_films'] = country_films
        
        # Porcentaje del total de películas
        kpis['country_percentage'] = (country_films / len(df) * 100) if len(df) > 0 else 0
        
        # Co-producciones del país de enfoque (películas donde participa junto con otros países)
        country_coproductions = df['countries_for_analysis'].dropna().apply(
            lambda x: focus_country in get_countries_from_string(x) and len(get_countries_from_string(x)) > 1
        ).sum()
        
        kpis['country_coproductions'] = country_coproductions
        
        # Porcentaje de co-producciones del país de enfoque
        kpis['country_coproduction_percentage'] = (
            country_coproductions / country_films * 100
        ) if country_films > 0 else 0
        
        # Principales países co-productores con el país de enfoque
        coproducer_countries = []
        for countries_str in df['countries_for_analysis'].dropna():
            countries_list = get_countries_from_string(countries_str)
            if focus_country in countries_list and len(countries_list) > 1:
                coproducer_countries.extend([c for c in countries_list if c != focus_country])
        
        # Top co-productores
        coproducer_counts = pd.Series(coproducer_countries).value_counts()
        kpis['top_coproducers'] = coproducer_counts.head(5).to_dict() if not coproducer_counts.empty else {}
    
    # Añadir KPIs para todos los países seleccionados
    if countries:
        country_films_counts = {}
        for country in countries:
            # Contar películas por país
            count = df['countries_for_analysis'].dropna().apply(
                lambda x: country in get_countries_from_string(x)
            ).sum()
            country_films_counts[country] = count
        
        kpis['country_films_counts'] = country_films_counts
    
    # Calcular distribución de co-producciones por número de países
    coproduction_distribution = countries_per_film.value_counts().sort_index().to_dict()
    kpis['coproduction_distribution'] = coproduction_distribution
    
    # Calcular evolución anual de co-producciones si hay datos de año
    if 'year' in df.columns:
        yearly_stats = df.groupby('year').apply(
            lambda x: {
                'total': len(x),
                'coproductions': (x['countries_for_analysis'].dropna().apply(
                    lambda y: len(get_countries_from_string(y)) > 1
                )).sum(),
                'avg_countries': x['countries_for_analysis'].dropna().apply(
                    lambda y: len(get_countries_from_string(y))
                ).mean()
            }
        ).to_dict()
        
        kpis['yearly_stats'] = yearly_stats
    
    # Si hay datos de productoras, añadir análisis
    if 'productoras_normalizadas' in df.columns or 'productoras_consolidadas_normalized' in df.columns:
        # Usar la columna correcta según la disponibilidad
        prod_column = 'productoras_consolidadas_normalized' if 'productoras_consolidadas_normalized' in df.columns else 'productoras_normalizadas'
        
        # Total de productoras únicas
        all_production_companies = set()
        for companies_str in df[prod_column].dropna():
            # Asumiendo que las productoras están separadas por comas
            companies_list = companies_str.split(',')
            companies_list = [comp.strip() for comp in companies_list if comp.strip()]
            all_production_companies.update(companies_list)
        
        kpis['total_production_companies'] = len(all_production_companies)
    
    return kpis
