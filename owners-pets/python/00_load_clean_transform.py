"""
=============================================================================
PROJECT  : Owners & Pets Analysis
FILE     : python/00_load_clean_transform.py
PURPOSE  : Load raw CSVs → clean & transform → save clean CSVs
           Database creation and data loading is handled by SQL:
             1. psql -U postgres               -f sql/00_create_database.sql
             2. psql -U postgres -d owners_pets -f sql/schema.sql
             3. psql -U postgres -d owners_pets -f sql/load_data.sql
=============================================================================
"""

import os
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_raw(filename):
    path = os.path.join(RAW_DIR, filename)
    df   = pd.read_csv(path)
    print(f"  Loaded  {filename:<30} {len(df):>4} rows  |  {df.shape[1]} columns")
    return df


def save_clean(df, filename):
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  Saved   {filename:<30} {len(df):>4} rows")


# ── owners ────────────────────────────────────────────────────────────────────
def clean_owners(df):
    # strip whitespace from all string columns (important for CHAR fields)
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()
    # lowercase email
    df["email"] = df["email"].str.lower()
    # state must be exactly 2 uppercase characters
    df["state"] = df["state"].str.upper().str[:2]
    # city must be exactly 3 uppercase characters
    df["city"] = df["city"].str.upper().str[:3]

    before = len(df)
    df = df.dropna(subset=["first_name", "last_name", "state"])
    if before != len(df):
        print(f"  Dropped {before - len(df)} owner rows with missing critical fields.")

    return df[["id", "first_name", "last_name", "state", "email", "city"]]


# ── pets ──────────────────────────────────────────────────────────────────────
def clean_pets(df):
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()
    # capitalise species and full_name
    df["species"]   = df["species"].str.title()
    df["full_name"] = df["full_name"].str.title()
    # age must be non-negative integer
    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")

    before = len(df)
    df = df.dropna(subset=["species", "owner_id"])
    df = df[df["age"] >= 0]
    if before != len(df):
        print(f"  Dropped {before - len(df)} pet rows with invalid data.")

    return df[["id", "species", "full_name", "age", "owner_id"]]


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Owners & Pets — Load, Clean & Transform")
    print("=" * 60)

    print("\n[ Step 1 ]  Loading raw CSVs ...")
    df_owners = load_raw("owners_raw.csv")
    df_pets   = load_raw("pets_raw.csv")

    print("\n[ Step 2 ]  Cleaning & transforming ...")
    df_owners = clean_owners(df_owners)
    df_pets   = clean_pets(df_pets)

    print(f"\n  Clean owners : {len(df_owners)} rows  |  {df_owners.shape[1]} columns")
    print(f"  Clean pets   : {len(df_pets)} rows  |  {df_pets.shape[1]} columns")

    print("\n[ Step 3 ]  Saving clean CSVs ...")
    save_clean(df_owners, "owners_clean.csv")
    save_clean(df_pets,   "pets_clean.csv")

    print()
    print("Clean CSVs saved. Next steps — run in order:")
    print("  1. psql -U postgres -f sql/00_create_database.sql")
    print("  2. psql -U postgres -d owners_pets -f sql/schema.sql")
    print("  3. psql -U postgres -d owners_pets -f sql/load_data.sql")
