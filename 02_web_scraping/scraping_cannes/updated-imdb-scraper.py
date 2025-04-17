import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import quote
# Importamos la clase normalizadora
from company_normalizer import ProductionCompanyNormalizer

# Constantes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def clean_movie_title(title):
    """
    Limpia el título de la película eliminando texto entre paréntesis que no sea un año.
    """
    # Primero conservamos cualquier año entre paréntesis (patrón de 4 dígitos)
    years = re.findall(r'\((\d{4})\)', title)
    
    # Eliminar todos los paréntesis y su contenido
    clean_title = re.sub(r'\([^)]*\)', '', title)
    
    # Limpiar espacios extra
    clean_title = clean_title.strip()
    
    return clean_title

def search_imdb_id(title, year=None):
    """Busca una película en IMDb y devuelve su ID."""
    # Limpiar el título para eliminar texto adicional entre paréntesis
    clean_title = clean_movie_title(title)
    
    search_query = f"{clean_title}"
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
            
            # Verificar coincidencia - usando el título limpio para comparar
            if (not year or not result_year or abs(int(year) - result_year) <= 1) and \
               (result_title.lower() in clean_title.lower() or clean_title.lower() in result_title.lower()):
                
                # Extraer ID de IMDb
                link = title_elem.get("href", "")
                imdb_id_match = re.search(r'/title/(tt\d+)/', link)
                if imdb_id_match:
                    return imdb_id_match.group(1)
        
        # Si no encontramos coincidencia exacta, intentar con el primer resultado
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
    """Extrae información detallada de las compañías productoras de una película en IMDb."""
    if not imdb_id:
        return []
        
    url = f"https://www.imdb.com/title/{imdb_id}/companycredits"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscar las secciones de productoras
        production_companies = []
        
        # 1. Buscar la sección "Production Companies"
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

def normalize_companies_in_dataframe(df, company_column):
    """
    Normaliza los nombres de las compañías productoras en el DataFrame.
    
    Args:
        df: DataFrame con los datos
        company_column: Nombre de la columna que contiene las compañías productoras
        
    Returns:
        DataFrame actualizado con columnas de productoras normalizadas
    """
    if company_column not in df.columns:
        print(f"❌ Columna '{company_column}' no encontrada en el DataFrame")
        return df
    
    # Inicializar el normalizador
    normalizer = ProductionCompanyNormalizer()
    
    # Crear columna para productoras normalizadas
    normalized_column = f"{company_column}_normalized"
    df[normalized_column] = None
    
    # Normalizar cada fila
    for i, row in df.iterrows():
        companies_str = row[company_column]
        if pd.isna(companies_str) or companies_str == "":
            continue
            
        # Dividir por comas y normalizar cada compañía
        companies = [c.strip() for c in str(companies_str).split(',')]
        normalized_companies = [normalizer.normalize(c) for c in companies if c]
        
        # Eliminar duplicados
        normalized_companies = list(dict.fromkeys(normalized_companies))
        
        # Unir de nuevo con comas
        df.at[i, normalized_column] = ", ".join(normalized_companies)
    
    return df

def consolidate_production_companies(df):
    """
    Consolida todas las fuentes de compañías productoras en una sola columna
    y las normaliza.
    
    Args:
        df: DataFrame con los datos
        
    Returns:
        DataFrame actualizado con columna consolidada y normalizada
    """
    # Columnas que pueden contener información de productoras
    company_columns = [
        'productoras', 'production_company', 'imdb_production_companies', 
        'tmdb_production_companies'
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
    
    # Normalizar la columna consolidada
    df = normalize_companies_in_dataframe(df, 'productoras_consolidadas')
    
    # Agrupar compañías similares en toda la base de datos
    print("🔄 Agrupando compañías similares en todo el dataset...")
    
    # Extraer todas las compañías únicas
    all_companies = set()
    for value in df['productoras_consolidadas'].dropna():
        if isinstance(value, str):
            companies = [c.strip() for c in value.split(',')]
            all_companies.update([c for c in companies if c])
    
    # Agrupar compañías similares
    normalizer = ProductionCompanyNormalizer()
    clusters = normalizer.cluster_similar_companies(all_companies)
    
    # Crear mapa de reemplazo
    replacement_map = {}
    for canonical, variants in clusters.items():
        for variant in variants:
            if variant != canonical:
                replacement_map[variant] = canonical
    
    # Aplicar reemplazos a la columna normalizada
    for i, row in df.iterrows():
        if pd.isna(df.at[i, 'productoras_consolidadas_normalized']):
            continue
            
        companies = [c.strip() for c in df.at[i, 'productoras_consolidadas_normalized'].split(',')]
        replaced_companies = [replacement_map.get(c, c) for c in companies]
        
        # Eliminar duplicados que pudieron surgir de la normalización
        replaced_companies = list(dict.fromkeys(replaced_companies))
        
        df.at[i, 'productoras_consolidadas_normalized'] = ", ".join(replaced_companies)
    
    return df

def main():
    """Función principal que procesa el Excel de Cannes y enriquece con datos de IMDb."""
    try:
        # Cargar el archivo Excel existente
        input_file = "../datos_generados/cannes_base.xlsx"
        
        print(f"📊 Cargando archivo '{input_file}'...")
        df = pd.read_excel(input_file)
        
        # Añadir columnas para IMDb
        if "imdb_id" not in df.columns:
            df["imdb_id"] = None
        if "imdb_production_companies" not in df.columns:
            df["imdb_production_companies"] = None
        
        # Procesar cada película para obtener datos de IMDb
        for i, row in df.iterrows():
            # Obtener el título original y mostrar también el título limpio
            original_title = row['title']
            clean_title = clean_movie_title(original_title)
            
            print(f"\n📽️ Procesando {original_title} ({row['year']})...")
            if original_title != clean_title:
                print(f"   → Título limpio para búsqueda: '{clean_title}'")
            
            # Solo buscar películas sin ID de IMDb
            if pd.isna(df.at[i, "imdb_id"]) or df.at[i, "imdb_id"] == "":
                # Buscar ID de IMDb
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
                else:
                    print("❌ No se encontró ID de IMDb")
            
            # Esperar para no sobrecargar el servidor
            time.sleep(2)
        
        # NUEVO: Consolidar y normalizar productoras
        print("\n🔄 Consolidando y normalizando nombres de productoras...")
        df = consolidate_production_companies(df)
        print(f"✅ Normalización completada: {len(df)} películas procesadas")
        
        # Guardar resultados
        output_file = "../datos_generados/cannes_con_imdb.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Datos guardados en '{output_file}'")
        
    except Exception as e:
        print(f"Error en el procesamiento: {e}")

if __name__ == "__main__":
    main()
