# AirBNB NYC Market Analysis

## About This Project

This is one of several projects in my data analytics portfolio, built while transitioning into a data career at 33.
My background is not in tech — I'm learning SQL, Python, and BI tools from scratch, and I'm using real-world
datasets to practice and demonstrate what I've picked up along the way.

This is not a perfect project. It's a learning project — and it'll keep improving as I do.

If you're on a similar journey, feel free to fork it, build on it, or reach out.

---

## Objective

Analyse the New York City Airbnb listings dataset to uncover pricing dynamics,
listing composition, geographic distribution, and host behaviour patterns across
the five boroughs of New York City.

**Skills practised:** Python (pandas, matplotlib, seaborn), SQL (DDL + DQL),
PostgreSQL schema design, data cleaning, and exploratory data analysis.

---

## Dataset

| Attribute      | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| Source         | [Kaggle — Airbnb NYC Listings](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data) |
| Raw file       | `data/airbnb_raw.csv`                                                  |
| Rows (raw)     | 30,478                                                                 |
| Rows (cleaned) | 29,875                                                                 |
| Columns        | 13                                                                     |

> **Note:** Data was sourced from Kaggle for practice purposes only.
> All analysis in this project is intended for learning and portfolio demonstration.

**Key columns:** `host_id`, `host_since`, `neighbourhood` (borough),
`property_type`, `room_type`, `zipcode`, `beds`, `price`,
`number_of_reviews`, `review_score_rating`

---

## Project Structure

```
air-bnb/
├── README.md
├── .env                              # DB credentials — not committed to GitHub
├── .gitignore
│
├── data/
│   ├── airbnb_raw.csv                # Raw source data (from Kaggle)
│   └── airbnb_clean.csv              # Cleaned & transformed — loaded into PostgreSQL
│
├── sql/
│   ├── 00_create_database.sql        # CREATE DATABASE airbnb_nyc
│   ├── schema.sql                    # DDL — CREATE TABLE, ERD, column comments, indexes
│   ├── load_data.sql                 # COPY clean CSV into listings table
│   ├── 01_price_analysis.sql
│   ├── 02_room_property_analysis.sql
│   ├── 03_geographic_analysis.sql
│   └── 04_host_review_analysis.sql
│
├── python/
│   ├── 00_load_clean_transform.py    # Load raw CSV → clean → save airbnb_clean.csv
│   ├── 01_price_analysis.py
│   ├── 02_room_property_analysis.py
│   ├── 03_geographic_analysis.py
│   └── 04_host_review_analysis.py
│
└── outputs/                          # All generated charts saved as PNG
```

---

## Pipeline

```
Raw CSV  →  Python (clean & transform)  →  airbnb_clean.csv
                                                  ↓
                                         SQL: CREATE DATABASE
                                         SQL: CREATE TABLE + indexes
                                         SQL: COPY data into table
                                                  ↓
                                    SQL analysis files (DQL queries)
                                    Python analysis files (same queries + charts)
                                                  ↓
                                             outputs/ (PNG charts)
```

---

## How to Run

### 1. Prerequisites

```bash
pip install pandas psycopg2-binary matplotlib seaborn python-dotenv
```

PostgreSQL 17 must be running locally.

### 2. Configure credentials

Create a `.env` file in the `air-bnb/` folder (never commit this):

```
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DATABASE=airbnb_nyc
```

### 3. Run in order

```bash
# Step 1 — Clean the raw data and save airbnb_clean.csv
python python/00_load_clean_transform.py

# Step 2 — Set up the database and load data using SQL
psql -U postgres -f sql/00_create_database.sql
psql -U postgres -d airbnb_nyc -f sql/schema.sql
psql -U postgres -d airbnb_nyc -f sql/load_data.sql

# Step 3 — Run analysis scripts (any order)
python python/01_price_analysis.py
python python/02_room_property_analysis.py
python python/03_geographic_analysis.py
python python/04_host_review_analysis.py
```

All charts are saved to `outputs/`.

---

## Analyses

### 1. Price Analysis (`01_*`)

| Question | SQL Approach |
|---|---|
| Median & avg price per borough | GROUP BY + PERCENTILE_CONT |
| Price distribution by room type | Box plot, GROUP BY |
| How number of beds affects price | GROUP BY beds (1–6) |
| Most expensive property types | GROUP BY, HAVING COUNT >= 10 |
| Price bucket breakdown | CASE WHEN + window function % |
| Borough × Room Type heatmap | Pivot on median price |

### 2. Room & Property Type Analysis (`02_*`)

| Question | SQL Approach |
|---|---|
| Listing count & share per room type | GROUP BY + window % |
| Top 10 property types by count | GROUP BY, ORDER BY COUNT |
| Room type composition per borough | Window PARTITION BY neighbourhood |
| Average beds by room type | AVG aggregation |
| Property type × room type cross-tab | Heatmap pivot |
| Review scores by room type | AVG WHERE NOT NULL |

### 3. Geographic & Neighbourhood Analysis (`03_*`)

| Question | SQL Approach |
|---|---|
| Listings, price & unique hosts per borough | GROUP BY, COUNT DISTINCT |
| Top 15 ZIP codes by listing count | GROUP BY zipcode |
| Most expensive ZIP codes | HAVING COUNT >= 20 |
| Listings per host (commercial density) | Derived ratio |
| Borough price vs city average | RANK() + deviation from AVG window |

### 4. Host & Review Analysis (`04_*`)

| Question | SQL Approach |
|---|---|
| New hosts joining per year | EXTRACT(YEAR), COUNT DISTINCT |
| Host portfolio segmentation | CASE WHEN on subquery count |
| Review score band distribution | CASE WHEN bucketing |
| Avg review score by borough | GROUP BY neighbourhood |
| Portfolio size vs review score & price | JOIN host subquery |

---

## Key Findings

- **Manhattan** dominates with 52.7% of all listings and the highest median price at **$155/night**
- **Entire home/apt** is the most common room type, making up 56% of all listings
- Listings in the **$100–$149/night** range account for the largest share of the market
- Host growth peaked around **2015–2016** and plateaued after that
- **Single-listing hosts** consistently score higher on reviews than multi-listing commercial operators
- The most expensive ZIP codes are concentrated in **lower Manhattan and parts of Brooklyn**

---

## What I Practised

- Writing DDL (CREATE TABLE, constraints, indexes, column comments)
- Loading data with PostgreSQL's `\copy` command
- Writing DQL queries: GROUP BY, HAVING, CASE WHEN, window functions (RANK, PERCENTILE_CONT, PARTITION BY)
- Cleaning and transforming data with pandas
- Building charts with matplotlib and seaborn
- Structuring a project for GitHub with a clean folder layout

---

## Tools & Technologies

| Tool | Purpose |
|---|---|
| Python 3.13 | Data cleaning, transformation, visualisation |
| pandas | Data manipulation and transformation |
| matplotlib / seaborn | Charts and visualisations |
| psycopg2 | PostgreSQL connectivity from Python |
| PostgreSQL 17 | Database engine |
| SQL — DDL + DQL | Schema design and analytical queries |
| VS Code | Development environment |
| Git / GitHub | Version control and portfolio hosting |

---

## My Learning Journey

This project is part of a growing portfolio I'm building as I transition into data at 33.
I started with PostgreSQL through a hands-on practice project called
[OOSHDB](https://github.com/kpmasud/ooshdb-vivanti-project) — a simulated food retail database where I learned
schema design, ERD modelling, bulk data injection (1M+ rows), and connecting to BI tools like Qlik Sense.

From there I moved to working with real public datasets to practice the full pipeline:
raw data → cleaning → SQL → Python → visualisation.

**Tools I've worked with so far:** PostgreSQL, pgAdmin 4, VS Code, Mac Terminal,
Python (pandas, matplotlib, seaborn), Qlik Sense, Git/GitHub.

---

*Built by Masud — data analytics learner, career changer, work in progress.*
