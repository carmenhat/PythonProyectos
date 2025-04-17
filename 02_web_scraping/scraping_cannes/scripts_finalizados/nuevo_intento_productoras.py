from pathlib import Path

# Este script busca las productoras de las películas en Wikipedia
# y las añade a un archivo Excel existente con la información de Cannes.
# Asegúrate de tener el archivo "datos_generados/cannes_wiki.xlsx" en la misma carpeta que este script
# o proporciona la ruta correcta al archivo.
# Este archivo debe contener las columnas "film_wiki_url" y "title".
# Si no tienes el archivo, puedes generarlo ejecutando el script "scrapear_para_productoras.py".
# Si no lo tienes, primero ejecuta el script "scrapear_para_productoras.py" para generarlo.
# genera el excel cannes oficial wiki con productoras que luego se usa para la visualización
# de las productoras más frecuentes por país.
# Este script es una continuación del anterior y se basa en el archivo generado por él.
# Asegúrate de tener las librerías necesarias instaladas:
# pip install pandas requests beautifulsoup4 openpyxl

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Cargar el archivo anterior
# Construir la ruta correcta a la carpeta datos_generados
input_dir = Path(__file__).parent.parent / "datos_generados"
input_file = input_dir / "cannes_wiki.xlsx"

# Verificar si el archivo existe
if not input_file.exists():
    raise FileNotFoundError(f"El archivo '{input_file.resolve()}' no existe. Asegúrate de generarlo primero.")

# Cargar el archivo Excel
df = pd.read_excel(input_file)

productoras = []

for i, row in df.iterrows():
    url = row["film_wiki_url"]
    print(f"🔎 Procesando {row['title']} ({row['year']})")

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ No se pudo acceder a {url}: {e}")
        productoras.append("")
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    infobox = soup.find("table", class_="infobox vevent")
    prod = ""

    if infobox:
        for row in infobox.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                label = th.get_text(strip=True).lower()
                if "production" in label or "studio" in label:
                    prod = td.get_text(separator=", ", strip=True)
                    break

    productoras.append(prod)
    time.sleep(1)

# Añadir la nueva columna
df["productoras"] = productoras

# Guardar resultado
# Crear el directorio si no existe
output_dir = Path("datos_generados")
output_dir.mkdir(parents=True, exist_ok=True)

# Guardar el archivo Excel
df.to_excel(output_dir / "cannes_wiki_enriquecido.xlsx", index=False)
print(f"✅ Archivo actualizado con productoras guardado como '{output_dir / 'cannes_wiki_enriquecido.xlsx'}'")



