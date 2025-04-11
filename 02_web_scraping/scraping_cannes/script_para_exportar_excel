import requests
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Paso 1: Obtener años desde la API
years_url = "https://www.festival-cannes.com/en/api/festival/years"
response = requests.get(years_url, headers=headers)
years_data = response.json()

# Últimos 10 años (o desde 2013 en adelante)
years = sorted([y['year'] for y in years_data if y['year'] >= 2013], reverse=True)

film_data = []

# Paso 2: Scraping de películas por año
for year in years:
    url = f"https://www.festival-cannes.com/en/api/films/selection/officialSelection?year={year}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"❌ Error al cargar {year}")
        continue

    films = r.json().get("films", [])

    for film in films:
        film_id = film.get("id")
        film_data.append({
            "Año": year,
            "Título": film.get("title", "").strip(),
            "Director": film.get("director", "").strip() if film.get("director") else "",
            "Duración": film.get("duration"),
            "Categoría": film.get("category", {}).get("label", ""),
            "Países": ", ".join([c["label"] for c in film.get("countries", [])]),
            "Enlace": f"https://www.festival-cannes.com/en/festival/films/{film_id}"
        })

    print(f"✅ Año {year} completado con {len(films)} películas")
    time.sleep(1)

# Paso 3: Convertir a DataFrame
df = pd.DataFrame(film_data)

# Paso 4: Guardar en Excel
nombre_archivo = "peliculas_cannes.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"\n🎉 Archivo guardado correctamente como {nombre_archivo}")
