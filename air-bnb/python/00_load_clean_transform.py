"""
=============================================================================
PROJECT  : AirBNB NYC Market Analysis
FILE     : python/00_load_clean_transform.py
PURPOSE  : Load raw CSV → clean & transform → save airbnb_clean.csv
           Database creation and data loading is handled by SQL:
             1. psql -U postgres          -f sql/00_create_database.sql
             2. psql -U postgres -d airbnb_nyc -f sql/schema.sql
             3. psql -U postgres -d airbnb_nyc -f sql/load_data.sql
=============================================================================
"""

import os
import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV   = os.path.join(BASE_DIR, "data", "airbnb_raw.csv")
CLEAN_CSV = os.path.join(BASE_DIR, "data", "airbnb_clean.csv")


# ── Step 1 : Load raw CSV ──────────────────────────────────────────────────────
def load_raw(path):
    print("[ Step 1 ]  Loading raw CSV ...")
    df = pd.read_csv(path)
    print(f"            {len(df):,} rows  |  {df.shape[1]} columns")
    return df


# ── Step 2 : Clean & Transform ────────────────────────────────────────────────
def clean_transform(df):
    print("[ Step 2 ]  Cleaning & transforming ...")

    # --- rename columns to match DB schema ---
    df = df.rename(columns={
        "Host Id":                       "host_id",
        "Host Since":                    "host_since",
        "Name":                          "listing_name",
        "Neighbourhood":                 "neighbourhood",
        "Property Type":                 "property_type",
        "Review Scores Rating (bin)":    "review_score_bin",
        "Room Type":                     "room_type",
        "Zipcode":                       "zipcode",
        "Beds":                          "beds",
        "Number of Records":             "number_of_records",
        "Number Of Reviews":             "number_of_reviews",
        "Price":                         "price",
        "Review Scores Rating":          "review_score_rating",
    })

    # --- strip whitespace from string columns ---
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # --- drop rows missing critical fields ---
    before = len(df)
    df = df.dropna(subset=["price", "room_type", "neighbourhood", "property_type"])
    print(f"            Dropped {before - len(df)} rows with nulls in critical columns.")

    # --- price: remove extreme outliers (keep 1st–99th percentile) ---
    p1, p99 = df["price"].quantile([0.01, 0.99])
    before = len(df)
    df = df[(df["price"] >= p1) & (df["price"] <= p99)]
    print(f"            Dropped {before - len(df)} price outliers (kept ${p1:.0f}–${p99:.0f}).")

    # --- host_since: parse to ISO date string (YYYY-MM-DD) ---
    df["host_since"] = pd.to_datetime(df["host_since"], errors="coerce").dt.strftime("%Y-%m-%d")

    # --- zipcode: cast to string, strip decimal ---
    df["zipcode"] = df["zipcode"].apply(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )

    # --- beds: fill missing with median ---
    df["beds"] = df["beds"].fillna(df["beds"].median())

    # --- number_of_records: fill missing with 1 ---
    df["number_of_records"] = df["number_of_records"].fillna(1).astype(int)

    # --- number_of_reviews: fill missing with 0 ---
    df["number_of_reviews"] = df["number_of_reviews"].fillna(0).astype(int)

    # --- price: ensure int ---
    df["price"] = df["price"].astype(int)

    # --- reorder columns to match table schema ---
    df = df[[
        "host_id", "host_since", "listing_name", "neighbourhood",
        "property_type", "room_type", "zipcode", "beds",
        "number_of_records", "number_of_reviews", "price",
        "review_score_bin", "review_score_rating"
    ]]

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
    print("  AirBNB NYC — Load, Clean & Transform")
    print("=" * 60)

    df_raw   = load_raw(RAW_CSV)
    df_clean = clean_transform(df_raw)
    save_clean(df_clean, CLEAN_CSV)

    print()
    print("Clean CSV saved. Next steps — run in order:")
    print("  1. psql -U postgres -f sql/00_create_database.sql")
    print("  2. psql -U postgres -d airbnb_nyc -f sql/schema.sql")
    print("  3. psql -U postgres -d airbnb_nyc -f sql/load_data.sql")
