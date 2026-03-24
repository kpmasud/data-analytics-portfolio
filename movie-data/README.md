# Movie Data Analysis

## About This Project

This is one of several projects in my data analytics portfolio, built while transitioning into a data career at 33.
My background is not in tech — I'm learning SQL, Python, and BI tools from scratch, and I'm using real-world
datasets to practice and demonstrate what I've picked up along the way.

This is not a perfect project. It's a learning project — and it'll keep improving as I do.

If you're on a similar journey, feel free to fork it, build on it, or reach out.

---

## Objective

Analyse a curated movie database covering 53 films, 147 actors, and 75 directors to explore
box-office revenue patterns, movie catalogue composition, director productivity, and actor demographics.

**Skills practised:** Python (pandas, matplotlib, seaborn), SQL (DDL + DQL),
PostgreSQL schema design with foreign keys, multi-table joins, data cleaning, and exploratory data analysis.

---

## Dataset

| Attribute      | Detail                                         |
|----------------|------------------------------------------------|
| Source         | Structured movie database (relational schema)  |
| Tables         | 5 — directors, actors, movies, movie_revenues, movies_actors |
| Movies         | 53                                             |
| Actors         | 147                                            |
| Directors      | 75                                             |
| Revenue rows   | 53 (domestic and/or international takings)     |
| Cast links     | 181 (movies_actors junction)                   |

> Revenue figures are in millions USD.
> All analysis is intended for learning and portfolio demonstration.

**Key fields:** `movie_lang`, `age_certificate`, `release_date`, `movie_length`,
`domestic_takings`, `international_takings`, `nationality`, `gender`

---

## Project Structure

```
movie-data/
├── README.md
├── .env                              # DB credentials — not committed to GitHub
├── .gitignore
│
├── data/
│   ├── raw/                          # Raw CSVs exported from the source database
│   │   ├── directors_raw.csv
│   │   ├── actors_raw.csv
│   │   ├── movies_raw.csv
│   │   ├── movie_revenues_raw.csv
│   │   └── movies_actors_raw.csv
│   ├── directors_clean.csv           # Cleaned — loaded into PostgreSQL
│   ├── actors_clean.csv
│   ├── movies_clean.csv
│   ├── movie_revenues_clean.csv
│   └── movies_actors_clean.csv
│
├── sql/
│   ├── 00_create_database.sql        # CREATE DATABASE movie_data
│   ├── schema.sql                    # DDL — ERD, DROP/CREATE tables, comments, indexes
│   ├── load_data.sql                 # \copy clean CSVs into all tables
│   ├── 01_revenue_analysis.sql
│   ├── 02_movie_catalog_analysis.sql
│   ├── 03_director_analysis.sql
│   └── 04_actor_analysis.sql
│
├── python/
│   ├── 00_load_clean_transform.py    # Load raw CSVs → clean → save clean CSVs
│   ├── 01_revenue_analysis.py
│   ├── 02_movie_catalog_analysis.py
│   ├── 03_director_analysis.py
│   └── 04_actor_analysis.py
│
└── outputs/                          # All generated charts saved as PNG
```

---

## Pipeline

```
Raw CSVs (data/raw/)  →  Python (clean & transform)  →  *_clean.csv
                                                               ↓
                                                      SQL: CREATE DATABASE
                                                      SQL: CREATE TABLEs + indexes
                                                      SQL: \copy data into tables
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

Create a `.env` file in the `movie-data/` folder (never commit this):

```
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DATABASE=movie_data
```

### 3. Run in order

```bash
# Step 1 — Clean raw CSVs and save clean versions
python python/00_load_clean_transform.py

# Step 2 — Set up the database and load data
psql -U postgres -f sql/00_create_database.sql
psql -U postgres -d movie_data -f sql/schema.sql
psql -U postgres -d movie_data -f sql/load_data.sql

# Step 3 — Run analysis scripts (any order)
python python/01_revenue_analysis.py
python python/02_movie_catalog_analysis.py
python python/03_director_analysis.py
python python/04_actor_analysis.py
```

All charts are saved to `outputs/`.

---

## Analyses

### 1. Revenue Analysis (`01_*`)

| Question | SQL Approach |
|---|---|
| Top 10 movies by total revenue | JOIN + COALESCE + ORDER BY |
| Domestic vs international comparison | Scatter plot, ratio calculation |
| Revenue data coverage | LEFT JOIN + COUNT vs COUNT(*) |
| Average revenue by language | GROUP BY + AVG(COALESCE) |
| Revenue by director nationality | JOIN directors + GROUP BY nationality |
| International dominance | intl − domestic surplus, signed bar chart |

### 2. Movie Catalog Analysis (`02_*`)

| Question | SQL Approach |
|---|---|
| Movie count & share by language | GROUP BY + window % |
| Age certificate breakdown | GROUP BY + avg length + avg cast size |
| Movie length by language | MIN / MAX / AVG / PERCENTILE_CONT |
| Movies released by decade | EXTRACT(YEAR) / 10 * 10 bucketing |
| Language × age certificate heatmap | Pivot on COUNT |
| Movies per year by language | EXTRACT(YEAR) + GROUP BY lang |

### 3. Director Analysis (`03_*`)

| Question | SQL Approach |
|---|---|
| Director nationality distribution | GROUP BY + window % |
| Most prolific directors | COUNT, HAVING > 1 film |
| Director revenue performance | JOIN revenues + SUM / AVG |
| Director age distribution | DATE_PART AGE histogram |
| English vs non-English comparison | CASE WHEN + GROUP BY |
| Career span (first to last film) | MIN / MAX release year per director |

### 4. Actor Analysis (`04_*`)

| Question | SQL Approach |
|---|---|
| Gender distribution | CASE WHEN + COUNT + window % |
| Most prolific actors | JOIN movies_actors + COUNT |
| Actor age histogram | DATE_PART AGE |
| Cast size per movie | COUNT(actor_id) GROUP BY movie_id |
| Average cast size by language | Subquery join + AVG |
| Gender representation by language | SUM(CASE WHEN gender) + pct_female |

---

## Key Findings

- **English-language films** make up the largest share of the catalogue but earn only moderately higher average revenue than Chinese-language films
- **Crouching Tiger Hidden Dragon** is the top earner with $213.2M total, demonstrating that non-English films can dominate globally
- The majority of films (**65%+**) have no international takings on record — a significant data gap worth noting
- **American directors** lead in both quantity and total box-office revenue
- **Stanley Kubrick** is the most represented director with multiple classics in the dataset
- The cast is **male-dominated** across all languages, with Female actors averaging around 30% of appearances
- Film lengths have **increased over the decades** — 2000s films average longer than 1970s films

---

## What I Practised

- Writing DDL with multiple tables, foreign keys, column comments, and composite primary keys
- Loading data with PostgreSQL's `\copy` across parent-child tables in dependency order
- Resetting SERIAL sequences after bulk CSV loads
- Writing multi-table JOINs, window functions (RANK, PERCENTILE_CONT, PARTITION BY), and CASE WHEN
- Cleaning multi-table relational data with pandas
- Building charts with matplotlib and seaborn including scatter plots, range bars, and heatmaps
- Structuring a relational project for GitHub with a clean folder layout

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

From there I moved to working with real datasets to practice the full pipeline:
raw data → cleaning → SQL → Python → visualisation.

**Tools I've worked with so far:** PostgreSQL, pgAdmin 4, VS Code, Mac Terminal,
Python (pandas, matplotlib, seaborn), Qlik Sense, Git/GitHub.

---

*Built by Masud — data analytics learner, career changer, work in progress.*
