# Hospital Bed Management Analysis

A data analytics project exploring hospital operational data across 4 services — emergency, surgery, general medicine, and ICU — covering 52 weeks of bed utilisation, patient records, and staff attendance.

**Purpose:** Practising multi-table SQL (JOINs, CTEs, window functions), Python data cleaning with a malformed real-world CSV, and operational healthcare analytics.

---

## The Dataset

| Detail | Value |
|---|---|
| Source | Synthetic hospital operations dataset |
| Services | Emergency, Surgery, General Medicine, ICU |
| Tables | bed_metrics, patients, staff, staff_schedule |
| Weeks | 52 (full year) |
| Total rows | ~7,870 across 4 tables |
| Events | none, flu, donation, strike |

### Table Summary

| Table | Rows | Description |
|---|---|---|
| bed_metrics | 208 | Weekly capacity & KPIs per service (52 weeks × 4 services) |
| patients | 1,000 | Individual patient records with arrival/departure dates |
| staff | 110 | Staff roster with role and service assignment |
| staff_schedule | 6,552 | Weekly attendance per staff member |

---

## Pipeline

```
4 raw CSVs (data/raw/)
        |
        v
python/00_load_clean_transform.py   -- clean, fix column bug, compute derived fields
        |
        v
sql/00_create_database.sql          -- CREATE DATABASE hospital_db
sql/schema.sql                      -- CREATE TABLE x4 + indexes
sql/load_data.sql                   -- \copy 4 clean CSVs into PostgreSQL
        |
        v
sql/01_bed_utilisation.sql          -- 6 bed capacity queries
sql/02_patient_analysis.sql         -- 6 patient queries
sql/03_staff_analysis.sql           -- 6 staff queries
sql/04_service_performance.sql      -- 6 service KPI queries
        |
        v
python/01–04_*.py                   -- same queries + 24 charts → outputs/
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
psql -U postgres -d hospital_db -f sql/schema.sql
psql -U postgres -d hospital_db -f sql/load_data.sql
```

**Step 3 — Run SQL analysis (optional — open in psql or pgAdmin):**
```bash
psql -U postgres -d hospital_db -f sql/01_bed_utilisation.sql
psql -U postgres -d hospital_db -f sql/02_patient_analysis.sql
psql -U postgres -d hospital_db -f sql/03_staff_analysis.sql
psql -U postgres -d hospital_db -f sql/04_service_performance.sql
```

**Step 4 — Generate visualisations:**
```bash
python3 python/01_bed_utilisation.py
python3 python/02_patient_analysis.py
python3 python/03_staff_analysis.py
python3 python/04_service_performance.py
```

Charts are saved to `outputs/`.

---

## Analysis Modules

### 01 — Bed Utilisation & Capacity
| Question | Technique |
|---|---|
| Admission rate by service | AVG, GROUP BY |
| Weekly occupancy trend | SUM / available_beds, line chart |
| Monthly refusal rate | SUM + ratio, dual-axis chart |
| Event impact on admissions & satisfaction | GROUP BY event |
| Most overcrowded service | AVG refused, ranked bar |
| Occupancy heatmap — service × month | Pivot heatmap |

### 02 — Patient Analysis
| Question | Technique |
|---|---|
| Age distribution of patients | Histogram |
| Length of stay by service | PERCENTILE_CONT, box plot |
| Patient satisfaction by service | AVG, GROUP BY |
| Monthly admissions & avg length of stay | EXTRACT(MONTH), dual-axis |
| Age group × service demand | CASE WHEN + heatmap |
| Satisfaction by length-of-stay band | CASE WHEN buckets |

### 03 — Staff & Attendance
| Question | Technique |
|---|---|
| Staff count by role and service | COUNT, GROUP BY, pivot bar |
| Weekly attendance rate by service | SUM(present)/COUNT, multi-line |
| Staff morale trend by month | AVG, MIN, MAX with range band |
| Attendance rate by role | SUM(present)/total shifts |
| Attendance heatmap — service × month | JOIN bed_metrics for week→month |
| Staff morale vs patient satisfaction | Scatter plot |

### 04 — Service Performance
| Question | Technique |
|---|---|
| KPI summary per service | Multi-metric grouped bar |
| Event impact on all KPIs | GROUP BY event, grouped bar |
| Month-over-month demand growth | LAG() window function |
| High-pressure weeks — satisfaction | CTE + CROSS JOIN threshold |
| Morale vs satisfaction by service | Bubble scatter chart |
| Weekly composite performance score | AVG of 3 KPIs, colour-coded bar |

---

## Key Findings

- **General medicine has the lowest admission rate** (~52%) — highest unmet demand in the hospital
- **7,642 patients were refused** across the year — a significant capacity gap, peaking in summer months
- **Flu events reduce staff morale** the most sharply, while donation events slightly improve satisfaction
- **Surgery patients stay longest** on average (7.9 days), ICU second (7.6 days)
- **Staff attendance dips in mid-year** (months 5–7), correlating with lower patient satisfaction scores
- **ICU has the highest staff morale** despite serving critically ill patients — smallest team, tightest cohesion
- **The composite performance score** peaks in weeks 10–14 and dips in weeks 24–30 (mid-year pressure)

---

## What I Practised

**SQL**
- Multi-table `JOIN` across 4 tables
- `EXTRACT(MONTH FROM ...)` for date-based grouping
- `LAG()` window function for month-over-month growth
- `PERCENTILE_CONT` for median length of stay
- `CASE WHEN` for age groups and stay bands
- CTEs (`WITH`) for threshold-based filtering
- `CROSS JOIN` for benchmark comparisons

**Python**
- Fixing a real-world CSV column-shift bug in the clean script
- Computing derived fields: `admission_rate`, `length_of_stay`
- `pd.to_datetime` for date handling and stay duration calculation
- Dual-axis charts (`twinx`) for count + rate on one figure
- Heatmaps with `seaborn` and `matplotlib`
- Bubble scatter charts with variable marker size
- Joining week → month via a separate query for heatmap aggregation

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
hospital-bed-management/
├── README.md
├── .env                        (not committed — contains DB credentials)
├── .gitignore
├── data/
│   ├── raw/                    (4 original CSVs)
│   ├── bed_metrics_clean.csv
│   ├── patients_clean.csv
│   ├── staff_clean.csv
│   └── schedule_clean.csv
├── sql/
│   ├── 00_create_database.sql
│   ├── schema.sql
│   ├── load_data.sql
│   ├── 01_bed_utilisation.sql
│   ├── 02_patient_analysis.sql
│   ├── 03_staff_analysis.sql
│   └── 04_service_performance.sql
├── python/
│   ├── 00_load_clean_transform.py
│   ├── 01_bed_utilisation.py
│   ├── 02_patient_analysis.py
│   ├── 03_staff_analysis.py
│   └── 04_service_performance.py
└── outputs/                    (24 PNG charts)
```

---

*Built by Masud — data analytics learner, career changer, work in progress.*
