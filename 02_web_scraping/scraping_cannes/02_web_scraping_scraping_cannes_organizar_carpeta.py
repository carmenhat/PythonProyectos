import os
import shutil

# Directorio raíz del proyecto
directorio_raiz = "02_web_scraping/scraping_cannes"

# Subcarpetas para organizar los archivos
carpetas = {
    "documentación": ["README.md", "temas_pendientes.md", "instrucciones_para_analizar_web.md"],
    "scripts_finalizados": ["productoras.py", "nuevo_intento_productoras.py"],
    "scripts_incompletos": ["no_vale_scrape_cannes_no_oficiales.py"],
    "visualizaciones": ["graficos_barras.html", "evolucion_paises.html", "proporcion_paises.png"],
    "notebook": ["proyecto_cannes.ipynb"],
    "datos_generados": ["cannes_oficial.xlsx", "cannes_no_oficiales_con_paises.xlsx", "cannes_oficial_wiki_con_productoras.xlsx"]
}

# Crear carpetas si no existen
for carpeta in carpetas.keys():
    ruta_carpeta = os.path.join(directorio_raiz, carpeta)
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

# Mover archivos a sus carpetas correspondientes
for carpeta, archivos in carpetas.items():
    for archivo in archivos:
        origen = os.path.join(directorio_raiz, archivo)
        destino = os.path.join(directorio_raiz, carpeta, archivo)
        if os.path.exists(origen):
            shutil.move(origen, destino)
            print(f"Movido: {archivo} -> {carpeta}")

print("Organización completada.")