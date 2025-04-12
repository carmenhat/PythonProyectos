import re
import pandas as pd
from rapidfuzz import fuzz, process
from collections import defaultdict

class ProductionCompanyNormalizer:
    """Clase para normalizar y desambiguar nombres de productoras."""
    
    def __init__(self):
        # Sufijos comunes de nombres de empresas
        self.suffixes = [
            r'\bInc\.?$', r'\bLLC$', r'\bLtd\.?$', r'\bGmbH$', r'\bS\.A\.?$', 
            r'\bS\.L\.?$', r'\bS\.p\.A\.?$', r'\bCo\.?$', r'\bCompany$',
            r'\bCorp\.?$', r'\bCorporation$', r'\bProductions?$', r'\bProd\.?$',
            r'\bPictures?$', r'\bPics?\.?$', r'\bStudio(?:s)?$', r'\bFilms?$',
            r'\bEntertainment$', r'\bEnter\.?$', r'\bMedia$', r'\bFictures?$'
        ]
        
        # Palabras a ignorar para comparaciones
        self.ignore_words = [
            'the', 'and', 'of', 'de', 'la', 'el', 'les', 'das', 'der', 'die'
        ]
        
        # Diccionario de alias conocidos (nombre alternativo -> nombre canónico)
        self.known_aliases = {
            'fox': '20th Century Fox',
            'fox searchlight': 'Searchlight Pictures',
            'searchlight': 'Searchlight Pictures',
            'warner': 'Warner Bros.',
            'warner brothers': 'Warner Bros.',
            'wb': 'Warner Bros.',
            'disney': 'Walt Disney Pictures',
            'walt disney': 'Walt Disney Pictures',
            'sony': 'Sony Pictures',
            'columbia': 'Columbia Pictures',
            'universal': 'Universal Pictures',
            'paramount': 'Paramount Pictures',
            'gaumont': 'Gaumont Film Company',
            'pathe': 'Pathé',
            'pathe films': 'Pathé',
            'canal+': 'Canal+',
            'canal plus': 'Canal+',
            'tf1': 'TF1 Films Production',
            'france televisions': 'France Télévisions',
            'arte': 'Arte France Cinéma',
            'arte france': 'Arte France Cinéma',
            'mgm': 'Metro-Goldwyn-Mayer',
            'metro goldwyn mayer': 'Metro-Goldwyn-Mayer',
            'focus': 'Focus Features',
            'focus features': 'Focus Features',
            'new line': 'New Line Cinema',
            'newline': 'New Line Cinema',
            'miramax': 'Miramax Films',
            'lionsgate': 'Lionsgate Films',
            'lions gate': 'Lionsgate Films',
            'wild bunch': 'Wild Bunch',
            'mk2': 'MK2 Films',
            'mk2 films': 'MK2 Films',
            'a24': 'A24',
            'netflix': 'Netflix',
            'amazon': 'Amazon Studios',
            'amazon studios': 'Amazon Studios',
            'apple': 'Apple TV+',
            'apple tv': 'Apple TV+',
            'apple tv+': 'Apple TV+',
            'hbo': 'HBO Films',
            'hbo films': 'HBO Films',
            'bbc': 'BBC Films',
            'bbc films': 'BBC Films',
        }
        
        # Cache para resultados de normalización
        self.normalization_cache = {}
    
    def strip_suffix(self, name):
        """Elimina sufijos comunes de empresas."""
        original = name
        for suffix in self.suffixes:
            name = re.sub(suffix, '', name, flags=re.IGNORECASE)
        
        # Si quitamos un sufijo, eliminar espacio final
        if original != name:
            name = name.rstrip()
            
        return name
    
    def normalize(self, name):
        """Normaliza un nombre de productora."""
        if not isinstance(name, str) or not name.strip():
            return ""
            
        # Revisar cache
        if name in self.normalization_cache:
            return self.normalization_cache[name]
            
        # Convertir a minúsculas
        normalized = name.lower()
        
        # Verificar alias conocidos
        for alias, canonical in self.known_aliases.items():
            if normalized == alias or normalized.startswith(f"{alias} "):
                self.normalization_cache[name] = canonical
                return canonical
                
        # Eliminar caracteres no alfanuméricos
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Eliminar sufijos corporativos
        normalized = self.strip_suffix(normalized)
        
        # Eliminar espacios extras
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Guardar en cache y devolver el nombre original para preservar formato
        self.normalization_cache[name] = name
        return name
    
    def find_canonical_name(self, names):
        """
        Identifica el nombre canónico de una lista de variantes del mismo nombre.
        Prioriza nombres más largos y evita abreviaturas.
        """
        if not names:
            return ""
            
        if len(names) == 1:
            return names[0]
            
        # Ordenar por prioridad: 
        # 1. Alias conocidos
        # 2. Longitud (preferir nombres completos a abreviaturas)
        # 3. Nombres que no son solo mayúsculas (evitar acrónimos)
        
        # Primero comprobar si alguno es alias conocido
        for name in names:
            normalized = name.lower()
            if normalized in self.known_aliases.values():
                return name
                
        # Luego ordenar por criterios de calidad
        scored_names = []
        for name in names:
            score = 0
            # Preferir nombres más largos (pero no demasiado)
            length = len(name)
            if length > 3 and length < 30:
                score += min(length / 3, 8)
            
            # Penalizar nombres todo en mayúsculas (posibles acrónimos)
            if name.isupper() and len(name) > 2:
                score -= 5
                
            # Bonificar nombres con mayúsculas/minúsculas mezcladas (formato correcto)
            if not name.isupper() and not name.islower() and any(c.isupper() for c in name):
                score += 3
                
            # Penalizar nombres muy cortos
            if len(name) < 3:
                score -= 5
                
            scored_names.append((score, name))
            
        # Devolver el mejor
        return sorted(scored_names, key=lambda x: x[0], reverse=True)[0][1]
    
    def cluster_similar_companies(self, company_list, threshold=85):
        """
        Agrupa nombres de compañías similares usando fuzzy matching.
        Devuelve un diccionario {nombre_canónico: [variantes]}
        """
        if not company_list:
            return {}
            
        # Normalizar primero
        normalized_companies = {company: self.normalize(company) for company in company_list if company}
        
        # Agrupar por similitud
        clusters = defaultdict(list)
        processed = set()
        
        # Procesar primero los alias conocidos
        for company, normalized in normalized_companies.items():
            norm_lower = normalized.lower()
            if norm_lower in self.known_aliases:
                canonical = self.known_aliases[norm_lower]
                clusters[canonical].append(company)
                processed.add(company)
        
        # Procesar el resto
        companies = [c for c in company_list if c not in processed]
        
        while companies:
            current = companies.pop(0)
            if current in processed:
                continue
                
            # Crear un nuevo cluster con este elemento
            cluster = [current]
            processed.add(current)
            
            # Buscar similares entre los no procesados
            i = 0
            while i < len(companies):
                candidate = companies[i]
                
                # Calcular similitud
                similarity = fuzz.ratio(
                    self.normalize(current).lower(), 
                    self.normalize(candidate).lower()
                )
                
                if similarity >= threshold:
                    cluster.append(candidate)
                    processed.add(candidate)
                    companies.pop(i)
                else:
                    i += 1
            
            # Asignar nombre canónico
            canonical = self.find_canonical_name(cluster)
            clusters[canonical].extend(cluster)
        
        return clusters

def process_production_companies(excel_file):
    """
    Procesa un archivo Excel con datos de productoras,
    normaliza y agrupa compañías similares.
    """
    try:
        # Cargar el Excel
        df = pd.read_excel(excel_file)
        
        # Columna donde buscar nombres de productoras
        company_columns = [
            'productoras_consolidadas', 'consolidated_production_companies',
            'productoras', 'production_company', 'imdb_production_companies', 
            'tmdb_production_companies'
        ]
        
        # Usar la primera columna disponible
        company_col = None
        for col in company_columns:
            if col in df.columns:
                company_col = col
                break
                
        if not company_col:
            print("❌ No se encontró ninguna columna con datos de productoras")
            return None
        
        # Extraer todos los nombres de compañías
        all_companies = set()
        for value in df[company_col].dropna():
            if isinstance(value, str):
                companies = [c.strip() for c in value.split(',')]
                all_companies.update([c for c in companies if c])
        
        print(f"🔍 Encontradas {len(all_companies)} productoras únicas")
        
        # Normalizar y agrupar
        normalizer = ProductionCompanyNormalizer()
        clusters = normalizer.cluster_similar_companies(all_companies)
        
        print(f"✅ Productoras agrupadas en {len(clusters)} entidades únicas")
        
        # Crear un mapa para reemplazos
        replacement_map = {}
        for canonical, variants in clusters.items():
            for variant in variants:
                replacement_map[variant] = canonical
        
        # Crear nueva columna normalizada
        df[f"{company_col}_normalized"] = None
        
        # Aplicar normalización
        for i, row in df.iterrows():
            if pd.isna(row[company_col]):
                continue
                
            companies = [c.strip() for c in str(row[company_col]).split(',')]
            normalized_companies = [replacement_map.get(c, c) for c in companies if c]
            
            # Eliminar duplicados
            normalized_companies = list(dict.fromkeys(normalized_companies))
            
            df.at[i, f"{company_col}_normalized"] = ", ".join(normalized_companies)
        
        return df
        
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        return None

# Esta función se puede usar para probar la normalización de manera independiente
if __name__ == "__main__":
    test_companies = [
        "Warner Bros.", 
        "Warner Brothers Pictures", 
        "WB Entertainment",
        "Columbia Pictures", 
        "Columbia", 
        "Sony Pictures",
        "Fox Searchlight Pictures",
        "Searchlight",
        "Canal+"
    ]
    
    normalizer = ProductionCompanyNormalizer()
    clusters = normalizer.cluster_similar_companies(test_companies)
    
    print("Agrupaciones de productoras similares:")
    for canonical, variants in clusters.items():
        print(f"- {canonical}: {', '.join(variants)}")
