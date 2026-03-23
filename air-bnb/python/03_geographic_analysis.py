"""
=============================================================================
PROJECT  : AirBNB NYC Market Analysis
FILE     : python/03_geographic_analysis.py
PURPOSE  : Analyse listing distribution and pricing across NYC boroughs
           and ZIP codes
           Mirrors: sql/03_geographic_analysis.sql
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
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Listings and price per borough ───────────────────────────────────────
def plot_borough_overview():
    df = query("""
        SELECT
            neighbourhood                               AS borough,
            COUNT(*)                                    AS total_listings,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
            ROUND(AVG(price), 2)                        AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price,
            COUNT(DISTINCT host_id)                     AS unique_hosts
        FROM listings
        GROUP BY neighbourhood
        ORDER BY total_listings DESC
    """)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Borough Overview", fontweight="bold", fontsize=13)
    palette = sns.color_palette("Set2", len(df))

    # Listings count
    bars = axes[0].bar(df["borough"], df["total_listings"], color=palette)
    for bar, pct in zip(bars, df["pct_of_total"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 100,
                     f"{pct}%", ha="center", va="bottom", fontsize=9)
    axes[0].set_title("Total Listings")
    axes[0].set_ylabel("Listings")
    axes[0].set_xlabel("")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    axes[0].tick_params(axis="x", rotation=20)

    # Median price
    bars2 = axes[1].bar(df["borough"], df["median_price"], color=palette)
    for bar in bars2:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 2,
                     f"${bar.get_height():.0f}", ha="center", va="bottom", fontsize=9)
    axes[1].set_title("Median Nightly Price")
    axes[1].set_ylabel("Price (USD)")
    axes[1].set_xlabel("")
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    axes[1].tick_params(axis="x", rotation=20)

    # Unique hosts
    bars3 = axes[2].bar(df["borough"], df["unique_hosts"], color=palette)
    for bar in bars3:
        axes[2].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 50,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)
    axes[2].set_title("Unique Hosts")
    axes[2].set_ylabel("Hosts")
    axes[2].set_xlabel("")
    axes[2].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    axes[2].tick_params(axis="x", rotation=20)

    plt.tight_layout()
    save(fig, "03a_borough_overview.png")


# ── Q2 : Top 15 ZIP codes by listing count ────────────────────────────────────
def plot_top_zipcodes_by_listings():
    df = query("""
        SELECT
            zipcode,
            neighbourhood                               AS borough,
            COUNT(*)                                    AS total_listings,
            ROUND(AVG(price), 2)                        AS avg_price,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price
        FROM listings
        WHERE zipcode IS NOT NULL
        GROUP BY zipcode, neighbourhood
        ORDER BY total_listings DESC
        LIMIT 15
    """)

    fig, ax = plt.subplots(figsize=(12, 6))
    palette = {b: c for b, c in zip(
        df["borough"].unique(),
        sns.color_palette("Set2", df["borough"].nunique())
    )}
    colors = df["borough"].map(palette)
    bars = ax.barh(df["zipcode"].astype(str), df["total_listings"], color=colors)
    for bar in bars:
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():,.0f}", va="center", fontsize=9)
    ax.set_title("Top 15 ZIP Codes by Number of Listings", fontweight="bold")
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("ZIP Code")
    ax.invert_yaxis()

    # Legend for boroughs
    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=b) for b, c in palette.items()]
    ax.legend(handles=handles, title="Borough", loc="lower right")
    save(fig, "03b_top_zipcodes_by_listings.png")


# ── Q3 : Most expensive ZIP codes ─────────────────────────────────────────────
def plot_expensive_zipcodes():
    df = query("""
        SELECT
            zipcode,
            neighbourhood                               AS borough,
            COUNT(*)                                    AS total_listings,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price)                        AS median_price
        FROM listings
        WHERE zipcode IS NOT NULL
        GROUP BY zipcode, neighbourhood
        HAVING COUNT(*) >= 20
        ORDER BY median_price DESC
        LIMIT 15
    """)

    fig, ax = plt.subplots(figsize=(12, 6))
    palette = {b: c for b, c in zip(
        df["borough"].unique(),
        sns.color_palette("flare", df["borough"].nunique())
    )}
    colors = df["borough"].map(palette)
    bars = ax.barh(df["zipcode"].astype(str), df["median_price"], color=colors)
    for bar in bars:
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                f"${bar.get_width():,.0f}", va="center", fontsize=9)
    ax.set_title("Top 15 Most Expensive ZIP Codes (min 20 listings)", fontweight="bold")
    ax.set_xlabel("Median Nightly Price (USD)")
    ax.set_ylabel("ZIP Code")
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    ax.invert_yaxis()

    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=b) for b, c in palette.items()]
    ax.legend(handles=handles, title="Borough", loc="lower right")
    save(fig, "03c_expensive_zipcodes.png")


# ── Q4 : Listings per host — commercialisation by borough ─────────────────────
def plot_listings_per_host():
    df = query("""
        SELECT
            neighbourhood                               AS borough,
            COUNT(*)                                    AS total_listings,
            COUNT(DISTINCT host_id)                     AS unique_hosts,
            ROUND(COUNT(*) * 1.0 /
                COUNT(DISTINCT host_id), 2)             AS listings_per_host,
            ROUND(AVG(price), 2)                        AS avg_price
        FROM listings
        GROUP BY neighbourhood
        ORDER BY listings_per_host DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    palette = sns.color_palette("viridis", len(df))
    bars = ax.bar(df["borough"], df["listings_per_host"], color=palette)
    for bar, val in zip(bars, df["listings_per_host"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.2f}", ha="center", va="bottom", fontsize=11)
    ax.set_title("Average Listings per Host by Borough\n(Higher = more commercial activity)",
                 fontweight="bold")
    ax.set_ylabel("Listings per Host")
    ax.set_xlabel("")
    save(fig, "03d_listings_per_host_by_borough.png")


# ── Q5 : Borough price ranking (vs city average) ──────────────────────────────
def plot_borough_price_vs_city_avg():
    df = query("""
        SELECT
            neighbourhood                               AS borough,
            ROUND(AVG(price), 2)                        AS avg_price,
            RANK() OVER (ORDER BY AVG(price) DESC)      AS price_rank,
            ROUND(AVG(price) - AVG(AVG(price)) OVER (), 2) AS diff_from_city_avg
        FROM listings
        GROUP BY neighbourhood
        ORDER BY price_rank
    """)

    city_avg = (df["avg_price"] * (1 / len(df))).sum()  # approximate

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#e74c3c" if d > 0 else "#2ecc71" for d in df["diff_from_city_avg"]]
    bars = ax.bar(df["borough"], df["diff_from_city_avg"], color=colors)
    for bar, val in zip(bars, df["diff_from_city_avg"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (1 if val >= 0 else -3),
                f"${val:+.0f}", ha="center",
                va="bottom" if val >= 0 else "top", fontsize=11)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("Borough Avg Price vs City Average\n(Red = above average, Green = below)",
                 fontweight="bold")
    ax.set_ylabel("Difference from City Avg (USD)")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:+,.0f}"))
    save(fig, "03e_borough_vs_city_avg_price.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AirBNB NYC — Geographic & Neighbourhood Analysis")
    print("=" * 60)
    plot_borough_overview()
    plot_top_zipcodes_by_listings()
    plot_expensive_zipcodes()
    plot_listings_per_host()
    plot_borough_price_vs_city_avg()
    print("\nGeographic analysis complete.")
