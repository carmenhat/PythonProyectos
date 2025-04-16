
### 1. **`scrapear_para_productoras.py`**
#### 📝 **Qué hace**
- Extrae datos **básicos de Wikipedia** sobre películas de Cannes (2015-2023)
- Incluye: título, director, países y productoras (si están en tablas de Wikipedia)
- Genera enlaces a fichas de películas en Wikipedia
- Identifica banderas de España/Francia/EEUU

#### 🎯 **Salida**  
`cannes_base.xlsx`

#### 💣 **Puntos complejos**  
- **Estructura variable** de tablas en Wikipedia (requiere lógica flexible)
- **Problema detectado**:  
  ```python
  COUNTRIES_LIST = [...]  # Definida pero no usada
  # En su lugar usa lista hardcodeada en el loop (línea 56)
  ```

| Archivo                      | Fuente     | Datos Obtenidos               | Fiabilidad | Complejidad |
|------------------------------|------------|--------------------------------|------------|-------------|
| `scrapear_para_productoras.py` | Wikipedia  | Datos básicos + enlaces        | Alta       | Media       |


