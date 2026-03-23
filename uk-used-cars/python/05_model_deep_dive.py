"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/05_model_deep_dive.py
PURPOSE  : Deep-dive into individual car models — top models per brand,
           value, affordability, depreciation, and fuel efficiency
           Mirrors: sql/05_model_deep_dive.sql
=============================================================================
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PG = dict(
    host     = os.getenv("PG_HOST", "localhost"),
    port     = int(os.getenv("PG_PORT", 5432)),
    user     = os.getenv("PG_USER", "postgres"),
    password = os.getenv("PG_PASSWORD", ""),
    dbname   = os.getenv("PG_DATABASE", "cars_uk"),
)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Top 3 models per brand ───────────────────────────────────────────────
def plot_top_models_per_brand():
    df = query("""
        WITH ranked AS (
            SELECT brand, model, COUNT(*) AS listings,
                   ROUND(AVG(price)::NUMERIC, 0) AS avg_price,
                   RANK() OVER (PARTITION BY brand ORDER BY COUNT(*) DESC) AS rnk
            FROM cars GROUP BY brand, model
        )
        SELECT brand, model, listings, avg_price
        FROM ranked WHERE rnk <= 3
        ORDER BY brand, listings DESC
    """)
    df["label"] = df["model"]

    brands = df["brand"].unique()
    n = len(brands)
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle("Top 3 Most Listed Models per Brand", fontweight="bold", fontsize=14)
    axes = axes.flatten()

    for i, brand in enumerate(brands):
        sub = df[df["brand"] == brand]
        axes[i].barh(sub["label"], sub["listings"],
                     color=sns.color_palette("tab10", 3))
        axes[i].set_title(brand, fontweight="bold")
        axes[i].set_xlabel("Listings")
        axes[i].xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        for j, row in sub.iterrows():
            axes[i].text(row["listings"] + 5, j - sub.index[0],
                         f"{row['listings']:,}", va="center", fontsize=9)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    save(fig, "05a_top_models_per_brand.png")


# ── Q2 : Best value models — price per mile ───────────────────────────────────
def plot_best_value_models():
    df = query("""
        SELECT brand || ' ' || model AS brand_model,
               COUNT(*) AS listings,
               ROUND(AVG(price)::NUMERIC, 0) AS avg_price,
               ROUND(AVG(mileage)::NUMERIC, 0) AS avg_mileage,
               ROUND(AVG(price)::NUMERIC / NULLIF(AVG(mileage), 0), 4) AS price_per_mile
        FROM cars
        GROUP BY brand, model
        HAVING COUNT(*) >= 100
        ORDER BY price_per_mile ASC
        LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=df, x="brand_model", y="price_per_mile",
                palette="YlGn_r", ax=ax)
    ax.set_title("Best Value Models — Lowest Price per Mile (min 100 listings)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("£ per Mile")
    save(fig, "05b_best_value_models.png")


# ── Q3 : Most affordable models ───────────────────────────────────────────────
def plot_affordable_models():
    df = query("""
        SELECT brand || ' ' || model AS brand_model,
               COUNT(*) AS listings,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
               ROUND(AVG(mileage)::NUMERIC, 0) AS avg_mileage
        FROM cars
        GROUP BY brand, model
        HAVING COUNT(*) >= 50
            AND PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) <= 8000
        ORDER BY median_price ASC
        LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = sns.barplot(data=df, x="brand_model", y="median_price",
                       palette="Greens_d", ax=ax)
    ax.set_title("Most Affordable Models under £8,000 (min 50 listings)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    save(fig, "05c_affordable_models.png")


# ── Q4 : Model depreciation 2019 → 2015 ──────────────────────────────────────
def plot_model_depreciation():
    df = query("""
        WITH new_stock AS (
            SELECT brand, model,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS price_2019
            FROM cars WHERE year = 2019
            GROUP BY brand, model HAVING COUNT(*) >= 10
        ),
        old_stock AS (
            SELECT brand, model,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS price_2015
            FROM cars WHERE year = 2015
            GROUP BY brand, model HAVING COUNT(*) >= 10
        )
        SELECT n.brand || ' ' || n.model AS brand_model,
               ROUND(n.price_2019::NUMERIC, 0) AS price_2019,
               ROUND(o.price_2015::NUMERIC, 0) AS price_2015,
               ROUND(((n.price_2019 - o.price_2015) * 100.0 /
                   NULLIF(n.price_2019, 0))::NUMERIC, 1) AS pct_drop
        FROM new_stock n JOIN old_stock o USING (brand, model)
        ORDER BY pct_drop DESC LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(df))
    ax.bar([i - 0.2 for i in x], df["price_2019"], width=0.35,
           label="2019 Stock Price", color="steelblue")
    ax.bar([i + 0.2 for i in x], df["price_2015"], width=0.35,
           label="2015 Stock Price", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(df["brand_model"], rotation=35, ha="right")
    ax.set_title("Model Depreciation: 2019 Stock vs 2015 Stock (Top 12)", fontweight="bold")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    ax.legend()
    plt.tight_layout()
    save(fig, "05d_model_depreciation.png")


# ── Q5 : Model fuel efficiency league ─────────────────────────────────────────
def plot_fuel_efficiency_league():
    df = query("""
        SELECT brand || ' ' || model AS brand_model, fuel_type,
               ROUND(AVG(mpg)::NUMERIC, 1) AS avg_mpg,
               COUNT(*) AS listings
        FROM cars WHERE mpg IS NOT NULL AND mpg > 0
        GROUP BY brand, model, fuel_type
        HAVING COUNT(*) >= 50
        ORDER BY avg_mpg DESC LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    palette = {"Diesel": "steelblue", "Petrol": "coral", "Hybrid": "seagreen",
               "Electric": "purple", "Other": "grey"}
    colors = [palette.get(ft, "grey") for ft in df["fuel_type"]]
    bars = ax.barh(df["brand_model"], df["avg_mpg"], color=colors)
    for bar, mpg in zip(bars, df["avg_mpg"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{mpg:.1f} mpg", va="center", fontsize=9)
    ax.set_title("Most Fuel-Efficient Models (min 50 listings)", fontweight="bold")
    ax.set_xlabel("Average MPG")

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=v, label=k) for k, v in palette.items()
                       if k in df["fuel_type"].values]
    ax.legend(handles=legend_elements, title="Fuel Type")
    plt.tight_layout()
    save(fig, "05e_fuel_efficiency_league.png")


# ── Q6 : Price ranking within each brand (top 5 per brand) ───────────────────
def plot_price_rank_within_brand():
    df = query("""
        WITH ranked AS (
            SELECT brand, model, COUNT(*) AS listings,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
                   DENSE_RANK() OVER (
                       PARTITION BY brand
                       ORDER BY PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) DESC
                   ) AS price_rank
            FROM cars GROUP BY brand, model
            HAVING COUNT(*) >= 30
        )
        SELECT brand, model, listings, ROUND(median_price::NUMERIC, 0) AS median_price, price_rank
        FROM ranked WHERE price_rank <= 5
        ORDER BY brand, price_rank
    """)

    brands = df["brand"].unique()
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle("Top 5 Priciest Models per Brand (min 30 listings)", fontweight="bold", fontsize=14)
    axes = axes.flatten()

    for i, brand in enumerate(brands):
        sub = df[df["brand"] == brand].head(5)
        axes[i].barh(sub["model"][::-1], sub["median_price"][::-1],
                     color=sns.color_palette("rocket", 5))
        axes[i].set_title(brand, fontweight="bold")
        axes[i].set_xlabel("Median Price (£)")
        axes[i].xaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    save(fig, "05f_price_rank_within_brand.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Cars — Model Deep-Dive Analysis")
    print("=" * 60)
    plot_top_models_per_brand()
    plot_best_value_models()
    plot_affordable_models()
    plot_model_depreciation()
    plot_fuel_efficiency_league()
    plot_price_rank_within_brand()
    print("\nModel deep-dive analysis complete.")
