import requests
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Identificadores de secciones no oficiales (basados en investigación previa o estimaciones)
#
secciones = {
    "Un Certain Regard": "un-certain-regard",
    "Out of Competition": "hors-competition",
    "Cinéfondation": "cinefondation",
    "Quinzaine des Réalisateurs": "quinzaine-des-realisateurs",  # Ojo: esta puede no estar en la API oficial
    "Semaine de la Critique": "semaine-de-la-critique"  # Ídem
}

# Años que quieres scrapear
años = list(range(2015, 2025))

# Lista para almacenar los datos
datos_peliculas = []

# Bucle por año y sección
for año in años:
    for nombre_seccion, id_seccion in secciones.items():
        url = f"https://www.festival-cannes.com/en/api/films/selection/{id_seccion}?year={año}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            peliculas = response.json().get("films", [])
            for pelicula in peliculas:
                paises = [c["label"] for c in pelicula.get("countries", [])]
                paises_str = ", ".join(paises)

                datos_peliculas.append({
                    "Año": año,
                    "Sección": nombre_seccion,
                    "Título": pelicula.get("title", "").strip(),
                    "Director": pelicula.get("director", "").strip() if pelicula.get("director") else "",
                    "Duración": pelicula.get("duration"),
                    "Categoría": pelicula.get("category", {}).get("label", ""),
                    "Países": paises_str,
                    "España": any(p.lower() in ["españa", "spain"] for p in paises),
                    "Francia": any(p.lower() in ["francia", "france"] for p in pais
