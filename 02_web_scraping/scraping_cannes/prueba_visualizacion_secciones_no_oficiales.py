# antes necesito crear el dataframe df_peliculas

import seaborn as sns
import matplotlib.pyplot as plt

# Total de películas por país y año
df_total = df_peliculas.groupby(["Año"])[["España", "Francia", "EEUU"]].sum().reset_index()

# Melt para plot
df_melt = df_total.melt(id_vars="Año", var_name="País", value_name="Nº de películas")

plt.figure(figsize=(10,6))
sns.lineplot(data=df_melt, x="Año", y="Nº de películas", hue="País", marker="o")
plt.title("Participación de España, Francia y EEUU en secciones no oficiales de Cannes")
plt.ylabel("Número de películas")
plt.xlabel("Año")
plt.grid(True)
plt.tight_layout()
plt.show()
