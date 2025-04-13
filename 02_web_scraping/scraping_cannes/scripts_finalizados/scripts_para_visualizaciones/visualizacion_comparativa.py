import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# este script visualiza la participación de España, Francia y EEUU en las secciones oficiales de Cannes entre 2015 y 2024
# Obtener la ruta del directorio donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "datos_generados/cannes_seccion_oficial_wiki_con_paises_y_enlaces.xlsx")

# Cargar el Excel
df = pd.read_excel(file_path)

# Verificar las columnas del DataFrame
print("Columnas del DataFrame:", df.columns)

# Verificar los valores únicos en 'country_esp_fra_usa'
print("Valores únicos en 'country_esp_fra_usa':", df["country_esp_fra_usa"].unique())

# Procesar la columna 'country_esp_fra_usa' para contar películas por país
df_countries = df["country_esp_fra_usa"].str.get_dummies(sep=",")
df_countries["year"] = df["year"]

# Renombrar columnas para incluir las banderas
column_mapping = {
    "🇪🇸 Spain": "España",
    "🇫🇷 France": "Francia",
    "🇺🇸 USA": "EEUU"
}
df_countries.rename(columns=column_mapping, inplace=True)

# Verificar las columnas generadas
print("Columnas generadas en df_countries:", df_countries.columns)

# Agrupar por año y país
df_total = df_countries.groupby("year")[["España", "Francia", "EEUU"]].sum().reset_index()

# Transformar formato para seaborn
df_melt = df_total.melt(id_vars="year", var_name="País", value_name="Número de películas")

# Visualización
plt.figure(figsize=(10, 6))
sns.set(style="whitegrid")
sns.lineplot(data=df_melt, x="year", y="Número de películas", hue="País", marker="o", linewidth=2.5)

plt.title("Participación de España, Francia y EEUU en secciones oficiales de Cannes (2015–2024)", fontsize=14)
plt.xlabel("Año")
plt.ylabel("Número de películas")
plt.legend(title="País")
plt.tight_layout()
plt.show()
