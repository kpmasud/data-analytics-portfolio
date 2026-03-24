"""
=============================================================================
PROJECT  : Movie Data Analysis
FILE     : python/00_load_clean_transform.py
PURPOSE  : Load raw CSVs → clean & transform → save clean CSVs
           Database creation and data loading is handled by SQL:
             1. psql -U postgres             -f sql/00_create_database.sql
             2. psql -U postgres -d movie_data -f sql/schema.sql
             3. psql -U postgres -d movie_data -f sql/load_data.sql
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
    print(f"  Loaded  {filename:<35} {len(df):>4} rows  |  {df.shape[1]} columns")
    return df


def save_clean(df, filename):
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  Saved   {filename:<35} {len(df):>4} rows")


# ── directors ────────────────────────────────────────────────────────────────
def clean_directors(df):
    # strip whitespace from string columns
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()
    # ensure date format
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce").dt.strftime("%Y-%m-%d")
    # fill missing nationality with Unknown
    df["nationality"] = df["nationality"].fillna("Unknown")
    return df[["director_id", "first_name", "last_name", "date_of_birth", "nationality"]]


# ── actors ────────────────────────────────────────────────────────────────────
def clean_actors(df):
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce").dt.strftime("%Y-%m-%d")
    # gender should be M or F only
    df["gender"] = df["gender"].str.upper().where(df["gender"].str.upper().isin(["M", "F"]))
    return df[["actor_id", "first_name", "last_name", "gender", "date_of_birth"]]


# ── movies ────────────────────────────────────────────────────────────────────
def clean_movies(df):
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()
    df["release_date"]  = pd.to_datetime(df["release_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["movie_length"]  = pd.to_numeric(df["movie_length"], errors="coerce").astype("Int64")
    df["director_id"]   = pd.to_numeric(df["director_id"], errors="coerce").astype("Int64")

    before = len(df)
    df = df.dropna(subset=["movie_name"])
    if before != len(df):
        print(f"  Dropped {before - len(df)} rows with missing movie_name.")
    return df[["movie_id", "movie_name", "movie_length", "movie_lang", "release_date", "age_certificate", "director_id"]]


# ── movie_revenues ────────────────────────────────────────────────────────────
def clean_movie_revenues(df):
    df["domestic_takings"]      = pd.to_numeric(df["domestic_takings"],      errors="coerce")
    df["international_takings"] = pd.to_numeric(df["international_takings"], errors="coerce")
    # drop rows where both values are NULL (no meaningful data)
    before = len(df)
    df = df.dropna(subset=["domestic_takings", "international_takings"], how="all")
    if before != len(df):
        print(f"  Dropped {before - len(df)} revenue rows with no takings data.")
    return df[["revenue_id", "movie_id", "domestic_takings", "international_takings"]]


# ── movies_actors (junction) ──────────────────────────────────────────────────
def clean_movies_actors(df):
    df = df.drop_duplicates()
    return df[["movie_id", "actor_id"]]


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Data — Load, Clean & Transform")
    print("=" * 60)

    print("\n[ Step 1 ]  Loading raw CSVs ...")
    df_directors     = load_raw("directors_raw.csv")
    df_actors        = load_raw("actors_raw.csv")
    df_movies        = load_raw("movies_raw.csv")
    df_revenues      = load_raw("movie_revenues_raw.csv")
    df_movies_actors = load_raw("movies_actors_raw.csv")

    print("\n[ Step 2 ]  Cleaning & transforming ...")
    df_directors     = clean_directors(df_directors)
    df_actors        = clean_actors(df_actors)
    df_movies        = clean_movies(df_movies)
    df_revenues      = clean_movie_revenues(df_revenues)
    df_movies_actors = clean_movies_actors(df_movies_actors)

    print("\n[ Step 3 ]  Saving clean CSVs ...")
    save_clean(df_directors,     "directors_clean.csv")
    save_clean(df_actors,        "actors_clean.csv")
    save_clean(df_movies,        "movies_clean.csv")
    save_clean(df_revenues,      "movie_revenues_clean.csv")
    save_clean(df_movies_actors, "movies_actors_clean.csv")

    print()
    print("Clean CSVs saved. Next steps — run in order:")
    print("  1. psql -U postgres -f sql/00_create_database.sql")
    print("  2. psql -U postgres -d movie_data -f sql/schema.sql")
    print("  3. psql -U postgres -d movie_data -f sql/load_data.sql")
