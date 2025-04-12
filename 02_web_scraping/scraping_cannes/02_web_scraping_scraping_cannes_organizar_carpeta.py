import os
import shutil

# Directorio raíz del proyecto
directorio_raiz = "02_web_scraping/scraping_cannes"

# Subcarpetas para organizar los archivos
carpetas = {
    "documentación": ["README.md", "temas_pendientes.md", "instrucciones_para_analizar_web.md"],
    "scripts_finalizados": ["scripts_finalizados/productoras.py", "scripts_finalizados/nuevo_intento_productoras.py"],
    "scripts_incompletos": ["scripts_incompletos/no_vale_scrape_cannes_no_oficiales.py"],
    "visualizaciones": [".html", ".png"],  # Busca archivos con estas extensiones
    "notebook": ["proyecto_cannes.ipynb"],
    "datos_generados": [".xlsx"]  # Busca archivos con extensión .xlsx
}

# Crear carpetas si no existen
for carpeta in carpetas.keys():
    ruta_carpeta = os.path.join(directorio_raiz, carpeta)
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

# Mover archivos a sus carpetas correspondientes
for carpeta, criterios in carpetas.items():
    for root, _, files in os.walk(directorio_raiz):
        for archivo in files:
            # Si el archivo coincide con un criterio (extensión o nombre exacto)
            if any(archivo.endswith(criterio) or archivo == criterio for criterio in criterios):
                origen = os.path.join(root, archivo)
                destino = os.path.join(directorio_raiz, carpeta, archivo)
                shutil.move(origen, destino)
                print(f"Movido: {archivo} -> {carpeta}")

print("Organización completada.")