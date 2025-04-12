# pendiente de hacer: necesito el segundo dataset
# Cargar ambos
df_no = pd.read_excel("datos_generados/cannes_no_oficiales_con_paises.xlsx")
df_of = pd.read_excel("datos_generados/cannes_oficial.xlsx")

# Añadir tipo de sección
df_no["Tipo"] = "No oficiales"
df_of["Tipo"] = "Sección Oficial"

# Unir
df_union = pd.concat([df_no, df_of])

# Agrupar
df_grouped = df_union.groupby(["Año", "Tipo"])[["España", "Francia", "EEUU"]].sum().reset_index()
df_melted = df_grouped.melt(id_vars=["Año", "Tipo"], var_name="País", value_name="Nº películas")

# Gráfico
fig = px.line(
    df_melted,
    x="Año",
    y="Nº películas",
    color="País",
    line_dash="Tipo",
    title="Comparativa entre Sección Oficial y Secciones No Oficiales",
    markers=True
)

fig.update_layout(template="plotly_white")

fig.show()
