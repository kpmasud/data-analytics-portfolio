"""
=============================================================================
PROJECT  : Movie Data Analysis
FILE     : python/03_director_analysis.py
PURPOSE  : Analyse directors — nationality spread, most prolific directors,
           revenue performance, and age demographics
           Mirrors: sql/03_director_analysis.sql
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


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Director nationality distribution ───────────────────────────────────
def plot_director_nationality():
    df = query("""
        SELECT nationality, COUNT(*) AS director_count
        FROM directors
        WHERE nationality IS NOT NULL
        GROUP BY nationality
        ORDER BY director_count DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Director Nationality Distribution", fontweight="bold", fontsize=13)

    sns.barplot(data=df, x="nationality", y="director_count",
                palette="Blues_d", ax=axes[0])
    axes[0].set_title("Directors by Nationality")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Number of Directors")
    axes[0].tick_params(axis="x", rotation=35)
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=9)

    colors = sns.color_palette("tab10", len(df))
    axes[1].pie(df["director_count"], labels=df["nationality"],
                colors=colors, autopct="%1.1f%%", startangle=140,
                textprops={"fontsize": 8})
    axes[1].set_title("Nationality Share")

    plt.tight_layout()
    save(fig, "03a_director_nationality.png")


# ── Q2 : Most prolific directors ─────────────────────────────────────────────
def plot_prolific_directors():
    df = query("""
        SELECT
            d.first_name || ' ' || d.last_name AS director,
            d.nationality,
            COUNT(m.movie_id)                  AS movies_directed
        FROM directors d
        JOIN movies m ON d.director_id = m.director_id
        GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
        HAVING COUNT(m.movie_id) > 1
        ORDER BY movies_directed DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = sns.color_palette("viridis", len(df))
    bars   = ax.barh(df["director"], df["movies_directed"], color=colors)
    ax.invert_yaxis()
    ax.set_title("Directors with Multiple Films in Dataset", fontweight="bold")
    ax.set_xlabel("Number of Movies Directed")
    for bar in bars:
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(int(bar.get_width())),
                va="center", fontsize=10)
    plt.tight_layout()
    save(fig, "03b_prolific_directors.png")


# ── Q3 : Director revenue performance ────────────────────────────────────────
def plot_director_revenue():
    df = query("""
        SELECT
            d.first_name || ' ' || d.last_name AS director,
            d.nationality,
            ROUND(SUM(
                COALESCE(mr.domestic_takings, 0)
                + COALESCE(mr.international_takings, 0)
            ), 2) AS total_revenue_m
        FROM directors d
        JOIN movies m          ON d.director_id = m.director_id
        JOIN movie_revenues mr ON m.movie_id    = mr.movie_id
        GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
        ORDER BY total_revenue_m DESC
        LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(11, 6))
    palette = sns.color_palette("mako", len(df))
    bars    = ax.barh(df["director"], df["total_revenue_m"], color=palette)
    ax.invert_yaxis()
    ax.set_title("Top Directors by Total Box-Office Revenue", fontweight="bold")
    ax.set_xlabel("Total Revenue (USD millions)")
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    for bar, nat in zip(bars, df["nationality"]):
        ax.text(bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f"${bar.get_width():.1f}M  [{nat}]",
                va="center", fontsize=9)
    plt.tight_layout()
    save(fig, "03c_director_revenue.png")


# ── Q4 : Director age histogram ──────────────────────────────────────────────
def plot_director_ages():
    df = query("""
        SELECT
            DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))::INTEGER AS age
        FROM directors
        WHERE date_of_birth IS NOT NULL
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["age"], bins=12, color="#4C72B0", edgecolor="white", linewidth=0.7)
    ax.axvline(df["age"].mean(), color="red", linestyle="--", linewidth=1.5,
               label=f"Mean age: {df['age'].mean():.1f} yrs")
    ax.axvline(df["age"].median(), color="orange", linestyle="--", linewidth=1.5,
               label=f"Median age: {df['age'].median():.1f} yrs")
    ax.set_title("Director Age Distribution", fontweight="bold")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Number of Directors")
    ax.legend()
    plt.tight_layout()
    save(fig, "03d_director_age_distribution.png")


# ── Q5 : English vs non-English — movie count & avg revenue ─────────────────
def plot_english_vs_nonenglish():
    df = query("""
        SELECT
            CASE WHEN m.movie_lang = 'English' THEN 'English' ELSE 'Non-English' END AS lang_group,
            COUNT(DISTINCT m.movie_id)   AS movies,
            ROUND(AVG(
                COALESCE(mr.domestic_takings, 0)
                + COALESCE(mr.international_takings, 0)
            ), 2)                        AS avg_total_revenue_m
        FROM movies m
        LEFT JOIN movie_revenues mr ON m.movie_id = mr.movie_id
        GROUP BY lang_group
    """)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle("English vs Non-English Films", fontweight="bold", fontsize=13)

    colors = ["#4C72B0", "#DD8452"]
    axes[0].bar(df["lang_group"], df["movies"], color=colors)
    axes[0].set_title("Movie Count")
    axes[0].set_ylabel("Number of Movies")
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.3,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=11, fontweight="bold")

    axes[1].bar(df["lang_group"], df["avg_total_revenue_m"], color=colors)
    axes[1].set_title("Avg Total Revenue")
    axes[1].set_ylabel("Avg Revenue (USD millions)")
    axes[1].yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}M"))
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.3,
                     f"${bar.get_height():.1f}M",
                     ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    save(fig, "03e_english_vs_nonenglish.png")


# ── Q6 : Director career span ────────────────────────────────────────────────
def plot_director_career_span():
    df = query("""
        SELECT
            d.first_name || ' ' || d.last_name         AS director,
            d.nationality,
            MIN(EXTRACT(YEAR FROM m.release_date))::INTEGER AS first_year,
            MAX(EXTRACT(YEAR FROM m.release_date))::INTEGER AS last_year,
            (MAX(EXTRACT(YEAR FROM m.release_date))
             - MIN(EXTRACT(YEAR FROM m.release_date)))::INTEGER AS span_years,
            COUNT(m.movie_id) AS films
        FROM directors d
        JOIN movies m ON d.director_id = m.director_id
        WHERE m.release_date IS NOT NULL
        GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
        HAVING COUNT(m.movie_id) > 1
        ORDER BY span_years DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    for _, row in df.iterrows():
        ax.plot([row["first_year"], row["last_year"]],
                [row["director"], row["director"]],
                "o-", linewidth=2, markersize=6)
    ax.set_title("Director Career Span (First to Last Film in Dataset)", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    save(fig, "03f_director_career_span.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Data — Director Analysis")
    print("=" * 60)
    plot_director_nationality()
    plot_prolific_directors()
    plot_director_revenue()
    plot_director_ages()
    plot_english_vs_nonenglish()
    plot_director_career_span()
    print("\nDirector analysis complete.")
