import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
# creando un script para extraer los datos de las productoras de las películas de la sección oficial del festival de cannes
# de los años 2015 a 2023 de la wikipedia (parece que en 2024 no encuentro datos)
# Importar las librerías necesarias
# crea el excel cannes_base.xlsx

YEARS = list(range(2015, 2024))
BASE_WIKI_URL = "https://en.wikipedia.org/wiki/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/112.0.0.0 Safari/537.36"
}

# Lista de países que nos interesa identificar
COUNTRIES_LIST = ['Spain', 'España', 'France', 'Francia', 'United States', 'USA', 'Estados Unidos']
# falta añadir el resto de países que me interesaban también (y que pensé después)
data = []

for year in YEARS:
    print(f"\nProcesando {year}...")
    wiki_title = f"{year}_Cannes_Film_Festival"
    url = BASE_WIKI_URL.format(wiki_title)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
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
        if not any("film" in h or "title" in h for h in headers):
            continue

        tablas_validas += 1

        for row in table.find_all("tr")[1:]:
            cols = row.find_all(["td", "th"])
            if len(cols) < 2:
                continue

            print("Encabezados:", headers)
            print("Columnas de la fila:", [col.get_text(strip=True) for col in cols])

            film = cols[0].get_text(strip=True)
            director = cols[1].get_text(strip=True) if len(cols) > 1 else ""

            countries = ""
            for i, h in enumerate(headers):
                if "country" in h and i < len(cols):
                    countries = cols[i].get_text(strip=True)

            # Verificamos si el país pertenece a España, Francia o USA (habría que expandir lista de países)
            country_flag = ""
            if any(country in countries for country in ['Spain', 'España']):
                country_flag = '🇪🇸 Spain'
            elif any(country in countries for country in ['France', 'Francia']):
                country_flag = '🇫🇷 France'
            elif any(country in countries for country in ['United States', 'USA', 'Estados Unidos']):
                country_flag = '🇺🇸 USA'

            # Extraer productoras si existe una columna relevante
            production_company = ""
            for i, h in enumerate(headers):
                if ("production" in h or "studio" in h) and i < len(cols):
                    production_company = cols[i].get_text(strip=True)

            # Enlace a la ficha de la película en Wikipedia
            film_url = film.replace(" ", "_")
            wiki_film_url = f"https://en.wikipedia.org/wiki/{film_url}"

            data.append({
                "year": year,
                "title": film,
                "director": director,
                "countries": countries,
                "section": "Official Selection (Wikipedia)",
                "country_esp_fra_usa": country_flag,
                "production_company": production_company,
                "film_wiki_url": wiki_film_url
            })

    if tablas_validas == 0:
        print(f"⚠️ No se encontró ninguna tabla con títulos de películas en {url}")

    time.sleep(1)

films_df = pd.DataFrame(data)
films_df.to_excel("../datos_generados/cannes_base.xlsx", index=False)
print("\n✅ Datos guardados en '../datos_generados/cannes_base.xlsx'")
