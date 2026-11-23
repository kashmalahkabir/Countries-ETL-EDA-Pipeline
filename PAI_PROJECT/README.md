# Countries ETL + EDA Pipeline

Source: REST Countries API v5 (https://restcountries.com), ~250 countries.
v5 needs a FREE API key: sign up at https://restcountries.com/sign-up

## Setup and run
    pip install -r requirements.txt
    # create a file api_key.txt in this folder and paste your key inside
    python main.py

## Steps
1. extract.py   - requests (paged, 100 per call) -> data/raw/countries_raw.json
2. transform.py - pandas cleaning + density column + Pydantic validation
                  (rejected records logged in data/rejected_records.log)
3. load.py      - clean data -> SQLite (countries.db, table "countries")
4. eda.py       - SQL queries, IQR outlier flags (table "countries_flagged"),
                  6 charts + summary tables in outputs/
