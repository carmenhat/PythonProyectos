#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script unificado para extracción, enriquecimiento y normalización de datos sobre películas
de la sección oficial del Festival de Cannes (2015-2023).

Este script combina funcionalidad de varios scripts previos para extraer datos de películas desde Wikipedia,
IMDb y enriquecer la información con productoras y países de origen. Además, normaliza los nombres de las productoras
para evitar duplicados y errores de escritura.
El script realiza las siguientes tareas:
1. Extrae la lista de películas desde Wikipedia.
2. Enriquecer la información con productoras desde Wikipedia.
3. Busca IDs de IMDb y extrae información de productoras y países.
4. Normaliza los nombres de las productoras.
5. Consolida la información en un DataFrame y la guarda en un archivo Excel.
6. Agrupa compañías similares en toda la base de datos.
7. Guarda el resultado en un archivo Excel.
8. Maneja errores y excepciones durante el proceso de scraping y enriquecimiento.
9. Utiliza un normalizador de nombres de productoras para evitar duplicados y errores de escritura.
10. Añade emojis de banderas para los países de origen de las películas.
11. Permite la configuración de años a extraer y URLs base para Wikipedia.
12. Utiliza BeautifulSoup para el scraping de datos y pandas para la manipulación de datos.
nECESITA instalar las librerías: requests, pandas, beautifulsoup4, openpyxl y company_normalizer
company_normalizer es un módulo externo que debe estar en la misma carpeta que este script.: lo he creado para normalizar los nombres de las productoras.

Autor: carmenhat
Fecha: Abril 2025
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from urllib.parse import quote
from pathlib import Path
from company_normalizer import ProductionCompanyNormalizer  # Importamos el normalizador (definido en segundo archivo)

# Constantes
YEARS = list(range(2015, 2024))
BASE_WIKI_URL = "https://en.wikipedia.org/wiki/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Lista de países con emojis de banderas
COUNTRY_EMOJIS = {
    "Spain": "🇪🇸 Spain",
    "España": "🇪🇸 Spain",
    "France": "🇫🇷 France",
    "Francia": "🇫🇷 France",
    "USA": "🇺🇸 USA",
    "United States": "🇺🇸 USA",
    "Estados Unidos": "🇺🇸 USA",
    "Italy": "🇮🇹 Italy",
    "Italia": "🇮🇹 Italy",
    "Japan": "🇯🇵 Japan",
    "Japón": "🇯🇵 Japan",
    "South Korea": "🇰🇷 South Korea",
    "Corea del Sur": "🇰🇷 South Korea",
    "United Kingdom": "🇬🇧 United Kingdom",
    "Reino Unido": "🇬🇧 United Kingdom",
    "UK": "🇬🇧 United Kingdom",
    "Mexico": "🇲🇽 Mexico",
    "México": "🇲🇽 Mexico",
    "Canada": "🇨🇦 Canada",
    "Canadá": "🇨🇦 Canada",
    "Denmark": "🇩🇰 Denmark",
    "Dinamarca": "🇩🇰 Denmark",
    "Switzerland": "🇨🇭 Switzerland",
    "Suiza": "🇨🇭 Switzerland",
    "Turkey": "🇹🇷 Turkey",
    "Turquía": "🇹🇷 Turkey",
    "Iran": "🇮🇷 Iran",
    "Irán": "🇮🇷 Iran",
    "Germany": "🇩🇪 Germany",
    "Alemania": "🇩🇪 Germany",
    "Austria": "🇦🇹 Austria",
    "Belgium": "🇧🇪 Belgium",
    "Bélgica": "🇧🇪 Belgium",
    "Brazil": "🇧🇷 Brazil",
    "Brasil": "🇧🇷 Brazil",
    "China": "🇨🇳 China",
    "Russia": "🇷🇺 Russia",
    "Rusia": "🇷🇺 Russia",
    "Sweden": "🇸🇪 Sweden",
    "Suecia": "🇸🇪 Sweden"
}

def clean_movie_title(title):
    """
    Limpia el título de la película eliminando texto entre paréntesis 
    que no sea un año (de 4 dígitos).
    """
    # Primero conservamos cualquier año entre paréntesis
    years = re.findall(r'\((\d{4})\)', title)
    
    # Eliminar todos los paréntesis y su contenido
    clean_title = re.sub(r'\([^)]*\)', '', title)
    
    # Limpiar espacios extra
    clean_title = clean_title.strip()
    
    return clean_title

def extract_films_from_wiki():
    """
    Extrae la lista de películas del Festival de Cannes entre 2015-2023 desde Wikipedia.
    
    Returns:
        DataFrame con información básica de las películas
    """
    print("🌐 Iniciando extracción de películas de Wikipedia...")
    
    data = []
    
    for year in YEARS:
        print(f"\nProcesando {year}...")
        wiki_title = f"{year}_Cannes_Film_Festival"
        url = BASE_WIKI_URL.format(wiki_title)
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Levantar excepción si hay error HTTP
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al acceder a {url}: {e}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="wikitable")
        
        if not tables:
            print(f"⚠️ No se encontraron tablas relevantes en {url}")
            continue
        
        tablas_validas = 0
        
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            
            # Verificar si la tabla contiene datos de películas
            if not any("film" in h or "title" in h for h in headers):
                continue
            
            tablas_validas += 1
            
            for row in table.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) < 2:
                    continue
                
                # Extraer título de la película
                film_elem = cols[0]
                film = film_elem.get_text(strip=True)
                
                # Intentar extraer enlace a Wikipedia para la película
                film_link = film_elem.find("a")
                film_wiki_url = ""
                if film_link and "href" in film_link.attrs:
                    href = film_link["href"]
                    if href.startswith("/wiki/"):
                        film_wiki_url = f"https://en.wikipedia.org{href}"
                        
                # Si no hay enlace directo, construir uno basado en el título
                if not film_wiki_url:
                    film_url = film.replace(" ", "_")
                    film_wiki_url = f"https://en.wikipedia.org/wiki/{film_url}"
                
                # Extraer director
                director = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                
                # Buscar columna de países si existe
                countries = ""
                for i, h in enumerate(headers):
                    if "country" in h and i < len(cols):
                        countries = cols[i].get_text(strip=True)
                
                # Identificar país (España, Francia o USA)
                country_flag = ""
                for country_key, emoji_country in COUNTRY_EMOJIS.items():
                    if country_key in countries:
                        if not country_flag:  # Añadimos el primero que encontremos
                            country_flag = emoji_country
                        else:  # Si ya hay uno, añadimos coma y el nuevo
                            country_flag += f", {emoji_country}"
                
                # Extraer productoras si existe una columna relevante
                production_company = ""
                for i, h in enumerate(headers):
                    if ("production" in h or "studio" in h) and i < len(cols):
                        production_company = cols[i].get_text(strip=True)
                
                # Añadir datos a la lista
                data.append({
                    "year": year,
                    "title": film,
                    "director": director,
                    "countries": countries,
                    "section": "Official Selection (Wikipedia)",
                    "country_emoji": country_flag,
                    "production_company_wiki": production_company,
                    "film_wiki_url": film_wiki_url
                })
        
        if tablas_validas == 0:
            print(f"⚠️ No se encontró ninguna tabla con títulos de películas en {url}")
        
        # Pausa para no sobrecargar el servidor
        time.sleep(1)
    
    # Crear DataFrame con todos los datos recopilados
    if data:
        films_df = pd.DataFrame(data)
        print(f"✅ Se extrajeron datos de {len(films_df)} películas")
        return films_df
    else:
        print("❌ No se encontraron datos de películas")
        return pd.DataFrame()

def extract_wiki_production_companies(df):
    """
    Enriquece el DataFrame con las productoras extraídas de las páginas de Wikipedia
    de cada película.
    
    Args:
        df: DataFrame con los datos de las películas (debe contener 'film_wiki_url')
        
    Returns:
        DataFrame actualizado con información de productoras
    """
    print("\n🔍 Extrayendo productoras desde Wikipedia...")
    
    # Verificar que exista la columna necesaria
    if "film_wiki_url" not in df.columns:
        print("❌ Error: No existe la columna 'film_wiki_url'")
        return df
    
    # Columna para almacenar las productoras encontradas en Wikipedia
    df["production_company_wiki_page"] = ""
    
    for i, row in df.iterrows():
        url = row["film_wiki_url"]
        print(f"🔎 Procesando {row['title']} ({row['year']})")
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"❌ No se pudo acceder a {url}: {e}")
            continue
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Buscar en el infobox de la película
        infobox = soup.find("table", class_="infobox vevent")
        prod = ""
        
        if infobox:
            for row in infobox.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    label = th.get_text(strip=True).lower()
                    if "production" in label or "studio" in label or "productora" in label:
                        prod = td.get_text(separator=", ", strip=True)
                        break
        
        if prod:
            df.at[i, "production_company_wiki_page"] = prod
        
        # Pausa para no sobrecargar el servidor
        time.sleep(1)
    
    return df

def search_imdb_id(title, year=None):
    """
    Busca una película en IMDb y devuelve su ID.
    
    Args:
        title: Título de la película
        year: Año de la película (opcional)
        
    Returns:
        ID de IMDb o None si no se encuentra
    """
    # Limpiar el título para eliminar texto adicional
    clean_title = clean_movie_title(title)
    
    search_query = clean_title
    if year:
        search_query += f" {year}"
    
    encoded_query = quote(search_query)
    search_url = f"https://www.imdb.com/find/?q={encoded_query}&s=tt&exact=true&ref_=fn_tt_ex"
    
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscar resultados de películas
        results = soup.select("li.find-title-result")
        
        for result in results:
            # Extraer título y año
            title_elem = result.select_one(".ipc-metadata-list-summary-item__t")
            if not title_elem:
                continue
                
            result_title = title_elem.text.strip()
            
            # Extraer año si está disponible
            year_match = re.search(r'\((\d{4})\)', result.text)
            result_year = int(year_match.group(1)) if year_match else None
            
            # Verificar coincidencia - usar el título limpio para comparación
            if (not year or not result_year or abs(int(year) - result_year) <= 1) and \
               (result_title.lower() in clean_title.lower() or clean_title.lower() in result_title.lower()):
                
                # Extraer ID de IMDb
                link = title_elem.get("href", "")
                imdb_id_match = re.search(r'/title/(tt\d+)/', link)
                if imdb_id_match:
                    return imdb_id_match.group(1)
        
        # Si no encontramos coincidencia exacta, probar con el primer resultado
        if results:
            first_result = results[0]
            link = first_result.select_one("a[href*='/title/']")
            if link:
                imdb_id_match = re.search(r'/title/(tt\d+)/', link.get("href", ""))
                if imdb_id_match:
                    return imdb_id_match.group(1)
                    
        return None
        
    except Exception as e:
        print(f"Error buscando '{clean_title}' en IMDb: {e}")
        return None

def scrape_imdb_for_production_companies(imdb_id):
    """
    Extrae información de compañías productoras desde IMDb.
    
    Args:
        imdb_id: ID de IMDb de la película
        
    Returns:
        Lista de nombres de compañías productoras
    """
    if not imdb_id:
        return []
        
    url = f"https://www.imdb.com/title/{imdb_id}/companycredits"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        production_companies = []
        
        # Buscar la sección "Production Companies"
        production_section = None
        
        # Método 1: buscar por encabezado
        for header in soup.find_all(["h2", "h3", "h4"]):
            if "Production" in header.text and "Companies" in header.text:
                production_section = header.find_next("ul")
                break
                
        # Método 2: buscar por ID o clase específica
        if not production_section:
            production_section = soup.select_one("#production")
            
        # Método 3: buscar por la estructura general
        if not production_section:
            sections = soup.select(".ipc-metadata-list")
            for section in sections:
                header = section.select_one(".ipc-metadata-list-item__label")
                if header and "Production compan" in header.text.lower():
                    production_section = section
                    break
        
        # Extraer compañías
        if production_section:
            company_items = production_section.select("li")
            
            if not company_items:  # Estructura alternativa
                company_items = production_section.select(".ipc-metadata-list-item")
            
            for item in company_items:
                company_link = item.select_one("a")
                if company_link:
                    company_name = company_link.text.strip()
                    production_companies.append(company_name)
        
        return production_companies
        
    except Exception as e:
        print(f"Error obteniendo productoras para {imdb_id}: {e}")
        return []

def scrape_imdb_for_countries(imdb_id):
    """
    Extrae información de países desde IMDb.
    
    Args:
        imdb_id: ID de IMDb de la película
        
    Returns:
        Lista de países
    """
    if not imdb_id:
        return []
        
    url = f"https://www.imdb.com/title/{imdb_id}/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        countries = []
        
        # Método 1: Buscar en los metadatos principales
        metadata_blocks = soup.select(".ipc-metadata-list")
        for block in metadata_blocks:
            header = block.select_one(".ipc-metadata-list-item__label")
            if header and ("Countries of origin" in header.text or "Country of origin" in header.text):
                country_elements = block.select(".ipc-metadata-list-item__list-content-item")
                for element in country_elements:
                    countries.append(element.text.strip())
                break
        
        # Método 2: Buscar en la información técnica si está disponible
        if not countries:
            details_page = f"https://www.imdb.com/title/{imdb_id}/technical/"
            try:
                details_response = requests.get(details_page, headers=HEADERS, timeout=10)
                details_response.raise_for_status()
                details_soup = BeautifulSoup(details_response.text, "html.parser")
                
                for item in details_soup.select(".technical-list li"):
                    label = item.select_one("h4")
                    if label and "Country" in label.text:
                        value = item.select_one("div")
                        if value:
                            for country in value.text.split(","):
                                countries.append(country.strip())
            except Exception as e:
                print(f"Error obteniendo detalles técnicos para {imdb_id}: {e}")
        
        # Método 3: Buscar en la sección "Details" de la página principal
        if not countries:
            details_section = soup.select_one("[data-testid='title-details-section']")
            if details_section:
                country_item = details_section.find(lambda tag: tag.name == "li" and "Country" in tag.text)
                if country_item:
                    country_links = country_item.select("a")
                    for link in country_links:
                        countries.append(link.text.strip())
        
        return countries
        
    except Exception as e:
        print(f"Error obteniendo países para {imdb_id}: {e}")
        return []

def enrich_with_imdb_data(df):
    """
    Enriquece el DataFrame con datos de IMDb: IDs, productoras y países.
    
    Args:
        df: DataFrame con los datos de las películas
        
    Returns:
        DataFrame actualizado con información de IMDb
    """
    print("\n🎬 Enriqueciendo con datos de IMDb...")
    
    # Añadir columnas para IMDb si no existen
    if "imdb_id" not in df.columns:
        df["imdb_id"] = None
    if "imdb_production_companies" not in df.columns:
        df["imdb_production_companies"] = None
    if "imdb_countries" not in df.columns:
        df["imdb_countries"] = None
    
    # Procesar cada película
    for i, row in df.iterrows():
        # Obtener el título original y mostrar también el título limpio
        original_title = row['title']
        clean_title = clean_movie_title(original_title)
        
        print(f"\n📽️ Procesando {original_title} ({row['year']})...")
        if original_title != clean_title:
            print(f"   → Título limpio para búsqueda: '{clean_title}'")
        
        # Buscar ID de IMDb si no existe
        if pd.isna(df.at[i, "imdb_id"]) or df.at[i, "imdb_id"] == "":
            imdb_id = search_imdb_id(original_title, row["year"])
            
            if imdb_id:
                print(f"✅ ID de IMDb encontrado: {imdb_id}")
                df.at[i, "imdb_id"] = imdb_id
                
                # Obtener productoras
                companies = scrape_imdb_for_production_companies(imdb_id)
                
                if companies:
                    companies_str = ", ".join(companies)
                    print(f"🏢 Productoras: {companies_str}")
                    df.at[i, "imdb_production_companies"] = companies_str
                else:
                    print("❌ No se encontraron productoras")
                
                # Obtener países
                countries = scrape_imdb_for_countries(imdb_id)
                
                if countries:
                    # Convertir a formato con emoji si es posible
                    countries_with_emoji = []
                    for country in countries:
                        added = False
                        for target, emoji_name in COUNTRY_EMOJIS.items():
                            if target in country:
                                countries_with_emoji.append(emoji_name)
                                added = True
                                break
                        
                        # Si no encontramos emoji para el país, lo añadimos tal cual
                        if not added:
                            countries_with_emoji.append(country)
                    
                    # Guardar países en formato string
                    countries_str = ", ".join(countries)
                    emoji_countries_str = ", ".join(countries_with_emoji)
                    
                    print(f"🌍 Países: {countries_str}")
                    df.at[i, "imdb_countries"] = countries_str
                    
                    # Actualizar columna country_emoji si está vacía o incompleta
                    if pd.isna(df.at[i, "country_emoji"]) or df.at[i, "country_emoji"] == "":
                        df.at[i, "country_emoji"] = emoji_countries_str
                    # Si ya tiene datos, añadir solo los que faltan
                    else:
                        existing = set(df.at[i, "country_emoji"].split(", "))
                        new = set(emoji_countries_str.split(", "))
                        combined = existing.union(new)
                        df.at[i, "country_emoji"] = ", ".join(combined)
                        
                else:
                    print("❌ No se encontraron datos de países")
            else:
                print("❌ No se encontró ID de IMDb")
        
        # Esperar para no sobrecargar el servidor
        time.sleep(2)
    
    return df

def consolidate_production_companies(df, normalizer):
    """
    Consolida todas las fuentes de compañías productoras en una sola columna
    y las normaliza.
    
    Args:
        df: DataFrame con los datos
        normalizer: Instancia de ProductionCompanyNormalizer
        
    Returns:
        DataFrame actualizado con columna consolidada y normalizada
    """
    print("\n🔄 Consolidando y normalizando nombres de productoras...")
    
    # Columnas que pueden contener información de productoras
    company_columns = [
        'production_company_wiki', 
        'production_company_wiki_page', 
        'imdb_production_companies'
    ]
    
    # Verificar qué columnas existen en el DataFrame
    available_columns = [col for col in company_columns if col in df.columns]
    
    if not available_columns:
        print("❌ No se encontraron columnas con datos de productoras")
        return df
        
    # Crear columna consolidada
    df['productoras_consolidadas'] = None
    
    # Consolidar productoras de todas las fuentes
    for i, row in df.iterrows():
        all_companies = set()
        
        for col in available_columns:
            if not pd.isna(row[col]) and row[col] != "":
                companies = [c.strip() for c in str(row[col]).split(',')]
                all_companies.update([c for c in companies if c])
        
        if all_companies:
            df.at[i, 'productoras_consolidadas'] = ", ".join(all_companies)
    
    # Normalizar cada compañía productora
    df['productoras_normalizadas'] = None
    
    for i, row in df.iterrows():
        if pd.isna(row['productoras_consolidadas']) or row['productoras_consolidadas'] == "":
            continue
            
        # Dividir por comas y normalizar cada compañía
        companies = [c.strip() for c in str(row['productoras_consolidadas']).split(',')]
        normalized_companies = [normalizer.normalize(c) for c in companies if c]
        
        # Eliminar duplicados
        normalized_companies = list(dict.fromkeys(normalized_companies))
        
        # Unir de nuevo con comas
        df.at[i, 'productoras_normalizadas'] = ", ".join(normalized_companies)
    
    # Agrupar compañías similares en toda la base de datos
    print("🔄 Agrupando compañías similares en todo el dataset...")
    
    # Extraer todas las compañías únicas
    all_companies = set()
    for value in df['productoras_normalizadas'].dropna():
        if isinstance(value, str):
            companies = [c.strip() for c in value.split(',')]
            all_companies.update([c for c in companies if c])
    
    # Agrupar compañías similares
    clusters = normalizer.cluster_similar_companies(all_companies)
    
    # Crear mapa de reemplazo
    replacement_map = {}
    for canonical, variants in clusters.items():
        for variant in variants:
            if variant != canonical:
                replacement_map[variant] = canonical
    
    # Aplicar reemplazos a la columna normalizada
    for i, row in df.iterrows():
        if pd.isna(df.at[i, 'productoras_normalizadas']):
            continue
            
        companies = [c.strip() for c in df.at[i, 'productoras_normalizadas'].split(',')]
        replaced_companies = [replacement_map.get(c, c) for c in companies]
        
        # Eliminar duplicados que pudieron surgir de la normalización
        replaced_companies = list(dict.fromkeys(replaced_companies))
        
        df.at[i, 'productoras_normalizadas'] = ", ".join(replaced_companies)
    
    return df

def main():
    """Función principal que coordina todo el proceso."""
    try:
        print("🚀 Iniciando proceso unificado de extracción de datos de Cannes...")
        
        # Paso 1: Extracción inicial desde Wikipedia
        films_df = extract_films_from_wiki()
        
        if films_df.empty:
            print("❌ No se pudieron extraer datos. Fin del proceso.")
            return
        
        # Paso 2: Enriquecer con productoras desde Wikipedia
        films_df = extract_wiki_production_companies(films_df)
        
        # Paso 3: Enriquecer con datos de IMDb (IDs, productoras y países)
        films_df = enrich_with_imdb_data(films_df)
        
        # Paso 4: Normalizar productoras
        normalizer = ProductionCompanyNormalizer()
        films_df = consolidate_production_companies(films_df, normalizer)
        
        # Crear directorio para datos si no existe
        output_dir = Path("datos_generados")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar resultados
        output_file = output_dir / "cannes_dataset_unificado.xlsx"
        films_df.to_excel(output_file, index=False)
        print(f"\n✅ Proceso completado. Datos guardados en '{output_file.resolve()}'")
        
    except Exception as e:
        print(f"\n❌ Error en el procesamiento: {e}")

if __name__ == "__main__":
    main()
