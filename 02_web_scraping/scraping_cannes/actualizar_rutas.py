import os
import re

# Configuración
directorio_raiz = "02_web_scraping"
nuevas_rutas = {
    "productoras.py": "scripts_finalizados/productoras.py",
    "nuevo_intento_productoras.py": "scripts_finalizados/nuevo_intento_productoras.py",
    "no_vale_scrape_cannes_no_oficiales.py": "scripts_incompletos/no_vale_scrape_cannes_no_oficiales.py",
    "cannes_oficial.xlsx": "datos_generados/cannes_oficial.xlsx",
    "cannes_no_oficiales_con_paises.xlsx": "datos_generados/cannes_no_oficiales_con_paises.xlsx",
    "cannes_oficial_wiki_con_productoras.xlsx": "datos_generados/cannes_oficial_wiki_con_productoras.xlsx"
}

# Buscar y reemplazar rutas en los scripts
def actualizar_rutas(directorio, nuevas_rutas):
    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(".py"):
                ruta_completa = os.path.join(root, file)
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    contenido = f.read()

                # Reemplazar rutas
                for ruta_antigua, ruta_nueva in nuevas_rutas.items():
                    contenido = re.sub(
                        rf"(['\"]){ruta_antigua}\1",  # Ruta antigua
                        rf"\1{ruta_nueva}\1",         # Ruta nueva
                        contenido
                    )

                # Guardar cambios
                with open(ruta_completa, "w", encoding="utf-8") as f:
                    f.write(contenido)
                print(f"Rutas actualizadas en: {ruta_completa}")

actualizar_rutas(directorio_raiz, nuevas_rutas)