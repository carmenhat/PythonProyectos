# nueva prueba para extraer productoras de IMDb
# funcionó a medias, fallaron muchas películas: crée el nuevo script updated-imdb-scraper.py 

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import quote
from pathlib import Path  

# Constantes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def search_imdb_id(title, year=None):
    """Busca una película en IMDb y devuelve su ID."""
    search_query = f"{title}"
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
            
            # Verificar coincidencia
            if (not year or not result_year or abs(int(year) - result_year) <= 1) and \
               (result_title.lower() in title.lower() or title.lower() in result_title.lower()):
                
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
        print(f"Error buscando '{title}' en IMDb: {e}")
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

def main():
    """Función principal que procesa el Excel de Cannes y enriquece con datos de IMDb."""
    try:
        # Cargar el archivo Excel existente
        input_file = Path(__file__).parent.parent / "datos_generados" / "cannes_wiki_enriquecido.xlsx"
        df = pd.read_excel(input_file)

        # Añadir columnas para IMDb si no existen
        if "imdb_id" not in df.columns:
            df["imdb_id"] = None
        if "imdb_production_companies" not in df.columns:
            df["imdb_production_companies"] = None

        # Procesar cada película
        for i, row in df.iterrows():
            print(f"\n📽️ Procesando {row['title']} ({row['year']})...")

            # Solo buscar películas sin ID de IMDb
            if pd.isna(df.at[i, "imdb_id"]) or df.at[i, "imdb_id"] == "":
                # Buscar ID de IMDb
                imdb_id = search_imdb_id(row["title"], row["year"])

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

        # Guardar resultados
        output_dir = Path(__file__).parent.parent / "datos_generados"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "cannes_y_productoras_imdb.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Datos guardados en '{output_file.resolve()}'")

    except Exception as e:
        print(f"Error en el procesamiento: {e}")

if __name__ == "__main__":
    main()