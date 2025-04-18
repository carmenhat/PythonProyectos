# 🎬 Cannes Film Festival Analysis (2015-2023)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A data analysis project that tracks films from the Cannes Film Festival's official selections from 2015 to 2023, with a focus on production companies and country of origin analysis.

![Cannes Film Festival](https://via.placeholder.com/800x400?text=Cannes+Film+Festival+Analysis)

## 📋 Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technical Requirements](#technical-requirements)
4. [Project Structure](#project-structure)
5. [Data Collection Workflow](#data-collection-workflow)
6. [Dashboard & Visualizations](#dashboard--visualizations)
7. [Installation & Usage](#installation--usage)
8. [Challenges & Lessons Learned](#challenges--lessons-learned)
9. [Future Development](#future-development)
10. [Contributing](#contributing)
11. [License](#license)

## 🌟 Introduction

This project collects and analyzes data about films presented in the official selections of the Cannes Film Festival from 2015 to 2023. The primary goals are to:

- Identify the country of origin for each film (with special focus on Spain, France, and the United States)
- Analyze production company involvement and partnerships
- Create an interactive dashboard for exploring the collected data
- Identify trends in international film production within the festival context

The project was developed for educational purposes to practice web scraping, data cleaning, and visualization techniques.

## ✨ Features

- **Data Collection**: Automated scraping from Wikipedia and IMDb
- **Data Processing**: 
  - Country of origin identification with flag emojis
  - Production company name normalization and clustering
  - Comprehensive data consolidation
- **Interactive Dashboard**: Streamlit-based visualization of films, countries, and production companies
- **Analysis Tools**: Compare film production trends across countries and years

## 🛠️ Technical Requirements

### Languages
- Python 3.8+

### Libraries & Tools
- **Web Scraping**: 
  - BeautifulSoup4
  - Requests
- **Data Processing**:
  - Pandas
  - NumPy
  - Regular Expressions
- **Data Visualization**: 
  - Streamlit
  - Plotly / Matplotlib
- **Storage**: 
  - Excel (.xlsx) via openpyxl

### Custom Modules
- `company_normalizer.py`: Custom module for normalizing company names

## 📁 Project Structure

```
scraping_cannes/
├── cannes-scraper-unified.py      # Main script for data collection
├── company_normalizer.py          # Utility for normalizing company names
├── dashboard_cannes_mejorado.py   # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── README.md                      # This documentation file
└── datos_generados/
    └── cannes_dataset_unificado.xlsx  # Generated dataset
```

### Dataset Structure

The `cannes_dataset_unificado.xlsx` file contains the following columns:

| Column | Description |
|--------|-------------|
| year | Year of the film's premiere |
| title | Film title |
| director | Film director (pending processing) |
| countries | Countries involved in production |
| section | Festival section (currently unused) |
| country_emoji | Country flags with names |
| film_wiki_url | Wikipedia URL of the film |
| imdb_id | IMDb identifier code |
| imdb_production_companies | Production companies according to IMDb |
| imdb_countries | Countries according to IMDb |
| productoras_consolidadas | Consolidated production companies |
| productoras_normalizadas | Normalized production company names |

## 🔄 Data Collection Workflow

The data collection process follows these steps:

1. **Initial Extraction**: 
   - Extract film titles and basic information from Wikipedia's Cannes Film Festival pages
   - Gather production company information from individual film pages on Wikipedia

2. **Data Enrichment**:
   - Search for each film on IMDb to retrieve its unique identifier
   - Extract additional production company information and country of origin from IMDb
   - Add country flag emojis for better visualization

3. **Data Processing**:
   - Normalize production company names to address spelling variations
   - Cluster similar company names to identify the same companies with different spellings
   - Consolidate all sources of information into a single dataset

4. **Data Storage**:
   - Save the processed data to an Excel file for further analysis and visualization

## 📊 Dashboard & Visualizations

The project includes an interactive dashboard built with Streamlit (`dashboard_cannes_mejorado.py`) featuring:

- Film listings with filtering options
- Country of origin analysis and comparisons
- Production company participation metrics
- Year-by-year analysis of trends
- Special focus on Spanish film industry participation

![Dashboard Screenshot](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

## 🚀 Installation & Usage

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/carmenhat/PythonProyectos.git
   cd PythonProyectos/02_web_scraping/scraping_cannes
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Data Collection

Run the unified scraper to collect film data:
```bash
python cannes-scraper-unified.py
```

This will generate the dataset in `datos_generados/cannes_dataset_unificado.xlsx`.

### Running the Dashboard

Launch the Streamlit dashboard:
```bash
streamlit run dashboard_cannes_mejorado.py
```

The dashboard will be accessible at http://localhost:8501 in your web browser.

## 💡 Challenges & Lessons Learned

### Scraping Challenges
- **Inconsistent Data**: Wikipedia and IMDb pages don't follow a consistent structure across all films
- **Rate Limiting**: Careful implementation of delays was necessary to avoid being blocked
- **Data Quality**: Several films had incomplete information requiring manual verification

### Data Processing Challenges
- **Company Name Variations**: The same production company often appeared with different spellings or formats
- **Missing Information**: Not all films had complete production information available
- **International Character Support**: Handling special characters from different languages

### Lessons Learned
- Web scraping requires robust error handling and adaptability to changing website structures
- Normalizing entity names is crucial for accurate analysis
- A step-by-step approach to data enrichment yields better results than trying to collect everything at once

## 🔮 Future Development

1. **Dashboard Enhancements**:
   - Add more interactive visualizations
   - Create specialized views for country-specific analysis
   - Implement data filtering capabilities

2. **Data Collection Improvements**:
   - Process director information for director-based analysis
   - Expand to include award information
   - Add film genre classification

3. **Technical Improvements**:
   - Refactor code into a more modular structure
   - Implement proper logging
   - Add automated tests
   - Create a data update mechanism for future festival editions

4. **Analysis Extensions**:
   - Compare with other major film festivals
   - Analyze director-producer relationships
   - Study the correlation between production companies and awards

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by [carmenhat](https://github.com/carmenhat) - Feel free to contact me for any questions or suggestions!
