"""
=============================================================================
PROJECT  : UK Used Car Market Analysis
FILE     : python/03_fuel_transmission_analysis.py
PURPOSE  : Run fuel type and transmission analysis and produce charts
           Mirrors: sql/03_fuel_transmission_analysis.sql
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


# ── Q1 : Fuel type distribution ───────────────────────────────────────────────
def plot_fuel_distribution():
    df = query("""
        SELECT fuel_type, COUNT(*) AS listings,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
        FROM cars GROUP BY fuel_type ORDER BY listings DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Fuel Type Distribution", fontweight="bold", fontsize=13)

    axes[0].pie(df["listings"], labels=df["fuel_type"], autopct="%1.1f%%",
                startangle=140, colors=sns.color_palette("Set2", len(df)))
    axes[0].set_title("Market Share by Fuel Type")

    sns.barplot(data=df, x="fuel_type", y="listings", palette="Set2", ax=axes[1])
    axes[1].set_title("Listing Count by Fuel Type")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Listings")
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200,
                     f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    save(fig, "03a_fuel_type_distribution.png")


# ── Q2 : Transmission breakdown ───────────────────────────────────────────────
def plot_transmission_breakdown():
    df = query("""
        SELECT transmission, COUNT(*) AS listings,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct,
               ROUND(AVG(price)::NUMERIC, 0) AS avg_price
        FROM cars GROUP BY transmission ORDER BY listings DESC
    """)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(df["transmission"], df["listings"],
                  color=sns.color_palette("pastel", len(df)))
    for bar, pct in zip(bars, df["pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 300,
                f"{pct}%", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_title("Transmission Type Breakdown", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Number of Listings")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    save(fig, "03b_transmission_breakdown.png")


# ── Q3 : Average MPG by fuel type ─────────────────────────────────────────────
def plot_mpg_by_fuel():
    df = query("""
        SELECT fuel_type,
               ROUND(AVG(mpg)::NUMERIC, 2) AS avg_mpg,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mpg) AS median_mpg,
               COUNT(*) AS listings
        FROM cars WHERE mpg IS NOT NULL AND mpg > 0
        GROUP BY fuel_type ORDER BY avg_mpg DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(df))
    ax.bar(x, df["avg_mpg"], color=sns.color_palette("crest", len(df)), label="Avg MPG")
    ax.plot(x, df["median_mpg"], "o--", color="tomato", linewidth=2,
            markersize=9, label="Median MPG")
    ax.set_xticks(x)
    ax.set_xticklabels(df["fuel_type"], rotation=15)
    ax.set_title("Average & Median MPG by Fuel Type", fontweight="bold")
    ax.set_ylabel("Miles Per Gallon")
    ax.legend()
    for i, (avg, cnt) in enumerate(zip(df["avg_mpg"], df["listings"])):
        ax.text(i, avg + 0.5, f"{avg:.1f}", ha="center", va="bottom", fontsize=9)
    save(fig, "03c_mpg_by_fuel_type.png")


# ── Q4 : Annual tax by fuel type ──────────────────────────────────────────────
def plot_tax_by_fuel():
    df = query("""
        SELECT fuel_type,
               ROUND(AVG(tax)::NUMERIC, 2) AS avg_tax,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tax) AS median_tax,
               COUNT(*) AS listings
        FROM cars WHERE tax IS NOT NULL
        GROUP BY fuel_type ORDER BY avg_tax DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=df, x="fuel_type", y="avg_tax", palette="flare", ax=ax)
    ax.set_title("Average Annual Road Tax by Fuel Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Avg Road Tax (£)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"£{bar.get_height():.0f}", ha="center", va="bottom", fontsize=10)
    save(fig, "03d_tax_by_fuel_type.png")


# ── Q5 : Fuel type trend by year ──────────────────────────────────────────────
def plot_fuel_trend_by_year():
    df = query("""
        SELECT year, fuel_type, COUNT(*) AS listings
        FROM cars WHERE year >= 2010
        GROUP BY year, fuel_type ORDER BY year, listings DESC
    """)
    pivot = df.pivot(index="year", columns="fuel_type", values="listings").fillna(0)

    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax,
               colormap="tab10", width=0.8)
    ax.set_title("Fuel Type Mix by Year (2010–2020)", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Listings")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend(title="Fuel Type", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.tick_params(axis="x", rotation=0)
    plt.tight_layout()
    save(fig, "03e_fuel_trend_by_year.png")


# ── Q6 : Engine size by fuel type ─────────────────────────────────────────────
def plot_engine_size_by_fuel():
    df = query("SELECT fuel_type, engine_size FROM cars")
    order = df.groupby("fuel_type")["engine_size"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="fuel_type", y="engine_size", order=order,
                palette="pastel", ax=ax,
                flierprops=dict(marker="o", markersize=2, alpha=0.3))
    ax.set_title("Engine Size Distribution by Fuel Type", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Engine Size (litres)")
    save(fig, "03f_engine_size_by_fuel.png")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  UK Used Cars — Fuel & Transmission Analysis")
    print("=" * 60)
    plot_fuel_distribution()
    plot_transmission_breakdown()
    plot_mpg_by_fuel()
    plot_tax_by_fuel()
    plot_fuel_trend_by_year()
    plot_engine_size_by_fuel()
    print("\nFuel & transmission analysis complete.")
