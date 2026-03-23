"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/01_price_analysis.py
PURPOSE  : Run price analysis queries against PostgreSQL and produce charts
           Mirrors: sql/01_price_analysis.sql
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

# ── Config ─────────────────────────────────────────────────────────────────────
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


# ── Q1 : Median price per brand ────────────────────────────────────────────────
def plot_price_by_brand():
    df = query("""
        SELECT brand,
               COUNT(*)                                     AS total_listings,
               ROUND(AVG(price)::NUMERIC, 2)                AS avg_price,
               PERCENTILE_CONT(0.5) WITHIN GROUP
                   (ORDER BY price)                         AS median_price
        FROM cars
        GROUP BY brand
        ORDER BY median_price DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Asking Price by Brand", fontweight="bold", fontsize=13)

    sns.barplot(data=df, x="brand", y="median_price", palette="Blues_d", ax=axes[0])
    axes[0].set_title("Median Asking Price (£)")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Price (£)")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    axes[0].tick_params(axis="x", rotation=30)
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 150,
                     f"£{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)

    sns.barplot(data=df, x="brand", y="total_listings", palette="Greens_d", ax=axes[1])
    axes[1].set_title("Total Listings")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Number of Listings")
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    axes[1].tick_params(axis="x", rotation=30)
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    save(fig, "01a_price_by_brand.png")


# ── Q2 : Price by fuel type ────────────────────────────────────────────────────
def plot_price_by_fuel():
    df = query("SELECT fuel_type, price FROM cars")
    order = df.groupby("fuel_type")["price"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="fuel_type", y="price", order=order, palette="Set2", ax=ax,
                flierprops=dict(marker="o", markersize=2, alpha=0.3))
    ax.set_title("Price Distribution by Fuel Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    save(fig, "01b_price_by_fuel_type.png")


# ── Q3 : Price by transmission ────────────────────────────────────────────────
def plot_price_by_transmission():
    df = query("""
        SELECT transmission,
               COUNT(*)                                     AS listings,
               ROUND(AVG(price)::NUMERIC, 2)                AS avg_price,
               PERCENTILE_CONT(0.5) WITHIN GROUP
                   (ORDER BY price)                         AS median_price
        FROM cars
        GROUP BY transmission
        ORDER BY median_price DESC
    """)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(df["transmission"], df["median_price"],
                  color=sns.color_palette("crest", len(df)))
    ax.set_title("Median Price by Transmission Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    for bar, cnt in zip(bars, df["listings"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                f"£{bar.get_height():,.0f}\n({cnt:,} listings)",
                ha="center", va="bottom", fontsize=10)
    ax.set_axisbelow(True)
    save(fig, "01c_price_by_transmission.png")


# ── Q4 : Price bracket breakdown ──────────────────────────────────────────────
def plot_price_buckets():
    df = query("""
        SELECT
            CASE
                WHEN price < 5000                  THEN 'Under £5k'
                WHEN price BETWEEN 5000 AND 9999   THEN '£5k – £10k'
                WHEN price BETWEEN 10000 AND 14999 THEN '£10k – £15k'
                WHEN price BETWEEN 15000 AND 19999 THEN '£15k – £20k'
                WHEN price BETWEEN 20000 AND 29999 THEN '£20k – £30k'
                ELSE '£30k+'
            END                                    AS price_bracket,
            COUNT(*)                               AS listings,
            ROUND(COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (), 1)          AS pct_of_total
        FROM cars
        GROUP BY price_bracket
        ORDER BY MIN(price)
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("RdYlGn_r", len(df))
    bars = ax.bar(df["price_bracket"], df["listings"], color=colors)
    for bar, pct in zip(bars, df["pct_of_total"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                f"{pct}%", ha="center", va="bottom", fontsize=10)
    ax.set_title("Listing Count by Price Bracket", fontweight="bold")
    ax.set_xlabel("Price Range")
    ax.set_ylabel("Number of Listings")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "01d_price_buckets.png")


# ── Q5 : Top 10 most expensive models ─────────────────────────────────────────
def plot_top_models_by_price():
    df = query("""
        SELECT brand || ' ' || model AS brand_model,
               COUNT(*)              AS listings,
               PERCENTILE_CONT(0.5) WITHIN GROUP
                   (ORDER BY price)  AS median_price
        FROM cars
        GROUP BY brand, model
        HAVING COUNT(*) >= 50
        ORDER BY median_price DESC
        LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=df, x="brand_model", y="median_price", palette="magma", ax=ax)
    ax.set_title("Top 10 Models by Median Price (min 50 listings)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("Median Price (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    save(fig, "01e_top_models_by_price.png")


# ── Q6 : Brand × Transmission heatmap ─────────────────────────────────────────
def plot_brand_transmission_heatmap():
    df = query("""
        SELECT brand, transmission,
               PERCENTILE_CONT(0.5) WITHIN GROUP
                   (ORDER BY price) AS median_price
        FROM cars
        GROUP BY brand, transmission
    """)
    pivot = df.pivot(index="brand", columns="transmission", values="median_price")

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Median Price (£)"})
    ax.set_title("Median Price: Brand × Transmission", fontweight="bold")
    ax.set_xlabel("Transmission")
    ax.set_ylabel("Brand")
    save(fig, "01f_brand_transmission_heatmap.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Cars — Price Analysis")
    print("=" * 60)
    plot_price_by_brand()
    plot_price_by_fuel()
    plot_price_by_transmission()
    plot_price_buckets()
    plot_top_models_by_price()
    plot_brand_transmission_heatmap()
    print("\nPrice analysis complete.")
