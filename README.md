# 🌍 WorldPulse: Countries ETL + EDA Pipeline

An end-to-end data pipeline in Python that fetches data on ~250 countries from the
[REST Countries API](https://restcountries.com) (v5), cleans and validates it,
stores it in a SQLite database, and explores it with SQL, outlier detection and charts.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![pandas](https://img.shields.io/badge/pandas-data%20cleaning-150458)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063)
![SQLite](https://img.shields.io/badge/SQLite-database-003B57)
![matplotlib](https://img.shields.io/badge/matplotlib-charts-11557c)

---

## 📌 Overview

| Stage | File | What it does |
|-------|------|--------------|
| **Extract** | `extract.py` | Calls the API page by page (100 records per request) and saves the raw response to `data/raw/countries_raw.json` |
| **Transform** | `transform.py` | Flattens nested JSON, removes duplicates, fills missing values, computes `density`, and validates every record with Pydantic |
| **Load** | `load.py` | Writes the clean data to SQLite (`countries.db`, table `countries`) |
| **EDA** | `eda.py` | Runs SQL queries, flags outliers with the IQR method, and saves 6 charts and CSV summaries to `outputs/` |
| **Run all** | `main.py` | Runs Extract → Transform → Load → EDA in one command |

```
REST Countries API ──► extract.py ──► transform.py ──► load.py ──► eda.py
                          │               │               │           │
                   data/raw/*.json  rejected_records.log  countries.db  outputs/
```

## ✨ Features

- **Paginated API extraction** with clear error messages (for example when the API key is missing).
- **Data cleaning with pandas**: flattening nested JSON, dropping duplicates by country code, filling missing capitals and subregions with `"Unknown"`, safe numeric conversion.
- **Feature engineering**: population density (`population / area`).
- **Record validation with Pydantic**: invalid rows are rejected and logged in `data/rejected_records.log` instead of silently breaking the analysis.
- **SQL-based analysis** on SQLite: top countries, region totals, most and least crowded countries.
- **Outlier detection (IQR method)**: outliers are flagged in a `countries_flagged` table, never deleted.
- **6 ready-made charts** and 3 CSV reports.

## 🧰 Tech Stack

Python · requests · pandas · NumPy · Pydantic v2 · SQLite (`sqlite3`) · matplotlib

## 📁 Project Structure

```
.
├── main.py                 # runs the full pipeline
├── extract.py              # E: download data from the API
├── transform.py            # T: clean + validate data
├── load.py                 # L: save to SQLite
├── eda.py                  # SQL queries, outliers, charts
├── requirements.txt
├── countries.db            # SQLite database (generated)
├── data/
│   ├── raw/countries_raw.json     # unchanged API response (generated)
│   └── rejected_records.log       # records that failed validation (generated)
└── outputs/                # charts and CSV reports (generated)
    ├── 1_top10_population.png
    ├── 2_region_population.png
    ├── 3_region_density.png
    ├── 4_crowded_countries.png
    ├── 5_histogram_population.png
    ├── 6_boxplots.png
    ├── summary_table.csv
    ├── region_comparison.csv
    └── outliers.csv
```

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/worldpulse.git
cd worldpulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
REST Countries v5 needs a **free** API key. Sign up at <https://restcountries.com/sign-up>, then either:

- create a file named `api_key.txt` in the project folder and paste the key inside, **or**
- set an environment variable:
  ```bash
  # macOS / Linux
  export RESTCOUNTRIES_API_KEY="your_key_here"
  # Windows (PowerShell)
  $env:RESTCOUNTRIES_API_KEY="your_key_here"
  ```

> ⚠️ Never commit your key. Add `api_key.txt` to `.gitignore`.

### 4. Run the pipeline
```bash
python main.py
```

You can also run a single stage, for example `python extract.py` or `python eda.py`.

## 📊 Output

After a run, `outputs/` contains:

| File | Description |
|------|-------------|
| `1_top10_population.png` | Top 10 countries by population |
| `2_region_population.png` | Total population by region |
| `3_region_density.png` | Average population density by region |
| `4_crowded_countries.png` | 10 most and 10 least crowded countries |
| `5_histogram_population.png` | Population distribution (log scale) |
| `6_boxplots.png` | Box plots of population and area (log scale) |
| `summary_table.csv` | Descriptive statistics for population, area, density |
| `region_comparison.csv` | Country count, total population and average density per region |
| `outliers.csv` | Countries flagged as population or area outliers |

### Sample insights
- Asia holds by far the largest share of the world population (about 4.7 billion in this dataset).
- Asia has the highest average density among the big regions, followed by Europe.
- Population is extremely right-skewed, so a log scale is used for the histogram and box plots.

## 🗄️ Data Quality

Of the raw records, a few are rejected by validation rules (these are logged, not hidden):

| Rule | Example rejected record |
|------|-------------------------|
| Country code (`cca3`) must be exactly 3 characters | Abkhazia |
| Population must be greater than 0 | Bouvet Island, Heard Island and McDonald Islands |

The final `countries` table holds the validated rows (248 in the included run).

## 🔎 Example SQL

```sql
-- Top 10 countries by population
SELECT name, population FROM countries
ORDER BY population DESC LIMIT 10;

-- Region comparison
SELECT region, COUNT(*) AS countries,
       SUM(population) AS total_population,
       ROUND(AVG(density), 1) AS avg_density
FROM countries GROUP BY region ORDER BY total_population DESC;
```

## 🔮 Possible Improvements

- Add unit tests for the transform and validation logic.
- Add more fields (languages, currencies, borders) and more charts.
- Schedule the pipeline to refresh the data automatically.
- Build an interactive dashboard (Streamlit or Plotly).

## 📄 License

Add your preferred license here (for example MIT).

## 🙏 Acknowledgements

Data provided by the [REST Countries API](https://restcountries.com).
