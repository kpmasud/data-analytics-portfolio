"""
=============================================================================
PROJECT  : AirBNB NYC Market Analysis
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
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PG = dict(
    host     = os.getenv("PG_HOST", "localhost"),
    port     = int(os.getenv("PG_PORT", 5432)),
    user     = os.getenv("PG_USER", "postgres"),
    password = os.getenv("PG_PASSWORD", ""),
    dbname   = os.getenv("PG_DATABASE", "airbnb_nyc"),
)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)


# ── Helpers ────────────────────────────────────────────────────────────────────
def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Median price per borough ─────────────────────────────────────────────
def plot_price_by_borough():
    df = query("""
        SELECT
            neighbourhood,
            COUNT(*)                                    AS total_listings,
            ROUND(AVG(price), 2)                        AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price
        FROM listings
        GROUP BY neighbourhood
        ORDER BY median_price DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Nightly Price by Borough", fontweight="bold", fontsize=13)

    # Bar — median price
    sns.barplot(data=df, x="neighbourhood", y="median_price",
                palette="Blues_d", ax=axes[0])
    axes[0].set_title("Median Nightly Price")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Price (USD)")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 2,
                     f"${bar.get_height():.0f}",
                     ha="center", va="bottom", fontsize=10)

    # Bar — listing count
    sns.barplot(data=df, x="neighbourhood", y="total_listings",
                palette="Greens_d", ax=axes[1])
    axes[1].set_title("Total Listings")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Number of Listings")
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 50,
                     f"{bar.get_height():,.0f}",
                     ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    save(fig, "01a_price_by_borough.png")


# ── Q2 : Price by room type ────────────────────────────────────────────────────
def plot_price_by_room_type():
    df = query("""
        SELECT
            room_type,
            price
        FROM listings
    """)

    order = df.groupby("room_type")["price"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=df, x="room_type", y="price", order=order,
                palette="Set2", ax=ax,
                flierprops=dict(marker="o", markersize=2, alpha=0.3))
    ax.set_title("Price Distribution by Room Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Nightly Price (USD)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    save(fig, "01b_price_by_room_type.png")


# ── Q3 : Price by beds ─────────────────────────────────────────────────────────
def plot_price_by_beds():
    df = query("""
        SELECT
            beds,
            ROUND(AVG(price), 2)                        AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price,
            COUNT(*)                                    AS listings
        FROM listings
        WHERE beds BETWEEN 1 AND 6
        GROUP BY beds
        ORDER BY beds
    """)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = df["beds"].astype(str)
    bars = ax.bar(x, df["median_price"],
                  color=sns.color_palette("crest", len(df)))
    ax.set_title("Median Nightly Price by Number of Beds", fontweight="bold")
    ax.set_xlabel("Number of Beds")
    ax.set_ylabel("Median Price (USD)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    for bar, cnt in zip(bars, df["listings"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 3,
                f"${bar.get_height():.0f}\n({cnt:,})",
                ha="center", va="bottom", fontsize=9)
    ax.set_axisbelow(True)
    save(fig, "01c_price_by_beds.png")


# ── Q4 : Price by property type ───────────────────────────────────────────────
def plot_price_by_property_type():
    df = query("""
        SELECT
            property_type,
            ROUND(AVG(price), 2)                        AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price,
            COUNT(*)                                    AS listings
        FROM listings
        GROUP BY property_type
        HAVING COUNT(*) >= 10
        ORDER BY median_price DESC
        LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=df, x="property_type", y="median_price",
                palette="magma", ax=ax)
    ax.set_title("Median Price by Property Type (Top 10, min 10 listings)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_xlabel("")
    ax.set_ylabel("Median Price (USD)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    save(fig, "01d_price_by_property_type.png")


# ── Q5 : Price bucket distribution ────────────────────────────────────────────
def plot_price_buckets():
    df = query("""
        SELECT
            CASE
                WHEN price < 50              THEN 'Under $50'
                WHEN price BETWEEN 50 AND 99 THEN '$50–$99'
                WHEN price BETWEEN 100 AND 149 THEN '$100–$149'
                WHEN price BETWEEN 150 AND 199 THEN '$150–$199'
                WHEN price BETWEEN 200 AND 299 THEN '$200–$299'
                ELSE '$300+'
            END                              AS price_bucket,
            COUNT(*)                         AS listings,
            ROUND(COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (), 1)    AS pct_of_total
        FROM listings
        GROUP BY price_bucket
        ORDER BY MIN(price)
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = sns.color_palette("RdYlGn_r", len(df))
    bars = ax.bar(df["price_bucket"], df["listings"], color=colors)
    for bar, pct in zip(bars, df["pct_of_total"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 100,
                f"{pct}%",
                ha="center", va="bottom", fontsize=10)
    ax.set_title("Listing Count by Price Bracket", fontweight="bold")
    ax.set_xlabel("Price Range")
    ax.set_ylabel("Number of Listings")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "01e_price_buckets.png")


# ── Q6 : Heatmap — borough × room type ────────────────────────────────────────
def plot_price_heatmap():
    df = query("""
        SELECT
            neighbourhood,
            room_type,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price
        FROM listings
        GROUP BY neighbourhood, room_type
    """)

    pivot = df.pivot(index="neighbourhood", columns="room_type", values="median_price")

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax,
                cbar_kws={"label": "Median Price (USD)"})
    ax.set_title("Median Nightly Price: Borough × Room Type", fontweight="bold")
    ax.set_xlabel("Room Type")
    ax.set_ylabel("Borough")
    plt.xticks(rotation=20)
    save(fig, "01f_price_heatmap_borough_roomtype.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AirBNB NYC — Price Analysis")
    print("=" * 60)
    plot_price_by_borough()
    plot_price_by_room_type()
    plot_price_by_beds()
    plot_price_by_property_type()
    plot_price_buckets()
    plot_price_heatmap()
    print("\nPrice analysis complete.")
