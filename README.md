# Helsinki Mobility Data Stack 🚌🚊

End-to-end ELT pipeline ingesting live Helsinki public transport data into a modern data lakehouse, with automated testing and an interactive dashboard.

## 🎯 What This Project Does

- **Extracts** real-time stop and route data from HSL (Helsinki Region Transport) GraphQL API
- **Loads** raw data into DuckDB following medallion architecture (Bronze layer)
- **Transforms** data through dbt staging and marts (Silver and Gold layers)
- **Tests** data quality with 20+ automated checks
- **Visualizes** insights through an interactive Streamlit dashboard

## 🏗️ Architecture
HSL Digitransit API
│
│  (extract_hsl.py, extract_routes.py)
▼
data/raw/.json          ← Raw layer (versioned, timestamped)
│
│  (load_to_duckdb.py)
▼
raw.stops, raw.routes    ← Bronze layer
│
│  (dbt: stg_stops, stg_routes)
▼
main_staging.           ← Silver layer (cleaned, validated)
│
│  (dbt: marts)
▼
main_marts.*             ← Gold layer (analytics-ready)
│
│  (Streamlit + Plotly)
▼
Interactive Dashboard

## 🛠️ Tech Stack

- **Python 3.11** — extraction scripts
- **DuckDB** — embedded analytical database
- **dbt-duckdb** — SQL transformations + testing
- **Streamlit** — interactive dashboard
- **Plotly** — visualizations
- **GraphQL** — HSL API integration

## 📊 Key Numbers

- **8,320** stops loaded from HSL across 7 vehicle modes
- **449** active routes (BUS, TRAM, RAIL, SUBWAY, FERRY, etc.)
- **5** dbt models (2 staging views + 3 mart tables)
- **20+** automated data quality tests passing
- **3-layer** medallion architecture (Bronze → Silver → Gold)

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Free HSL Digitransit API key from [portal-api.digitransit.fi](https://portal-api.digitransit.fi/)

### Setup
```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/helsinki-mobility-stack.git
cd helsinki-mobility-stack

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "HSL_API_KEY=your_key_here" > .env
```

### Run the Pipeline
```bash
# 1. Extract data
python extract_hsl.py
python extract_routes.py

# 2. Load to DuckDB
python load_to_duckdb.py

# 3. Run dbt transformations + tests
cd helsinki_dbt
dbt run
dbt test

# 4. Launch dashboard
cd ..
streamlit run app.py
```

## 📁 Project Structure
helsinki-mobility-stack/
├── extract_hsl.py              # Stops extraction
├── extract_routes.py           # Routes extraction
├── load_to_duckdb.py           # Bronze layer loader
├── app.py                      # Streamlit dashboard
├── helsinki.db                 # DuckDB database
├── data/
│   └── raw/                    # Timestamped JSON dumps
├── helsinki_dbt/               # dbt project
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/            # Silver layer
│       │   ├── stg_stops.sql
│       │   ├── stg_routes.sql
│       │   ├── _sources.yml
│       │   └── _models.yml
│       └── marts/              # Gold layer
│           ├── stops_by_mode.sql
│           ├── stops_central_helsinki.sql
│           └── route_summary.sql
├── .env                        # API key (gitignored)
├── .gitignore
└── README.md

## ✅ Data Quality

The pipeline runs 20+ automated tests on every build:
- **Source-level**: not_null and unique on primary keys
- **Staging-level**: type validation, accepted_values for enums
- **Mart-level**: not_null on aggregated metrics

Real production gotcha caught by these tests: the **Suomenlinna ferry** route (HSL-lautta operator) has no short_name in source data — handled by filtering at staging layer with a documented exception.

## 🎓 Concepts Demonstrated

- ELT vs ETL (modern pattern)
- Medallion architecture (Bronze / Silver / Gold)
- Idempotent pipelines (DROP IF EXISTS, CREATE IF NOT EXISTS)
- Data lineage (timestamped files + loaded_at columns)
- Secrets management (.env + .gitignore + python-dotenv)
- GraphQL API integration with rate limiting
- SQL injection prevention via parameter binding
- Production error handling (HTTP errors + GraphQL silent failures)
- Type safety in dbt via accepted_values tests

## 📜 Data Attribution

Data source: HSL Digitransit API ([digitransit.fi](https://digitransit.fi))  
Licensed under EUPL v1.2 / Creative Commons BY 4.0

## 👤 Author

Indrani Nag — Data Engineer | Tampere, Finland  
[LinkedIn](https://linkedin.com/in/) | [GitHub](https://github.com/)