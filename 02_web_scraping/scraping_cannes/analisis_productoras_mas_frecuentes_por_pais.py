import pandas as pd
from collections import Counter

# Cargar el Excel generado anteriormente
df = pd.read_excel("datos_generados/cannes_oficial_wiki_con_productoras.xlsx")

# Nos aseguramos de que no haya nulos
df = df[df["productoras"].notna() & df["country_esp_fra_usa"].notna()].copy()

# Normalizamos los nombres de país
df["pais"] = df["country_esp_fra_usa"].map({
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
})

# Eliminamos entradas sin país relevante
df = df[df["pais"].notna()]

# Dividimos las productoras en listas
df["productoras_lista"] = df["productoras"].str.split(",\\s*")

# Preparamos estructura para el conteo
resultados = []

for pais in ["España", "Francia", "EEUU"]:
    todas = []
    for items in df[df["pais"] == pais]["productoras_lista"]:
        todas.extend(items)
    
    top = Counter(todas).most_common(10)
    resultados.extend([{"País": pais, "Productora": p[0], "Apariciones": p[1]} for p in top])

# Crear DataFrame con el top por país
df_top = pd.DataFrame(resultados)

# Mostrar resultados
print("\n🏆 TOP 10 PRODUCTORAS POR PAÍS EN LA SECCIÓN OFICIAL (WIKIPEDIA):\n")
for pais in df_top["País"].unique():
    print(f"\n📍 {pais}")
    print(df_top[df_top["País"] == pais][["Productora", "Apariciones"]].to_string(index=False))

# Guardar como Excel adicional si lo deseas
df_top.to_excel("top_productoras_por_pais.xlsx", index=False)
print("\n✅ Archivo guardado: 'top_productoras_por_pais.xlsx'")
