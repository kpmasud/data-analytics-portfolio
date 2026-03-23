"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/00_load_clean_transform.py
PURPOSE  : Merge 9 brand CSVs → clean & transform → save cars_clean.csv
           Database creation and data loading is handled by SQL:
             1. psql -U postgres             -f sql/00_create_database.sql
             2. psql -U postgres -d cars_uk  -f sql/schema.sql
             3. psql -U postgres -d cars_uk  -f sql/load_data.sql
=============================================================================
"""

import os
import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR   = os.path.join(BASE_DIR, "data", "raw")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "cars_clean.csv")

BRAND_MAP = {
    "audi.csv":     "Audi",
    "bmw.csv":      "BMW",
    "ford.csv":     "Ford",
    "hyundi.csv":   "Hyundai",
    "merc.csv":     "Mercedes",
    "skoda.csv":    "Skoda",
    "toyota.csv":   "Toyota",
    "vauxhall.csv": "Vauxhall",
    "vw.csv":       "Volkswagen",
}


# ── Step 1 : Load and merge all brand CSVs ────────────────────────────────────
def load_raw(raw_dir):
    print("[ Step 1 ]  Loading and merging brand CSVs ...")
    frames = []
    for filename, brand in BRAND_MAP.items():
        path = os.path.join(raw_dir, filename)
        df = pd.read_csv(path)
        df.insert(0, "brand", brand)
        frames.append(df)
        print(f"            {brand:<12}  {len(df):>6,} rows")
    combined = pd.concat(frames, ignore_index=True)
    print(f"            ─────────────────────────")
    print(f"            Total        {len(combined):>6,} rows  |  {combined.shape[1]} columns")
    return combined


# ── Step 2 : Clean & Transform ────────────────────────────────────────────────
def clean_transform(df):
    print("[ Step 2 ]  Cleaning & transforming ...")

    # --- rename columns to snake_case ---
    df = df.rename(columns={
        "fuelType":   "fuel_type",
        "engineSize": "engine_size",
    })

    # --- strip whitespace from string columns ---
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # --- drop rows missing critical fields ---
    before = len(df)
    df = df.dropna(subset=["price", "year", "transmission", "mileage", "fuel_type", "engine_size"])
    print(f"            Dropped {before - len(df):,} rows with nulls in critical columns.")

    # --- drop rows with zero or negative price / engine_size ---
    before = len(df)
    df = df[(df["price"] > 0) & (df["engine_size"] > 0) & (df["mileage"] >= 0)]
    print(f"            Dropped {before - len(df):,} rows with invalid price/engine_size/mileage.")

    # --- year: keep 1998–2020 (data quality) ---
    before = len(df)
    df = df[(df["year"] >= 1998) & (df["year"] <= 2020)]
    print(f"            Dropped {before - len(df):,} rows outside year range 1998–2020.")

    # --- price: remove extreme outliers (1st–99th percentile) ---
    p1, p99 = df["price"].quantile([0.01, 0.99])
    before = len(df)
    df = df[(df["price"] >= p1) & (df["price"] <= p99)]
    print(f"            Dropped {before - len(df):,} price outliers (kept £{p1:,.0f}–£{p99:,.0f}).")

    # --- mileage: cap at 99th percentile ---
    m99 = df["mileage"].quantile(0.99)
    before = len(df)
    df = df[df["mileage"] <= m99]
    print(f"            Dropped {before - len(df):,} mileage outliers (kept ≤ {m99:,.0f} miles).")

    # --- cast types ---
    df["price"]    = df["price"].astype(int)
    df["mileage"]  = df["mileage"].astype(int)
    df["year"]     = df["year"].astype(int)
    df["engine_size"] = df["engine_size"].astype(float)
    if "tax" in df.columns:
        df["tax"] = pd.to_numeric(df["tax"], errors="coerce").round(0).astype("Int64")
    if "mpg" in df.columns:
        df["mpg"] = pd.to_numeric(df["mpg"], errors="coerce")

    # --- reorder columns to match DB schema ---
    df = df[["brand", "model", "year", "price", "transmission",
             "mileage", "fuel_type", "tax", "mpg", "engine_size"]]

    print(f"            Clean dataset: {len(df):,} rows  |  {df.shape[1]} columns")
    return df


# ── Step 3 : Save clean CSV ────────────────────────────────────────────────────
def save_clean(df, path):
    print("[ Step 3 ]  Saving clean CSV ...")
    df.to_csv(path, index=False)
    print(f"            Saved → {path}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Car Market — Load, Clean & Transform")
    print("=" * 60)

    df_raw   = load_raw(RAW_DIR)
    df_clean = clean_transform(df_raw)
    save_clean(df_clean, CLEAN_CSV)

    print()
    print("Clean CSV saved. Next steps — run in order:")
    print("  1. psql -U postgres -f sql/00_create_database.sql")
    print("  2. psql -U postgres -d cars_uk -f sql/schema.sql")
    print("  3. psql -U postgres -d cars_uk -f sql/load_data.sql")
