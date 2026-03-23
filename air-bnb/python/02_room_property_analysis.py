"""
=============================================================================
PROJECT  : AirBNB NYC Market Analysis
FILE     : python/02_room_property_analysis.py
PURPOSE  : Analyse room types and property types — listing counts,
           pricing, and composition across boroughs
           Mirrors: sql/02_room_property_analysis.sql
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


# ── Q1 : Room type distribution ───────────────────────────────────────────────
def plot_room_type_distribution():
    df = query("""
        SELECT
            room_type,
            COUNT(*)                                    AS total_listings,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
            ROUND(AVG(price), 2)                        AS avg_price
        FROM listings
        GROUP BY room_type
        ORDER BY total_listings DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Room Type Overview", fontweight="bold", fontsize=13)

    # Bar chart — listing counts
    colors = sns.color_palette("Set2", len(df))
    bars = axes[0].bar(df["room_type"], df["total_listings"], color=colors)
    for bar, pct in zip(bars, df["pct_of_total"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 100,
                     f"{pct}%", ha="center", va="bottom", fontsize=10)
    axes[0].set_title("Listing Count by Room Type")
    axes[0].set_ylabel("Number of Listings")
    axes[0].set_xlabel("")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    # Pie chart — share
    axes[1].pie(df["total_listings"], labels=df["room_type"],
                autopct="%1.1f%%", startangle=140, colors=colors,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    axes[1].set_title("Share of Listings by Room Type")

    plt.tight_layout()
    save(fig, "02a_room_type_distribution.png")


# ── Q2 : Top 10 property types ────────────────────────────────────────────────
def plot_property_type_top10():
    df = query("""
        SELECT
            property_type,
            COUNT(*)                                    AS total_listings,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
            ROUND(AVG(price), 2)                        AS avg_price
        FROM listings
        GROUP BY property_type
        ORDER BY total_listings DESC
        LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(df["property_type"], df["total_listings"],
                  color=sns.color_palette("coolwarm", len(df)))
    for bar, pct in zip(bars, df["pct_of_total"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 50,
                f"{pct}%", ha="center", va="bottom", fontsize=9)
    ax.set_title("Top 10 Property Types by Listing Count", fontweight="bold")
    ax.set_xticklabels(df["property_type"], rotation=30, ha="right")
    ax.set_ylabel("Number of Listings")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "02b_property_type_top10.png")


# ── Q3 : Room type composition per borough ────────────────────────────────────
def plot_room_type_by_borough():
    df = query("""
        SELECT
            neighbourhood,
            room_type,
            COUNT(*)                                    AS listings
        FROM listings
        GROUP BY neighbourhood, room_type
        ORDER BY neighbourhood, listings DESC
    """)

    pivot = df.pivot(index="neighbourhood", columns="room_type", values="listings").fillna(0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Room Type by Borough", fontweight="bold", fontsize=13)

    # Absolute counts stacked bar
    pivot.plot(kind="bar", stacked=True, ax=axes[0],
               color=sns.color_palette("Set2", pivot.shape[1]))
    axes[0].set_title("Absolute Listing Count")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Listings")
    axes[0].tick_params(axis="x", rotation=30)
    axes[0].legend(title="Room Type", bbox_to_anchor=(1.01, 1), loc="upper left")
    axes[0].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    # Percentage stacked bar
    pivot_pct.plot(kind="bar", stacked=True, ax=axes[1],
                   color=sns.color_palette("Set2", pivot_pct.shape[1]))
    axes[1].set_title("Percentage Composition")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Percentage (%)")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].legend(title="Room Type", bbox_to_anchor=(1.01, 1), loc="upper left")

    plt.tight_layout()
    save(fig, "02c_room_type_by_borough.png")


# ── Q4 : Average beds by room type ────────────────────────────────────────────
def plot_avg_beds_by_room_type():
    df = query("""
        SELECT
            room_type,
            ROUND(AVG(beds), 2)  AS avg_beds,
            COUNT(*)             AS listings
        FROM listings
        GROUP BY room_type
        ORDER BY avg_beds DESC
    """)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(df["room_type"], df["avg_beds"],
                  color=sns.color_palette("muted", len(df)))
    for bar, val in zip(bars, df["avg_beds"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=11)
    ax.set_title("Average Number of Beds by Room Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Average Beds")
    save(fig, "02d_avg_beds_by_room_type.png")


# ── Q5 : Property type × room type heatmap ────────────────────────────────────
def plot_property_room_heatmap():
    df = query("""
        SELECT
            property_type,
            room_type,
            COUNT(*) AS listings
        FROM listings
        WHERE property_type IN (
            SELECT property_type FROM listings
            GROUP BY property_type ORDER BY COUNT(*) DESC LIMIT 8
        )
        GROUP BY property_type, room_type
    """)

    pivot = df.pivot(index="property_type", columns="room_type", values="listings").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, ax=ax,
                cbar_kws={"label": "Number of Listings"})
    ax.set_title("Listing Count: Property Type × Room Type\n(Top 8 Property Types)",
                 fontweight="bold")
    ax.set_xlabel("Room Type")
    ax.set_ylabel("Property Type")
    plt.xticks(rotation=20)
    save(fig, "02e_property_room_heatmap.png")


# ── Q6 : Review score by room type ────────────────────────────────────────────
def plot_review_score_by_room_type():
    df = query("""
        SELECT
            room_type,
            ROUND(AVG(review_score_rating), 2)  AS avg_review_score,
            ROUND(AVG(number_of_reviews), 1)    AS avg_num_reviews
        FROM listings
        WHERE review_score_rating IS NOT NULL
        GROUP BY room_type
        ORDER BY avg_review_score DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Reviews by Room Type", fontweight="bold", fontsize=13)

    palette = sns.color_palette("Set2", len(df))

    bars = axes[0].bar(df["room_type"], df["avg_review_score"], color=palette)
    for bar, val in zip(bars, df["avg_review_score"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     f"{val:.1f}", ha="center", va="bottom", fontsize=11)
    axes[0].set_title("Avg Review Score (out of 100)")
    axes[0].set_ylabel("Avg Review Score")
    axes[0].set_ylim(0, 105)

    bars2 = axes[1].bar(df["room_type"], df["avg_num_reviews"], color=palette)
    for bar, val in zip(bars2, df["avg_num_reviews"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     f"{val:.1f}", ha="center", va="bottom", fontsize=11)
    axes[1].set_title("Avg Number of Reviews per Listing")
    axes[1].set_ylabel("Avg Number of Reviews")

    plt.tight_layout()
    save(fig, "02f_review_score_by_room_type.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  AirBNB NYC — Room & Property Type Analysis")
    print("=" * 60)
    plot_room_type_distribution()
    plot_property_type_top10()
    plot_room_type_by_borough()
    plot_avg_beds_by_room_type()
    plot_property_room_heatmap()
    plot_review_score_by_room_type()
    print("\nRoom & Property Type analysis complete.")
