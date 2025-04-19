import pandas as pd
import os
import re
from collections import Counter
import streamlit as st

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

@st.cache_data
def load_data():
    """Carga y preprocesa los datos del dataset de Cannes"""
    # Intentar cargar el archivo con datos expandidos
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(script_dir, "datos_generados/cannes_dataset_unificado.xlsx")
    
    if os.path.exists(file_path):
        st.sidebar.success("✅ Usando datos del archivo cannes_dataset_unificado.xlsx")
    else:
        st.error("❌ No se encontró el archivo cannes_dataset_unificado.xlsx")
        st.stop()
    
    # Cargar el DataFrame
    df = pd.read_excel(file_path)
    
    # Crear columna para análisis basada en los datos disponibles
    # Usando 'countries' como columna principal para el análisis
    if 'countries' in df.columns:
        df['countries_for_analysis'] = df['countries']
    else:
        st.error("❌ No se encontró la columna 'countries' en el archivo.")
        st.stop()
    
    # Extraer año como entero
    df['year'] = df['year'].astype(int)
    
    # Generar el conjunto de países únicos
    unique_countries = set()
    for countries in df['countries_for_analysis'].dropna():
        unique_countries.update(get_countries_from_string(countries))
    unique_countries = list(unique_countries)
    
    # Crear todas las columnas de países de una vez
    country_columns = {}
    for country in unique_countries:
        country_columns[country] = df['countries_for_analysis'].apply(
            lambda x: 1 if country in get_countries_from_string(x) else 0
        )
    
    # Convertir el diccionario a DataFrame
    country_df = pd.DataFrame(country_columns)
    
    # Unir las columnas de países al DataFrame original
    df = pd.concat([df, country_df], axis=1)
    
    # Añadir columna de total_countries per movie
    df['num_countries'] = df['countries_for_analysis'].apply(
        lambda x: 0 if pd.isna(x) else len(get_countries_from_string(x))
    )
    
    # Adaptación para las productoras
    if 'productoras_normalizadas' in df.columns:
        df['productoras_consolidadas_normalized'] = df['productoras_normalizadas']
    elif 'productoras_consolidadas' in df.columns:
        df['productoras_consolidadas_normalized'] = df['productoras_consolidadas']
    
    # Crear columna para indicar si hay datos de país disponibles
    df['has_country_data'] = df['countries_for_analysis'].notna() & (df['countries_for_analysis'] != "")
    
    return df, unique_countries

def filter_data(df, year_range, selected_section='Todas'):
    """Filtra el DataFrame según los criterios seleccionados"""
    filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    
    # Filtrar por sección si se seleccionó una específica
    if 'section' in df.columns and selected_section != "Todas":
        filtered_df = filtered_df[filtered_df['section'] == selected_section]
    
    return filtered_df

def get_coproduction_matrix(df, countries):
    """Crea una matriz de co-producciones entre países"""
    matrix = pd.DataFrame(0, index=countries, columns=countries)
    
    for _, row in df.iterrows():
        movie_countries = get_countries_from_string(row['countries_for_analysis'])
        movie_countries = [c for c in movie_countries if c in countries]
        
        if len(movie_countries) > 1:
            for i in range(len(movie_countries)):
                for j in range(i+1, len(movie_countries)):
                    country1, country2 = movie_countries[i], movie_countries[j]
                    matrix.loc[country1, country2] += 1
                    matrix.loc[country2, country1] += 1
    
    return matrix

def get_country_production_companies(df, country, top_n=10):
    """Obtiene las principales productoras de un país"""
    if "productoras_consolidadas_normalized" not in df.columns:
        return pd.DataFrame(columns=["Productora", "Películas"])
    
    # Filtrar películas del país
    country_films = df[df[country] == 1]
    
    # Extraer todas las productoras
    all_companies = []
    for companies in country_films["productoras_consolidadas_normalized"].dropna():
        all_companies.extend([c.strip() for c in str(companies).split(',')])
    
    # Contar frecuencias
    company_counter = Counter(all_companies)
    
    # Crear DataFrame
    companies_df = pd.DataFrame({
        "Productora": [company for company, _ in company_counter.most_common(top_n)],
        "Películas": [count for _, count in company_counter.most_common(top_n)]
    })
    
    return companies_df
