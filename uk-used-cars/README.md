# UK Used Car Market Analysis

A data analytics project exploring ~96,000 used car listings across 9 major UK brands. Built as part of my portfolio while changing careers into data analytics at 33.

**Data source:** [100,000 UK Used Car Dataset — Kaggle](https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes)

**Purpose:** Practising SQL (PostgreSQL), Python (pandas, matplotlib, seaborn), and data visualisation on a real-world dataset.

---

## The Dataset

| Detail | Value |
|---|---|
| Source | Kaggle — 9 brand CSV files |
| Brands | Audi, BMW, Ford, Hyundai, Mercedes, Skoda, Toyota, Vauxhall, Volkswagen |
| Raw rows | ~99,000 |
| Clean rows | 95,999 |
| Years | 1998 – 2020 |
| Price range | £3,995 – £52,000 |
| Columns | brand, model, year, price, transmission, mileage, fuel_type, tax, mpg, engine_size |

---

## Pipeline

```
9 brand CSVs (data/raw/)
        |
        v
python/00_load_clean_transform.py   -- merge, clean, save cars_clean.csv
        |
        v
sql/00_create_database.sql          -- CREATE DATABASE cars_uk
sql/schema.sql                      -- CREATE TABLE cars + indexes
sql/load_data.sql                   -- \copy 95,999 rows into PostgreSQL
        |
        v
sql/01_price_analysis.sql           -- 6 price queries
sql/02_brand_model_analysis.sql     -- 6 brand & model queries
sql/03_fuel_transmission_analysis.sql -- 6 fuel & transmission queries
sql/04_depreciation_mileage_analysis.sql -- 6 depreciation queries
sql/05_model_deep_dive.sql          -- 6 model-level queries
        |
        v
python/01–05_*.py                   -- same queries + 30 charts → outputs/
```

---

## How to Run

**Step 1 — Clean and transform the data:**
```bash
python3 python/00_load_clean_transform.py
```

**Step 2 — Set up the database (run in order from project root):**
```bash
psql -U postgres -f sql/00_create_database.sql
psql -U postgres -d cars_uk -f sql/schema.sql
psql -U postgres -d cars_uk -f sql/load_data.sql
```

**Step 3 — Run SQL analysis (optional — open in psql or pgAdmin):**
```bash
psql -U postgres -d cars_uk -f sql/01_price_analysis.sql
psql -U postgres -d cars_uk -f sql/02_brand_model_analysis.sql
psql -U postgres -d cars_uk -f sql/03_fuel_transmission_analysis.sql
psql -U postgres -d cars_uk -f sql/04_depreciation_mileage_analysis.sql
psql -U postgres -d cars_uk -f sql/05_model_deep_dive.sql
```

**Step 4 — Generate visualisations:**
```bash
python3 python/01_price_analysis.py
python3 python/02_brand_model_analysis.py
python3 python/03_fuel_transmission_analysis.py
python3 python/04_depreciation_mileage_analysis.py
python3 python/05_model_deep_dive.py
```

Charts are saved to `outputs/`.

---

## Analysis Modules

### 01 — Price Analysis
| Question | Technique |
|---|---|
| Median & avg price per brand | GROUP BY + PERCENTILE_CONT |
| Price distribution by fuel type | Box plot |
| Price by transmission type | Bar chart |
| Price bracket breakdown | CASE WHEN + window % |
| Top 10 most expensive models | GROUP BY, HAVING, ORDER BY |
| Brand × Transmission heatmap | Pivot on median price |

### 02 — Brand & Model Analysis
| Question | Technique |
|---|---|
| Market share per brand | COUNT + window % |
| Top 10 most listed models | GROUP BY, ORDER BY COUNT |
| Top 10 most expensive models | HAVING >= 50 |
| Average mileage per brand | AVG aggregation |
| Brand × Fuel type cross-tab | Heatmap |
| Year range per brand | MIN/MAX year |

### 03 — Fuel & Transmission Analysis
| Question | Technique |
|---|---|
| Fuel type distribution | GROUP BY + window % |
| Transmission type breakdown | COUNT, pie chart |
| Average MPG by fuel type | AVG WHERE NOT NULL |
| Annual road tax by fuel type | AVG, GROUP BY |
| Fuel type trend by year (2010–2020) | Stacked bar, GROUP BY year |
| Engine size distribution by fuel type | Box plot |

### 04 — Depreciation & Mileage Analysis
| Question | Technique |
|---|---|
| Depreciation curve — price by year | GROUP BY year |
| Median price by mileage band | CASE WHEN buckets |
| Average mileage by brand | AVG, GROUP BY |
| % depreciation vs newest stock | CTE + CROSS JOIN |
| Engine size bands vs price | CASE WHEN + bar chart |
| High vs low mileage price gap | FILTER clause + PERCENTILE_CONT |

### 05 — Model Deep-Dive
| Question | Technique |
|---|---|
| Top 3 most listed models per brand | RANK() OVER PARTITION BY |
| Best value models — price per mile | Ratio calc, HAVING >= 100 |
| Most affordable models under £8k | HAVING + PERCENTILE_CONT filter |
| Model price ranking within brand | DENSE_RANK() OVER PARTITION BY |
| Model depreciation: 2019 vs 2015 stock | CTE + JOIN on brand/model |
| Fuel efficiency league table | AVG MPG, HAVING >= 50 |

---

## Key Findings

- **Ford dominates** the dataset with ~18k listings — by far the most listed brand
- **Mercedes** commands the highest median price, nearly double that of Vauxhall
- **Diesel** accounts for the majority of listings but its share drops sharply post-2016 as petrol grows
- **Automatic** cars are significantly more expensive than manuals across every brand
- **Depreciation is steepest in the first 3–4 years** — cars from 2017–2020 hold value much better than pre-2015 stock
- **Toyota and Hyundai** have the lowest average mileage — suggesting buyers keep newer stock
- **BMW 5 Series and Mercedes E Class** show the steepest depreciation from 2019 to 2015 stock

---

## What I Practised

**SQL**
- `GROUP BY`, `HAVING`, `ORDER BY`
- `PERCENTILE_CONT` for median calculations
- `CASE WHEN` for bucketing and segmentation
- Window functions: `RANK()`, `DENSE_RANK()`, `PARTITION BY`, `FILTER`
- CTEs (`WITH`) and `CROSS JOIN`
- `\copy` for bulk CSV loading into PostgreSQL

**Python**
- `pandas` for merging multiple CSVs, cleaning, type casting, outlier removal
- `psycopg2` for PostgreSQL connectivity
- `matplotlib` + `seaborn` for bar charts, box plots, heatmaps, line charts, pie charts, stacked bars
- `python-dotenv` for credential management

---

## Tools

| Tool | Purpose |
|---|---|
| PostgreSQL 17 | Database |
| psql | DDL + data loading |
| Python 3 | Data cleaning + visualisation |
| pandas | Data manipulation |
| matplotlib / seaborn | Charts |
| VS Code | Development |

---

## Project Structure

```
uk-used-cars/
├── README.md
├── .env                      (not committed — contains DB credentials)
├── .gitignore
├── data/
│   ├── raw/                  (9 brand CSVs from Kaggle)
│   └── cars_clean.csv        (cleaned, merged, ready for PostgreSQL)
├── sql/
│   ├── 00_create_database.sql
│   ├── schema.sql
│   ├── load_data.sql
│   ├── 01_price_analysis.sql
│   ├── 02_brand_model_analysis.sql
│   ├── 03_fuel_transmission_analysis.sql
│   ├── 04_depreciation_mileage_analysis.sql
│   └── 05_model_deep_dive.sql
├── python/
│   ├── 00_load_clean_transform.py
│   ├── 01_price_analysis.py
│   ├── 02_brand_model_analysis.py
│   ├── 03_fuel_transmission_analysis.py
│   ├── 04_depreciation_mileage_analysis.py
│   └── 05_model_deep_dive.py
└── outputs/                  (30 PNG charts)
```

---

*Built by Masud — data analytics learner, career changer, work in progress.*
