"""
=============================================================================
PROJECT  : Movie Data Analysis
FILE     : python/01_revenue_analysis.py
PURPOSE  : Box-office revenue analysis — top earners, domestic vs
           international split, revenue by language and nationality
           Mirrors: sql/01_revenue_analysis.sql
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

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PG = dict(
    host     = os.getenv("PG_HOST", "localhost"),
    port     = int(os.getenv("PG_PORT", 5432)),
    user     = os.getenv("PG_USER", "postgres"),
    password = os.getenv("PG_PASSWORD", ""),
    dbname   = os.getenv("PG_DATABASE", "movie_data"),
)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)


# ── Helpers ──────────────────────────────────────────────────────────────────
def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Top 10 movies by total revenue ─────────────────────────────────────
def plot_top_10_revenue():
    df = query("""
        SELECT
            m.movie_name,
            COALESCE(mr.domestic_takings, 0)            AS domestic_m,
            COALESCE(mr.international_takings, 0)       AS international_m,
            COALESCE(mr.domestic_takings, 0)
                + COALESCE(mr.international_takings, 0) AS total_revenue_m
        FROM movies m
        JOIN movie_revenues mr ON m.movie_id = mr.movie_id
        WHERE mr.domestic_takings IS NOT NULL
           OR mr.international_takings IS NOT NULL
        ORDER BY total_revenue_m DESC
        LIMIT 10
    """)

    fig, ax = plt.subplots(figsize=(11, 6))
    y = range(len(df))
    bar_width = 0.4

    bars_dom  = ax.barh([i + bar_width/2 for i in y], df["domestic_m"],
                        height=bar_width, label="Domestic",     color="#4C72B0")
    bars_intl = ax.barh([i - bar_width/2 for i in y], df["international_m"],
                        height=bar_width, label="International", color="#DD8452")

    ax.set_yticks(list(y))
    ax.set_yticklabels(df["movie_name"])
    ax.invert_yaxis()
    ax.set_xlabel("Revenue (USD millions)")
    ax.set_title("Top 10 Movies by Total Box-Office Revenue", fontweight="bold")
    ax.legend()
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))

    # annotate total on the right
    for i, row in df.iterrows():
        ax.text(row["total_revenue_m"] + 1, i,
                f"${row['total_revenue_m']:.1f}M",
                va="center", fontsize=9)

    plt.tight_layout()
    save(fig, "01a_top10_revenue.png")


# ── Q2 : Domestic vs international scatter ───────────────────────────────────
def plot_dom_vs_intl():
    df = query("""
        SELECT
            m.movie_name,
            mr.domestic_takings,
            mr.international_takings
        FROM movies m
        JOIN movie_revenues mr ON m.movie_id = mr.movie_id
        WHERE mr.domestic_takings IS NOT NULL
          AND mr.international_takings IS NOT NULL
    """)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(df["domestic_takings"], df["international_takings"],
               s=80, alpha=0.75, color="#4C72B0", edgecolors="white", linewidths=0.5)

    # 1:1 reference line
    lim = max(df["domestic_takings"].max(), df["international_takings"].max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="grey", linewidth=1, label="Dom = Intl")

    # label notable points
    for _, row in df.nlargest(5, "international_takings").iterrows():
        ax.annotate(row["movie_name"],
                    (row["domestic_takings"], row["international_takings"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

    ax.set_xlabel("Domestic Takings (USD millions)")
    ax.set_ylabel("International Takings (USD millions)")
    ax.set_title("Domestic vs International Box-Office Revenue", fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    ax.legend()
    plt.tight_layout()
    save(fig, "01b_domestic_vs_international.png")


# ── Q3 : Revenue data coverage (pie) ────────────────────────────────────────
def plot_revenue_coverage():
    df = query("""
        SELECT
            COUNT(mr.revenue_id)                AS movies_with_revenue,
            COUNT(*) - COUNT(mr.revenue_id)     AS movies_missing_revenue
        FROM movies m
        LEFT JOIN movie_revenues mr ON m.movie_id = mr.movie_id
    """)

    sizes  = [df["movies_with_revenue"].iloc[0], df["movies_missing_revenue"].iloc[0]]
    labels = [f"Has Revenue Data\n({sizes[0]})", f"No Revenue Data\n({sizes[1]})"]
    colors = ["#55A868", "#C44E52"]

    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=90, textprops={"fontsize": 11}
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Revenue Data Coverage Across All Movies", fontweight="bold")
    plt.tight_layout()
    save(fig, "01c_revenue_coverage.png")


# ── Q4 : Average total revenue by language ───────────────────────────────────
def plot_revenue_by_language():
    df = query("""
        SELECT
            m.movie_lang,
            COUNT(m.movie_id)   AS movie_count,
            ROUND(AVG(
                COALESCE(mr.domestic_takings, 0)
                + COALESCE(mr.international_takings, 0)
            ), 2)               AS avg_total_revenue_m
        FROM movies m
        JOIN movie_revenues mr ON m.movie_id = mr.movie_id
        GROUP BY m.movie_lang
        ORDER BY avg_total_revenue_m DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = sns.barplot(data=df, x="movie_lang", y="avg_total_revenue_m",
                       palette="Blues_d", ax=ax)
    ax.set_title("Average Total Box-Office Revenue by Language", fontweight="bold")
    ax.set_xlabel("Language")
    ax.set_ylabel("Avg Total Revenue (USD millions)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    for bar, cnt in zip(ax.patches, df["movie_count"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"${bar.get_height():.1f}M\n({cnt} films)",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "01d_revenue_by_language.png")


# ── Q5 : Total revenue by director nationality ───────────────────────────────
def plot_revenue_by_nationality():
    df = query("""
        SELECT
            d.nationality,
            ROUND(SUM(
                COALESCE(mr.domestic_takings, 0)
                + COALESCE(mr.international_takings, 0)
            ), 2) AS total_revenue_m
        FROM movies m
        JOIN directors d       ON m.director_id = d.director_id
        JOIN movie_revenues mr ON m.movie_id    = mr.movie_id
        GROUP BY d.nationality
        ORDER BY total_revenue_m DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x="nationality", y="total_revenue_m",
                palette="viridis", ax=ax)
    ax.set_title("Total Box-Office Revenue by Director Nationality", fontweight="bold")
    ax.set_xlabel("Director Nationality")
    ax.set_ylabel("Total Revenue (USD millions)")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    plt.xticks(rotation=30, ha="right")
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"${bar.get_height():.0f}M",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "01e_revenue_by_director_nationality.png")


# ── Q6 : International dominance (surplus chart) ─────────────────────────────
def plot_international_dominance():
    df = query("""
        SELECT
            m.movie_name,
            mr.domestic_takings,
            mr.international_takings,
            ROUND(mr.international_takings - mr.domestic_takings, 2) AS intl_surplus_m
        FROM movies m
        JOIN movie_revenues mr ON m.movie_id = mr.movie_id
        WHERE mr.domestic_takings IS NOT NULL
          AND mr.international_takings IS NOT NULL
        ORDER BY intl_surplus_m DESC
    """)

    colors = ["#55A868" if v >= 0 else "#C44E52" for v in df["intl_surplus_m"]]

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(df["movie_name"], df["intl_surplus_m"], color=colors)
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("International vs Domestic Surplus (positive = intl dominated)", fontweight="bold")
    ax.set_xlabel("Surplus (USD millions)")
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    for bar in bars:
        val = bar.get_width()
        ax.text(val + (0.5 if val >= 0 else -0.5),
                bar.get_y() + bar.get_height() / 2,
                f"${val:+.1f}M",
                va="center", ha="left" if val >= 0 else "right", fontsize=8)
    plt.tight_layout()
    save(fig, "01f_international_dominance.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Data — Revenue Analysis")
    print("=" * 60)
    plot_top_10_revenue()
    plot_dom_vs_intl()
    plot_revenue_coverage()
    plot_revenue_by_language()
    plot_revenue_by_nationality()
    plot_international_dominance()
    print("\nRevenue analysis complete.")
