import pandas as pd
import plotly.express as px
from collections import Counter
from pathlib import Path
# estoy automatizando el proceso de generación del gráfico interactivo: voy a crear un script que lo haga automáticamente
# y lo guardaré en el directorio actual
# así puedo crear más ficheros de este tipo y no perder el tiempo
# Importar los datos
# Cambia la ruta del archivo según sea necesario

# Definir la ruta relativa para el archivo de datos
relative_path = Path("..") / "datos_generados" / "cannes_oficial_wiki_con_productoras.xlsx"
file_path = Path(__file__).parent.parent.parent / "datos_generados" / "cannes_oficial_wiki_con_productoras.xlsx"
print(f"Ruta del archivo: {file_path.resolve()}")

# Ensure the file exists before reading
if not file_path.exists():
    raise FileNotFoundError(f"El archivo no se encuentra en la ruta especificada: {file_path.resolve()}")

df = pd.read_excel(file_path)

# Filtrar y preparar los datos
df = df[df["productoras"].notna() & df["country_esp_fra_usa"].notna()].copy()

# Normalizar países
df["pais"] = df["country_esp_fra_usa"].map({
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
})

df = df[df["pais"].notna()]
df["productoras_lista"] = df["productoras"].str.split(r",\s*")

# Extraer top 10 por país
resultados = []

for pais in ["España", "Francia", "EEUU"]:
    todas = []
    for items in df[df["pais"] == pais]["productoras_lista"]:
        todas.extend(items)
    
    top = Counter(todas).most_common(10)
    resultados.extend([{"País": pais, "Productora": p[0], "Apariciones": p[1]} for p in top])

df_top = pd.DataFrame(resultados)

# Crear gráfico interactivo
fig = px.bar(
    df_top,
    x="Apariciones",
    y="Productora",
    color="País",
    facet_col="País",
    title="Top 10 Productoras por País en la Sección Oficial (Wikipedia)",
    orientation="h",
    height=700
)

fig.update_layout(template="plotly_white", yaxis={"categoryorder": "total ascending"})
fig.show()
# Ensure the directory exists before saving the file
output_dir = Path("visualizaciones")
output_dir.mkdir(parents=True, exist_ok=True)
fig.write_html(output_dir / "top_productoras.html")
print("✅ Gráfico guardado como 'visualizaciones/top_productoras.html'")
