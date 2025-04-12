from pathlib import Path
import json

# Crear un notebook para analizar el top de productoras por país
notebook_productoras = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 🏆 Top de Productoras por País en el Festival de Cannes\n",
                "\n",
                "Este notebook extrae y analiza las productoras más frecuentes en las secciones **oficial** y **no oficiales** del Festival de Cannes entre 2015 y 2024.\n",
                "El objetivo es identificar las empresas que más han participado en películas de España, Francia y EEUU."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "from collections import Counter\n",
                "import plotly.express as px\n",
                "\n",
                "# Cargar ambos datasets\n",
                "df_no = pd.read_excel(\"cannes_no_oficiales_con_paises.xlsx\")\n",
                "df_of = pd.read_excel(\"cannes_oficial.xlsx\")\n",
                "\n",
                "# Unir ambos\n",
                "df_total = pd.concat([df_no, df_of], ignore_index=True)\n",
                "\n",
                "# Filtrar solo las películas con productoras y país objetivo\n",
                "df_filtrado = df_total[df_total[\"Productoras\"].notna()].copy()\n",
                "df_filtrado = df_filtrado[df_filtrado[[\"España\", \"Francia\", \"EEUU\"]].any(axis=1)]\n",
                "\n",
                "# Expandir productoras\n",
                "df_filtrado[\"Productoras lista\"] = df_filtrado[\"Productoras\"].str.split(\", \")\n",
                "\n",
                "# Función para contar top productoras por país\n",
                "def top_productoras(df, pais_col, nombre_pais, top_n=10):\n",
                "    todas = []\n",
                "    for _, row in df[df[pais_col]].iterrows():\n",
                "        todas.extend(row[\"Productoras lista\"])\n",
                "    counter = Counter(todas)\n",
                "    top = counter.most_common(top_n)\n",
                "    return pd.DataFrame(top, columns=[\"Productora\", \"Nº Películas\"]).assign(País=nombre_pais)\n",
                "\n",
                "# Obtener top\n",
                "top_esp = top_productoras(df_filtrado, \"España\", \"España\")\n",
                "top_fra = top_productoras(df_filtrado, \"Francia\", \"Francia\")\n",
                "top_usa = top_productoras(df_filtrado, \"EEUU\", \"EEUU\")\n",
                "\n",
                "# Unir\n",
                "df_top = pd.concat([top_esp, top_fra, top_usa], ignore_index=True)\n",
                "\n",
                "# Gráfico\n",
                "fig = px.bar(\n",
                "    df_top,\n",
                "    x=\"Nº Películas\",\n",
                "    y=\"Productora\",\n",
                "    color=\"País\",\n",
                "    orientation=\"h\",\n",
                "    facet_col=\"País\",\n",
                "    title=\"Top 10 Productoras por País en Cannes (Sección Oficial + No Oficiales)\",\n",
                "    height=600\n",
                ")\n",
                "\n",
                "fig.update_layout(template=\"plotly_white\", yaxis={'categoryorder':'total ascending'})\n",
                "fig.show()"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.9"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Guardar el notebook
notebook_path = Path("/mnt/data/cannes_top_productoras.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook_productoras, f)

notebook_path
