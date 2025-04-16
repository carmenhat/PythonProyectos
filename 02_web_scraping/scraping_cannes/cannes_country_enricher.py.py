import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
import json
from tqdm import tqdm
from urllib.parse import quote

# Constantes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Lista expandida de países relevantes (con emojis de banderas)
COUNTRY_EMOJIS = {
    "Spain": "🇪🇸 Spain",
    "France": "🇫🇷 France",
    "USA": "🇺🇸 USA",
    "United States": "🇺🇸 USA",
    "Italy": "🇮🇹 Italy",
    "Japan": "🇯🇵 Japan",
    "South Korea": "🇰🇷 South Korea", 
    "United Kingdom": "🇬🇧 United Kingdom",
    "UK": "🇬🇧 United Kingdom",
    "Mexico": "🇲🇽 Mexico",
    "Canada": "🇨🇦 Canada",
    "Denmark": "🇩🇰 Denmark",
    "Switzerland": "🇨🇭 Switzerland",
    "Turkey": "🇹🇷 Turkey",
    "Iran": "🇮🇷 Iran",
    "Germany": "🇩🇪 Germany",
    "Austria": "🇦🇹 Austria",
    "Belgium": "🇧🇪 Belgium",
    "Brazil": "🇧🇷 Brazil",
    "China": "🇨🇳 China",
    "Russia": "🇷🇺 Russia",
    "Sweden": "🇸🇪 Sweden"
}

# Nombre del archivo de checkpoint para guardar progreso
CHECKPOINT_FILE = "datos_generados/country_enrichment_checkpoint.json"

def scrape_imdb_for_countries(imdb_id):
    """Extrae información de los países de una película en IMDb."""
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
            if header and ("Countries of origin" in header.text or "Country of origin" in header.text or "País de origen" in header.text):
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

def save_checkpoint(processed_ids):
    """Guarda un checkpoint de los IDs ya procesados."""
    directory = os.path.dirname(CHECKPOINT_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({"processed_ids": list(processed_ids)}, f)
    
    print(f"✅ Checkpoint guardado: {len(processed_ids)} películas procesadas")

def load_checkpoint():
    """Carga el checkpoint de IDs procesados."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get("processed_ids", []))
    return set()

def enrich_countries(input_file, output_file):
    """
    Enriquece los datos de países de las películas utilizando IMDb.
    
    Args:
        input_file (str): Ruta al archivo Excel con los datos de películas
        output_file (str): Ruta donde guardar el archivo Excel enriquecido
    """
    print(f"📊 Cargando archivo '{input_file}'...")
    df = pd.read_excel(input_file)
    
    # Crear columna country_expanded si no existe
    if 'country_expanded' not in df.columns:
        df['country_expanded'] = df['country_esp_fra_usa'].copy()
    
    # Cargar checkpoint de IDs ya procesados
    processed_ids = load_checkpoint()
    
    # Contar películas que necesitan ser procesadas
    need_processing = df[
        (df['imdb_id'].notna()) & 
        (df['imdb_id'] != "") & 
        (~df['imdb_id'].isin(processed_ids)) &
        (
            (df['country_expanded'].isna()) | 
            (df['country_expanded'] == "") |
            # También procesamos películas con solo algunos países (para añadir más si es posible)
            (df['country_expanded'].str.count(',') < 1)
        )
    ]
    
    total_to_process = len(need_processing)
    print(f"🎬 Total de películas a procesar: {total_to_process}")
    print(f"📌 Películas ya procesadas anteriormente: {len(processed_ids)}")
    
    # Preguntar al usuario si quiere continuar
    if total_to_process > 0:
        # Procesar cada película con ID de IMDb pero sin datos completos de país
        progress_bar = tqdm(total=total_to_process, desc="Procesando películas")
        
        save_interval = max(1, min(50, total_to_process // 10))  # Guardar cada 10% del progreso
        count = 0
        
        for i, row in need_processing.iterrows():
            imdb_id = row['imdb_id']
            
            # Obtener países de IMDb
            countries = scrape_imdb_for_countries(imdb_id)
            
            if countries:
                # Convertir a formato con emoji
                countries_with_emoji = []
                for country in countries:
                    for target, emoji_name in COUNTRY_EMOJIS.items():
                        if target in country:
                            countries_with_emoji.append(emoji_name)
                            break
                
                # Si encontramos países con emoji, actualizar
                if countries_with_emoji:
                    # Si ya había datos, combinar
                    if pd.notna(df.at[i, 'country_expanded']) and df.at[i, 'country_expanded'] != "":
                        existing = df.at[i, 'country_expanded'].split(', ')
                        combined = list(set(existing + countries_with_emoji))
                        df.at[i, 'country_expanded'] = ", ".join(combined)
                    else:
                        df.at[i, 'country_expanded'] = ", ".join(countries_with_emoji)
                    
                    # Mostrar resultados
                    tqdm.write(f"✅ {row['title']} ({row['year']}): {', '.join(countries)}")
                    tqdm.write(f"   → Con emoji: {df.at[i, 'country_expanded']}")
                else:
                    tqdm.write(f"⚠️ {row['title']}: No se encontraron coincidencias de países en la lista de países objetivo")
            else:
                tqdm.write(f"❌ {row['title']}: No se encontraron datos de países")
            
            # Marcar como procesado
            processed_ids.add(imdb_id)
            
            # Actualizar la barra de progreso
            progress_bar.update(1)
            count += 1
            
            # Guardar checkpoint y datos intermedios
            if count % save_interval == 0:
                save_checkpoint(processed_ids)
                df.to_excel(output_file, index=False)
                tqdm.write(f"💾 Guardando progreso intermedio ({count}/{total_to_process})")
            
            # Pausa para no sobrecargar el servidor
            time.sleep(1)
        
        progress_bar.close()
    
    # Guardar resultados finales
    save_checkpoint(processed_ids)
    df.to_excel(output_file, index=False)
    print(f"\n✅ Proceso completado. Datos guardados en '{output_file}'")
    
    # Mostrar estadísticas finales
    total_with_countries = df['country_expanded'].notna().sum()
    print(f"\n📊 Estadísticas finales:")
    print(f"   - Total de películas: {len(df)}")
    print(f"   - Películas con datos de país: {total_with_countries} ({total_with_countries/len(df)*100:.1f}%)")
    
    # Contar películas por país
    if total_with_countries > 0:
        country_counts = {}
        for country_list in df['country_expanded'].dropna():
            for country in country_list.split(', '):
                country_counts[country] = country_counts.get(country, 0) + 1
        
        print("\n🌍 Películas por país:")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {country}: {count}")

def main():
    """Función principal para enriquecer los datos de países."""
    try:
        # Obtener la ruta del directorio donde está el script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Definir rutas relativas basadas en el directorio del script
        input_file = os.path.join(script_dir, "datos_generados/cannes_con_imdb.xlsx")
        output_file = os.path.join(script_dir, "datos_generados/cannes_final.xlsx")

        # Enriquecer los datos
        enrich_countries(input_file, output_file)
        
    except Exception as e:
        print(f"\n❌ Error en el procesamiento: {e}")

if __name__ == "__main__":
    main()
