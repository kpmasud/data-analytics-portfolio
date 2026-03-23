"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/04_depreciation_mileage_analysis.py
PURPOSE  : Run depreciation and mileage analysis and produce charts
           Mirrors: sql/04_depreciation_mileage_analysis.sql
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


# ── Q1 : Depreciation curve (median price by year) ────────────────────────────
def plot_depreciation_curve():
    df = query("""
        SELECT year,
               ROUND(AVG(price)::NUMERIC, 0) AS avg_price,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
               COUNT(*) AS listings
        FROM cars GROUP BY year ORDER BY year
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(df["year"], df["median_price"], alpha=0.2, color="steelblue")
    ax.plot(df["year"], df["median_price"], "o-", color="steelblue",
            linewidth=2.5, markersize=7, label="Median Price")
    ax.plot(df["year"], df["avg_price"], "s--", color="coral",
            linewidth=2, markersize=6, label="Avg Price")
    ax.set_title("Car Depreciation Curve — Median Price by Year", fontweight="bold")
    ax.set_xlabel("Year of Manufacture")
    ax.set_ylabel("Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.legend()
    plt.tight_layout()
    save(fig, "04a_depreciation_curve.png")


# ── Q2 : Median price by mileage band ─────────────────────────────────────────
def plot_price_by_mileage_band():
    df = query("""
        SELECT
            CASE
                WHEN mileage < 10000              THEN 'Under 10k'
                WHEN mileage BETWEEN 10000 AND 24999 THEN '10k – 25k'
                WHEN mileage BETWEEN 25000 AND 49999 THEN '25k – 50k'
                WHEN mileage BETWEEN 50000 AND 74999 THEN '50k – 75k'
                ELSE '75k – 90k'
            END                                  AS mileage_band,
            COUNT(*)                             AS listings,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                 AS median_price
        FROM cars
        GROUP BY mileage_band
        ORDER BY MIN(mileage)
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(df["mileage_band"], df["median_price"],
                  color=sns.color_palette("RdYlGn_r", len(df)))
    for bar, cnt in zip(bars, df["listings"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                f"£{bar.get_height():,.0f}\n({cnt:,})",
                ha="center", va="bottom", fontsize=9)
    ax.set_title("Median Price by Mileage Band", fontweight="bold")
    ax.set_xlabel("Mileage Band")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    save(fig, "04b_price_by_mileage_band.png")


# ── Q3 : Average mileage by brand ─────────────────────────────────────────────
def plot_mileage_by_brand():
    df = query("""
        SELECT brand,
               ROUND(AVG(mileage)::NUMERIC, 0) AS avg_mileage,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mileage) AS median_mileage
        FROM cars GROUP BY brand ORDER BY avg_mileage ASC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x="brand", y="avg_mileage", palette="mako_r", ax=ax)
    ax.plot(range(len(df)), df["median_mileage"], "o--", color="coral",
            linewidth=2, markersize=8, label="Median")
    ax.set_title("Average Mileage by Brand (lowest to highest)", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Mileage (miles)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.tick_params(axis="x", rotation=20)
    ax.legend()
    save(fig, "04c_mileage_by_brand.png")


# ── Q4 : Depreciation rate vs newest stock ────────────────────────────────────
def plot_depreciation_rate():
    df = query("""
        WITH yearly AS (
            SELECT year,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
                   COUNT(*) AS listings
            FROM cars GROUP BY year
        ),
        newest AS (
            SELECT median_price AS base_price FROM yearly
            WHERE year = (SELECT MAX(year) FROM yearly)
        )
        SELECT y.year, y.listings,
               ROUND(y.median_price::NUMERIC, 0) AS median_price,
               ROUND((n.base_price - y.median_price)::NUMERIC, 0) AS price_drop,
               ROUND(((n.base_price - y.median_price) * 100.0 /
                   NULLIF(n.base_price, 0))::NUMERIC, 1) AS pct_depreciation
        FROM yearly y CROSS JOIN newest n
        ORDER BY y.year DESC
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(df["year"], df["pct_depreciation"],
           color=sns.color_palette("Reds_d", len(df)))
    ax.set_title("% Price Depreciation vs Newest Stock (2020)", fontweight="bold")
    ax.set_xlabel("Year of Manufacture")
    ax.set_ylabel("Depreciation vs 2020 Stock (%)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    for i, row in df.iterrows():
        if row["year"] % 3 == 0:
            ax.text(row["year"], row["pct_depreciation"] + 0.5,
                    f"{row['pct_depreciation']:.0f}%",
                    ha="center", va="bottom", fontsize=8)
    save(fig, "04d_depreciation_rate.png")


# ── Q5 : Engine size bands vs price ───────────────────────────────────────────
def plot_engine_vs_price():
    df = query("""
        SELECT
            CASE
                WHEN engine_size < 1.0               THEN 'Under 1.0L'
                WHEN engine_size BETWEEN 1.0 AND 1.4 THEN '1.0L – 1.4L'
                WHEN engine_size BETWEEN 1.5 AND 1.9 THEN '1.5L – 1.9L'
                WHEN engine_size BETWEEN 2.0 AND 2.9 THEN '2.0L – 2.9L'
                ELSE '3.0L+'
            END                                      AS engine_band,
            COUNT(*)                                 AS listings,
            ROUND(AVG(price)::NUMERIC, 0)            AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                     AS median_price
        FROM cars GROUP BY engine_band ORDER BY MIN(engine_size)
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(df))
    bars = ax.bar(x, df["median_price"], color=sns.color_palette("crest", len(df)))
    ax.plot(x, df["avg_price"], "o--", color="tomato", linewidth=2,
            markersize=9, label="Avg Price")
    ax.set_xticks(x)
    ax.set_xticklabels(df["engine_band"])
    ax.set_title("Median Price by Engine Size Band", fontweight="bold")
    ax.set_xlabel("Engine Size")
    ax.set_ylabel("Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    ax.legend()
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                f"£{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)
    save(fig, "04e_engine_size_vs_price.png")


# ── Q6 : High vs low mileage price gap per brand ──────────────────────────────
def plot_mileage_price_gap():
    df = query("""
        SELECT brand,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)
                   FILTER (WHERE mileage < 25000) AS low_mileage_price,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)
                   FILTER (WHERE mileage >= 60000) AS high_mileage_price
        FROM cars GROUP BY brand
    """)
    df["price_gap"] = df["low_mileage_price"] - df["high_mileage_price"]
    df = df.sort_values("price_gap", ascending=False)

    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(df))
    ax.bar(x, df["low_mileage_price"], label="Low Mileage (<25k mi)",
           color="steelblue", alpha=0.8)
    ax.bar(x, df["high_mileage_price"], label="High Mileage (≥60k mi)",
           color="coral", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(df["brand"], rotation=20)
    ax.set_title("Median Price: Low Mileage vs High Mileage Cars by Brand", fontweight="bold")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    ax.legend()
    save(fig, "04f_mileage_price_gap.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Cars — Depreciation & Mileage Analysis")
    print("=" * 60)
    plot_depreciation_curve()
    plot_price_by_mileage_band()
    plot_mileage_by_brand()
    plot_depreciation_rate()
    plot_engine_vs_price()
    plot_mileage_price_gap()
    print("\nDepreciation & mileage analysis complete.")
