"""
=============================================================================
PROJECT  : Hospital Bed Management Analysis
FILE     : python/00_load_clean_transform.py
PURPOSE  : Load 4 raw CSVs, clean & transform, save clean CSVs ready for
           PostgreSQL import.
           Database creation and loading is handled by SQL:
             1. psql -U postgres             -f sql/00_create_database.sql
             2. psql -U postgres -d hospital_db -f sql/schema.sql
             3. psql -U postgres -d hospital_db -f sql/load_data.sql
=============================================================================
"""

import os
import pandas as pd

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR   = os.path.join(BASE_DIR, "data", "raw")
DATA_DIR  = os.path.join(BASE_DIR, "data")


# ── Step 1 : Load raw CSVs ─────────────────────────────────────────────────
def load_raw():
    print("[ Step 1 ]  Loading raw CSVs ...")

    bed_metrics = pd.read_csv(os.path.join(RAW_DIR, "hospital_db.csv"))
    patients    = pd.read_csv(os.path.join(RAW_DIR, "patients.csv"))
    staff       = pd.read_csv(os.path.join(RAW_DIR, "staff.csv"))
    schedule    = pd.read_csv(os.path.join(RAW_DIR, "staff_schedule.csv"))

    print(f"            bed_metrics   {len(bed_metrics):>6,} rows")
    print(f"            patients      {len(patients):>6,} rows")
    print(f"            staff         {len(staff):>6,} rows")
    print(f"            staff_schedule{len(schedule):>6,} rows")

    return bed_metrics, patients, staff, schedule


# ── Step 2 : Clean & transform ─────────────────────────────────────────────
def clean_bed_metrics(df):
    print("[ Step 2a ] Cleaning bed_metrics ...")

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["week", "month", "service"])

    df["week"]               = df["week"].astype(int)
    df["month"]              = df["month"].astype(int)
    df["available_beds"]     = df["available_beds"].astype(int)
    df["patients_request"]   = df["patients_request"].astype(int)
    df["patients_admitted"]  = df["patients_admitted"].astype(int)
    df["patients_refused"]   = df["patients_refused"].astype(int)
    df["patient_satisfaction"] = pd.to_numeric(df["patient_satisfaction"], errors="coerce")
    df["staff_morale"]       = pd.to_numeric(df["staff_morale"], errors="coerce")
    df["service"]            = df["service"].str.strip()
    df["event"]              = df["event"].str.strip().fillna("none")

    # Derived: admission rate (%)
    df["admission_rate"] = (
        df["patients_admitted"] / df["patients_request"].replace(0, pd.NA) * 100
    ).round(1)

    df = df[["week", "month", "service", "available_beds",
             "patients_request", "patients_admitted", "patients_refused",
             "admission_rate", "patient_satisfaction", "staff_morale", "event"]]

    print(f"            Clean rows: {len(df):,}")
    return df


def clean_patients(df):
    print("[ Step 2b ] Cleaning patients ...")

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["patient_id", "arrival_date", "departure_date", "service"])

    df["arrival_date"]   = pd.to_datetime(df["arrival_date"])
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    df["age"]            = pd.to_numeric(df["age"], errors="coerce").astype("Int64")
    df["satisfaction"]   = pd.to_numeric(df["satisfaction"], errors="coerce").astype("Int64")
    df["service"]        = df["service"].str.strip()

    # Derived: length of stay in days
    df["length_of_stay"] = (df["departure_date"] - df["arrival_date"]).dt.days

    # Remove rows where departure < arrival
    before = len(df)
    df = df[df["length_of_stay"] >= 0]
    print(f"            Dropped {before - len(df):,} rows with invalid stay dates.")

    df = df[["patient_id", "name", "age", "arrival_date", "departure_date",
             "length_of_stay", "service", "satisfaction"]]

    print(f"            Clean rows: {len(df):,}")
    return df


def clean_staff(df):
    print("[ Step 2c ] Cleaning staff ...")

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["staff_id", "role", "service"])
    df["staff_first_name"] = df["staff_first_name"].str.strip()
    df["staff_last_name"]  = df["staff_last_name"].str.strip()
    df["role"]             = df["role"].str.strip()
    df["service"]          = df["service"].str.strip()

    df = df[["staff_id", "staff_first_name", "staff_last_name", "role", "service"]]
    print(f"            Clean rows: {len(df):,}")
    return df


def clean_schedule(df):
    print("[ Step 2d ] Cleaning staff_schedule ...")

    # The raw CSV has a column-shift bug:
    # Header: week, staff_id, first_name, last_name, role(empty), service(=role), present(=service), present.1(=0/1)
    # Fix: drop the empty 'role' col, rename remaining columns correctly.
    df = df.drop(columns=["role"])
    df.columns = ["week", "staff_id", "staff_first_name", "staff_last_name",
                  "role", "service", "present"]

    df["week"]    = df["week"].astype(int)
    df["present"] = pd.to_numeric(df["present"], errors="coerce").fillna(0).astype(int)
    df["role"]    = df["role"].str.strip()
    df["service"] = df["service"].str.strip()

    df = df[["week", "staff_id", "role", "service", "present"]]
    print(f"            Clean rows: {len(df):,}")
    return df


# ── Step 3 : Save clean CSVs ───────────────────────────────────────────────
def save_clean(df, filename):
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"            Saved → {path}")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Hospital Bed Management — Load, Clean & Transform")
    print("=" * 60)

    bed_metrics_raw, patients_raw, staff_raw, schedule_raw = load_raw()

    bed_metrics = clean_bed_metrics(bed_metrics_raw)
    patients    = clean_patients(patients_raw)
    staff       = clean_staff(staff_raw)
    schedule    = clean_schedule(schedule_raw)

    print("[ Step 3 ]  Saving clean CSVs ...")
    save_clean(bed_metrics, "bed_metrics_clean.csv")
    save_clean(patients,    "patients_clean.csv")
    save_clean(staff,       "staff_clean.csv")
    save_clean(schedule,    "schedule_clean.csv")

    print()
    print("Clean CSVs saved. Next steps — run in order:")
    print("  1. psql -U postgres -f sql/00_create_database.sql")
    print("  2. psql -U postgres -d hospital_db -f sql/schema.sql")
    print("  3. psql -U postgres -d hospital_db -f sql/load_data.sql")
