# Owners & Pets Analysis

## About This Project

This is one of several projects in my data analytics portfolio, built while transitioning into a data career at 33.
My background is not in tech — I'm learning SQL, Python, and BI tools from scratch, and I'm using real-world
datasets to practice and demonstrate what I've picked up along the way.

This is not a perfect project. It's a learning project — and it'll keep improving as I do.

If you're on a similar journey, feel free to fork it, build on it, or reach out.

---

## Objective

Analyse a pet ownership dataset covering 25 owners and 46 pets across 15 US states to explore
species demographics, geographic distribution, ownership patterns, and owner profiles.

**Skills practised:** Python (pandas, matplotlib, seaborn), SQL (DDL + DQL),
PostgreSQL schema design, one-to-many relationships, data cleaning, and exploratory data analysis.

---

## Dataset

| Attribute      | Detail                                              |
|----------------|-----------------------------------------------------|
| Source         | Structured owners & pets database (relational schema) |
| Tables         | 2 — owners_pets, pets                               |
| Owners         | 25 (across 15 US states)                            |
| Pets           | 46 (8 species)                                      |
| Relationship   | One owner → many pets (one-to-many)                 |

**Key fields:** `state`, `city`, `email`, `species`, `full_name`, `age`, `owner_id`

---

## Project Structure

```
owners-pets/
├── README.md
├── .env                              # DB credentials — not committed to GitHub
├── .gitignore
│
├── data/
│   ├── raw/                          # Raw CSVs exported from the source database
│   │   ├── owners_raw.csv
│   │   └── pets_raw.csv
│   ├── owners_clean.csv              # Cleaned — loaded into PostgreSQL
│   └── pets_clean.csv
│
├── sql/
│   ├── 00_create_database.sql        # CREATE DATABASE owners_pets
│   ├── schema.sql                    # DDL — ERD, DROP/CREATE tables, comments, indexes
│   ├── load_data.sql                 # \copy clean CSVs into tables + verification
│   ├── 01_pet_demographics.sql
│   ├── 02_geographic_analysis.sql
│   ├── 03_owner_pet_relationships.sql
│   └── 04_owner_profile_analysis.sql
│
├── python/
│   ├── 00_load_clean_transform.py    # Load raw CSVs → clean → save clean CSVs
│   ├── 01_pet_demographics.py
│   ├── 02_geographic_analysis.py
│   ├── 03_owner_pet_relationships.py
│   └── 04_owner_profile_analysis.py
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

Create a `.env` file in the `owners-pets/` folder (never commit this):

```
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DATABASE=owners_pets
```

### 3. Run in order

```bash
# Step 1 — Clean raw CSVs and save clean versions
python python/00_load_clean_transform.py

# Step 2 — Set up the database and load data
psql -U postgres -f sql/00_create_database.sql
psql -U postgres -d owners_pets -f sql/schema.sql
psql -U postgres -d owners_pets -f sql/load_data.sql

# Step 3 — Run analysis scripts (any order)
python python/01_pet_demographics.py
python python/02_geographic_analysis.py
python python/03_owner_pet_relationships.py
python python/04_owner_profile_analysis.py
```

All charts are saved to `outputs/`.

---

## Analyses

### 1. Pet Demographics (`01_*`)

| Question | SQL Approach |
|---|---|
| Species distribution & share | GROUP BY + window % |
| Average & median age by species | AVG + PERCENTILE_CONT |
| Age distribution (bucket breakdown) | CASE WHEN age groups |
| Pets per owner ranking | LEFT JOIN + COUNT GROUP BY owner |
| Species × age group matrix | CASE WHEN + GROUP BY species |
| Youngest & oldest per species | MIN / MAX / AVG per species |

### 2. Geographic Analysis (`02_*`)

| Question | SQL Approach |
|---|---|
| Owners by state | GROUP BY state + window % |
| Pets by state | JOIN + COUNT + AVG age |
| Owners and pets by city | GROUP BY city + derived ratio |
| Email domain distribution | SUBSTRING + POSITION |
| US region grouping (N/S/M/W) | CASE WHEN state → region |
| Pets per owner ratio by state | COUNT(pets) / COUNT(DISTINCT owners) |

### 3. Owner-Pet Relationships (`03_*`)

| Question | SQL Approach |
|---|---|
| Multi-pet vs single-pet owners | CASE WHEN on subquery count |
| Most popular species by state | JOIN + GROUP BY state, species |
| Species × state heatmap | Pivot on COUNT |
| Species diversity per owner | COUNT(DISTINCT species) per owner |
| Top owners by species diversity | ORDER BY unique_species + STRING_AGG |
| Pet count by species per city | GROUP BY city, species |

### 4. Owner Profile Analysis (`04_*`)

| Question | SQL Approach |
|---|---|
| Email domain distribution | SUBSTRING + POSITION + window % |
| Email domain vs avg pets owned | JOIN + COUNT / COUNT DISTINCT |
| Most popular pet names | GROUP BY full_name, species |
| Pet name length by species | AVG / MIN / MAX LENGTH |
| Pet age gap per owner | MAX(age) - MIN(age) per owner |
| Owner summary bubble chart | Total pets, unique species, avg age |

---

## Key Findings

- **Dogs and Cats** are by far the most popular species, together accounting for over 60% of all pets
- **New York** and **California** have the highest owner counts, with 3 owners each
- Owners with **3+ pets** show the most species diversity — they tend to mix dogs, cats, and smaller animals
- **Gmail** is the most popular email provider among owners, used by 52% of the dataset
- **Turtles** have the highest average age (10.5 years), while Hamsters are the youngest (avg 1 year)
- Most owners (68%) have exactly **1 or 2 pets** — true multi-pet households are a minority
- The **Pacific Northwest (WA)** and **Northeast (NY, MA)** have the highest pets-per-owner ratios

---

## What I Practised

- Writing DDL with a one-to-many relationship, foreign key constraints, column comments, and indexes
- Loading parent-child tables in dependency order using PostgreSQL's `\copy`
- Resetting SERIAL sequences after bulk CSV loads
- Writing DQL queries: GROUP BY, HAVING, CASE WHEN, window functions, subqueries, STRING_AGG
- Cleaning relational data with pandas — stripping CHAR padding, validating emails
- Building charts with matplotlib and seaborn including heatmaps, range bars, and bubble charts
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
[OOSHDB](https://github.com/masudrana) — a simulated food retail database where I learned
schema design, ERD modelling, bulk data injection (1M+ rows), and connecting to BI tools like Qlik Sense.

From there I moved to working with real datasets to practice the full pipeline:
raw data → cleaning → SQL → Python → visualisation.

**Tools I've worked with so far:** PostgreSQL, pgAdmin 4, VS Code, Mac Terminal,
Python (pandas, matplotlib, seaborn), Qlik Sense, Git/GitHub.

---

*Built by Masud — data analytics learner, career changer, work in progress.*
