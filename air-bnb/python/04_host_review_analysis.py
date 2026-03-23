"""
=============================================================================
PROJECT  : AirBNB NYC Market Analysis
FILE     : python/04_host_review_analysis.py
PURPOSE  : Analyse host activity, tenure, and guest review patterns
           Mirrors: sql/04_host_review_analysis.sql
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


# ── Q1 : New hosts per year ────────────────────────────────────────────────────
def plot_new_hosts_per_year():
    df = query("""
        SELECT
            EXTRACT(YEAR FROM host_since)::INT          AS join_year,
            COUNT(DISTINCT host_id)                     AS new_hosts
        FROM listings
        WHERE host_since IS NOT NULL
          AND EXTRACT(YEAR FROM host_since) >= 2008
        GROUP BY join_year
        ORDER BY join_year
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.fill_between(df["join_year"], df["new_hosts"], alpha=0.2,
                    color=sns.color_palette("Set2")[0])
    ax.plot(df["join_year"], df["new_hosts"], marker="o",
            color=sns.color_palette("Set2")[0], linewidth=2)
    for x, y in zip(df["join_year"], df["new_hosts"]):
        ax.text(x, y + 30, f"{y:,}", ha="center", fontsize=9)
    ax.set_title("New Hosts Joining Airbnb NYC Per Year", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("New Hosts")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "04a_new_hosts_per_year.png")


# ── Q2 : Host segmentation ────────────────────────────────────────────────────
def plot_host_segmentation():
    df = query("""
        SELECT
            CASE
                WHEN listing_count = 1             THEN 'Single listing'
                WHEN listing_count BETWEEN 2 AND 5 THEN '2–5 listings'
                WHEN listing_count BETWEEN 6 AND 10 THEN '6–10 listings'
                ELSE '11+ listings'
            END                                     AS host_segment,
            COUNT(*)                                AS host_count,
            ROUND(COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (), 1)           AS pct_of_hosts
        FROM (
            SELECT host_id, COUNT(*) AS listing_count
            FROM listings
            GROUP BY host_id
        ) hc
        GROUP BY host_segment
        ORDER BY MIN(listing_count)
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Host Portfolio Size Segmentation", fontweight="bold", fontsize=13)
    palette = sns.color_palette("Set2", len(df))

    bars = axes[0].bar(df["host_segment"], df["host_count"], color=palette)
    for bar, pct in zip(bars, df["pct_of_hosts"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 50,
                     f"{pct}%", ha="center", va="bottom", fontsize=10)
    axes[0].set_title("Host Count by Segment")
    axes[0].set_ylabel("Number of Hosts")
    axes[0].set_xlabel("")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    axes[1].pie(df["host_count"], labels=df["host_segment"],
                autopct="%1.1f%%", startangle=140, colors=palette,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    axes[1].set_title("Share by Segment")

    plt.tight_layout()
    save(fig, "04b_host_segmentation.png")


# ── Q3 : Review score distribution ───────────────────────────────────────────
def plot_review_score_distribution():
    df_raw = query("""
        SELECT review_score_rating
        FROM listings
        WHERE review_score_rating IS NOT NULL
    """)

    df_bands = query("""
        SELECT
            CASE
                WHEN review_score_rating < 60  THEN 'Below 60'
                WHEN review_score_rating BETWEEN 60 AND 69 THEN '60–69'
                WHEN review_score_rating BETWEEN 70 AND 79 THEN '70–79'
                WHEN review_score_rating BETWEEN 80 AND 89 THEN '80–89'
                WHEN review_score_rating BETWEEN 90 AND 94 THEN '90–94'
                ELSE '95–100'
            END                                         AS score_band,
            COUNT(*)                                    AS listings,
            ROUND(COUNT(*) * 100.0 /
                SUM(COUNT(*)) OVER (), 1)               AS pct_of_total
        FROM listings
        WHERE review_score_rating IS NOT NULL
        GROUP BY score_band
        ORDER BY MIN(review_score_rating)
    """)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Review Score Distribution", fontweight="bold", fontsize=13)

    # Histogram with KDE
    sns.histplot(df_raw["review_score_rating"], bins=25, kde=True,
                 color=sns.color_palette("Set2")[1], ax=axes[0])
    axes[0].axvline(df_raw["review_score_rating"].mean(), color="red",
                    linestyle="--", label=f"Mean: {df_raw['review_score_rating'].mean():.1f}")
    axes[0].legend()
    axes[0].set_title("Score Distribution (Histogram + KDE)")
    axes[0].set_xlabel("Review Score (out of 100)")
    axes[0].set_ylabel("Count")

    # Band breakdown
    palette = sns.color_palette("RdYlGn", len(df_bands))
    bars = axes[1].barh(df_bands["score_band"], df_bands["listings"], color=palette)
    for bar, pct in zip(bars, df_bands["pct_of_total"]):
        axes[1].text(bar.get_width() + 10,
                     bar.get_y() + bar.get_height() / 2,
                     f"{pct}%", va="center", fontsize=10)
    axes[1].set_title("Listings per Score Band")
    axes[1].set_xlabel("Number of Listings")
    axes[1].set_ylabel("Score Band")
    axes[1].xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    plt.tight_layout()
    save(fig, "04c_review_score_distribution.png")


# ── Q4 : Review score by borough ─────────────────────────────────────────────
def plot_review_score_by_borough():
    df = query("""
        SELECT
            neighbourhood                               AS borough,
            ROUND(AVG(review_score_rating), 2)          AS avg_review_score,
            ROUND(AVG(number_of_reviews), 1)            AS avg_num_reviews
        FROM listings
        GROUP BY neighbourhood
        ORDER BY avg_review_score DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Review Metrics by Borough", fontweight="bold", fontsize=13)
    palette = sns.color_palette("Set2", len(df))

    bars = axes[0].bar(df["borough"], df["avg_review_score"], color=palette)
    for bar in bars:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=11)
    axes[0].set_title("Avg Review Score (out of 100)")
    axes[0].set_ylabel("Avg Score")
    axes[0].set_ylim(0, 105)
    axes[0].set_xlabel("")

    bars2 = axes[1].bar(df["borough"], df["avg_num_reviews"], color=palette)
    for bar in bars2:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=11)
    axes[1].set_title("Avg Number of Reviews per Listing")
    axes[1].set_ylabel("Avg Reviews")
    axes[1].set_xlabel("")

    plt.tight_layout()
    save(fig, "04d_review_score_by_borough.png")


# ── Q5 : Host portfolio size vs review score ──────────────────────────────────
def plot_host_size_vs_reviews():
    df = query("""
        SELECT
            CASE
                WHEN listing_count = 1             THEN '1 listing'
                WHEN listing_count BETWEEN 2 AND 5 THEN '2–5 listings'
                WHEN listing_count BETWEEN 6 AND 10 THEN '6–10 listings'
                ELSE '11+ listings'
            END                                     AS host_segment,
            ROUND(AVG(review_score_rating), 2)      AS avg_review_score,
            ROUND(AVG(number_of_reviews), 1)        AS avg_num_reviews,
            ROUND(AVG(price), 2)                    AS avg_price
        FROM listings l
        JOIN (
            SELECT host_id, COUNT(*) AS listing_count
            FROM listings GROUP BY host_id
        ) hc ON l.host_id = hc.host_id
        WHERE review_score_rating IS NOT NULL
        GROUP BY host_segment
        ORDER BY MIN(listing_count)
    """)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Host Portfolio Size vs Performance", fontweight="bold", fontsize=13)
    palette = sns.color_palette("muted", len(df))

    for ax, col, title, fmt in zip(
        axes,
        ["avg_review_score", "avg_num_reviews", "avg_price"],
        ["Avg Review Score", "Avg Number of Reviews", "Avg Price (USD)"],
        ["{x:.0f}", "{x:.0f}", "${x:,.0f}"]
    ):
        bars = ax.bar(df["host_segment"], df[col], color=palette)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() * 1.01,
                    f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=10)
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel(title)
        ax.tick_params(axis="x", rotation=15)

    plt.tight_layout()
    save(fig, "04e_host_size_vs_performance.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AirBNB NYC — Host & Review Analysis")
    print("=" * 60)
    plot_new_hosts_per_year()
    plot_host_segmentation()
    plot_review_score_distribution()
    plot_review_score_by_borough()
    plot_host_size_vs_reviews()
    print("\nHost & Review analysis complete.")
