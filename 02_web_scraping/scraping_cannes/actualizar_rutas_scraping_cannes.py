import os
import re

# Configuración
directorio_raiz = "02_web_scraping/scraping_cannes"
carpetas = {
    "excel": "datos_generados/",
    "visualizaciones": "visualizaciones/",
    "scripts_finalizados": "scripts_finalizados/",
    "scripts_incompletos": "scripts_incompletos/",
}

# Extensiones de archivos para clasificar
extensiones = {
    "excel": [".xlsx"],
    "visualizaciones": [".png", ".jpg", ".jpeg", ".svg", ".html"],
}

# Buscar y reemplazar rutas en los scripts
def actualizar_rutas(directorio, carpetas, extensiones):
    if not os.path.exists(directorio):
        print(f"⚠️ El directorio raíz '{directorio}' no existe. Verifica la configuración.")
        return

    rutas_actualizadas = 0
    scripts_procesados = 0

    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(".py"):
                ruta_completa = os.path.join(root, file)
                scripts_procesados += 1
                print(f"🔍 Procesando: {ruta_completa}")

                try:
                    with open(ruta_completa, "r", encoding="utf-8") as f:
                        contenido = f.read()
                except Exception as e:
                    print(f"⚠️ Error leyendo el archivo {ruta_completa}: {e}")
                    continue

                # Reemplazar rutas antiguas por nuevas
                contenido_original = contenido
                for tipo, carpeta_destino in carpetas.items():
                    for extension in extensiones.get(tipo, []):
                        contenido = re.sub(
                            rf"(['\"])([^'\"]+{extension})\1",  # Ruta antigua con extensión
                            rf"\1{os.path.join(carpeta_destino, r'\2')}\1",  # Ruta nueva
                            contenido
                        )

                # Si hubo cambios, guardar el archivo
                if contenido != contenido_original:
                    try:
                        with open(ruta_completa, "w", encoding="utf-8") as f:
                            f.write(contenido)
                        rutas_actualizadas += 1
                        print(f"✅ Rutas actualizadas en: {ruta_completa}")
                    except Exception as e:
                        print(f"⚠️ Error escribiendo en el archivo {ruta_completa}: {e}")

    print(f"📊 Resumen:")
    print(f"    - Scripts procesados: {scripts_procesados}")
    print(f"    - Rutas actualizadas: {rutas_actualizadas}")

if __name__ == "__main__":
    if not os.path.exists(directorio_raiz):
        print(f"⚠️ El directorio raíz '{directorio_raiz}' no existe. Verifica la configuración.")
    else:
        actualizar_rutas(directorio_raiz, carpetas, extensiones)