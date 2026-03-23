"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/02_brand_model_analysis.py
PURPOSE  : Run brand and model analysis queries and produce charts
           Mirrors: sql/02_brand_model_analysis.sql
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


# ── Q1 : Market share per brand ───────────────────────────────────────────────
def plot_market_share():
    df = query("""
        SELECT brand, COUNT(*) AS listings,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS market_share_pct
        FROM cars GROUP BY brand ORDER BY listings DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Brand Market Share", fontweight="bold", fontsize=13)

    axes[0].pie(df["listings"], labels=df["brand"], autopct="%1.1f%%",
                startangle=140, colors=sns.color_palette("tab10", len(df)))
    axes[0].set_title("Share of Total Listings")

    sns.barplot(data=df, x="brand", y="listings", palette="viridis", ax=axes[1])
    axes[1].set_title("Total Listings per Brand")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Listings")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    save(fig, "02a_brand_market_share.png")


# ── Q2 : Top 10 most listed models ────────────────────────────────────────────
def plot_top_models_by_count():
    df = query("""
        SELECT brand || ' ' || model AS brand_model,
               COUNT(*) AS listings,
               ROUND(AVG(price)::NUMERIC, 0) AS avg_price
        FROM cars GROUP BY brand, model
        ORDER BY listings DESC LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = sns.barplot(data=df, x="brand_model", y="listings", palette="Blues_d", ax=ax)
    ax.set_title("Top 10 Most Listed Car Models", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("Number of Listings")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "02b_top_models_by_count.png")


# ── Q3 : Top 10 most expensive models ─────────────────────────────────────────
def plot_top_models_expensive():
    df = query("""
        SELECT brand || ' ' || model AS brand_model,
               COUNT(*) AS listings,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price
        FROM cars GROUP BY brand, model
        HAVING COUNT(*) >= 50
        ORDER BY median_price DESC LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=df, x="brand_model", y="median_price", palette="rocket", ax=ax)
    ax.set_title("Top 10 Most Expensive Models (min 50 listings)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    save(fig, "02c_top_models_by_price.png")


# ── Q4 : Average mileage per brand ────────────────────────────────────────────
def plot_avg_mileage_by_brand():
    df = query("""
        SELECT brand,
               ROUND(AVG(mileage)::NUMERIC, 0) AS avg_mileage,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mileage) AS median_mileage
        FROM cars GROUP BY brand ORDER BY avg_mileage DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(df))
    ax.bar(x, df["avg_mileage"], color=sns.color_palette("mako", len(df)), label="Avg")
    ax.plot(x, df["median_mileage"], "o--", color="coral", linewidth=2,
            markersize=8, label="Median")
    ax.set_xticks(x)
    ax.set_xticklabels(df["brand"], rotation=20)
    ax.set_title("Average & Median Mileage by Brand", fontweight="bold")
    ax.set_ylabel("Mileage (miles)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend()
    save(fig, "02d_avg_mileage_by_brand.png")


# ── Q5 : Brand × Fuel type heatmap ────────────────────────────────────────────
def plot_brand_fuel_heatmap():
    df = query("""
        SELECT brand, fuel_type, COUNT(*) AS listings
        FROM cars GROUP BY brand, fuel_type
    """)
    pivot = df.pivot(index="brand", columns="fuel_type", values="listings").fillna(0)

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Listings"})
    ax.set_title("Listings by Brand × Fuel Type", fontweight="bold")
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Brand")
    save(fig, "02e_brand_fuel_heatmap.png")


# ── Q6 : Year range per brand ─────────────────────────────────────────────────
def plot_year_range_by_brand():
    df = query("""
        SELECT brand, MIN(year) AS oldest_year, MAX(year) AS newest_year,
               ROUND(AVG(year)::NUMERIC, 1) AS avg_year
        FROM cars GROUP BY brand ORDER BY avg_year DESC
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    for _, row in df.iterrows():
        ax.plot([row["oldest_year"], row["newest_year"]], [row["brand"], row["brand"]],
                "o-", linewidth=3, markersize=8)
    ax.set_title("Stock Year Range per Brand", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Brand")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    save(fig, "02f_year_range_by_brand.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Cars — Brand & Model Analysis")
    print("=" * 60)
    plot_market_share()
    plot_top_models_by_count()
    plot_top_models_expensive()
    plot_avg_mileage_by_brand()
    plot_brand_fuel_heatmap()
    plot_year_range_by_brand()
    print("\nBrand & model analysis complete.")
