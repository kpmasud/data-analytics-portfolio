"""
=============================================================================
PROJECT  : Movie Data Analysis
FILE     : python/04_actor_analysis.py
PURPOSE  : Analyse actors — gender split, prolific performers, age
           demographics, and cast size patterns per movie
           Mirrors: sql/04_actor_analysis.sql
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


# ── Q1 : Gender distribution ─────────────────────────────────────────────────
def plot_gender_split():
    df = query("""
        SELECT
            CASE gender WHEN 'M' THEN 'Male' WHEN 'F' THEN 'Female' ELSE 'Unknown' END AS gender,
            COUNT(*) AS actor_count
        FROM actors
        GROUP BY gender
    """)

    fig, ax = plt.subplots(figsize=(6, 6))
    colors = {"Male": "#4C72B0", "Female": "#DD8452", "Unknown": "#8c8c8c"}
    color_list = [colors.get(g, "#95a5a6") for g in df["gender"]]
    wedges, texts, autotexts = ax.pie(
        df["actor_count"], labels=df["gender"], colors=color_list,
        autopct="%1.1f%%", startangle=90, textprops={"fontsize": 12}
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Actor Gender Distribution", fontweight="bold", fontsize=13)
    plt.tight_layout()
    save(fig, "04a_actor_gender.png")


# ── Q2 : Most prolific actors ────────────────────────────────────────────────
def plot_prolific_actors():
    df = query("""
        SELECT
            a.first_name || ' ' || a.last_name         AS actor,
            CASE a.gender WHEN 'M' THEN 'Male' ELSE 'Female' END AS gender,
            COUNT(ma.movie_id)                          AS movies_appeared_in
        FROM actors a
        JOIN movies_actors ma ON a.actor_id = ma.actor_id
        GROUP BY a.actor_id, a.first_name, a.last_name, a.gender
        ORDER BY movies_appeared_in DESC
        LIMIT 15
    """)

    color_map = {"Male": "#4C72B0", "Female": "#DD8452"}
    colors    = [color_map.get(g, "#8c8c8c") for g in df["gender"]]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(df["actor"], df["movies_appeared_in"], color=colors)
    ax.invert_yaxis()
    ax.set_title("Top 15 Most Prolific Actors (by Film Count)", fontweight="bold")
    ax.set_xlabel("Number of Movies")
    for bar in bars:
        ax.text(bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                str(int(bar.get_width())),
                va="center", fontsize=10)

    # legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#4C72B0", label="Male"),
                       Patch(facecolor="#DD8452", label="Female")]
    ax.legend(handles=legend_elements, loc="lower right")
    plt.tight_layout()
    save(fig, "04b_prolific_actors.png")


# ── Q3 : Actor age histogram ─────────────────────────────────────────────────
def plot_actor_ages():
    df = query("""
        SELECT
            DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))::INTEGER AS age
        FROM actors
        WHERE date_of_birth IS NOT NULL
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["age"], bins=15, color="#55A868", edgecolor="white", linewidth=0.7)
    ax.axvline(df["age"].mean(), color="red", linestyle="--", linewidth=1.5,
               label=f"Mean: {df['age'].mean():.1f} yrs")
    ax.axvline(df["age"].median(), color="orange", linestyle="--", linewidth=1.5,
               label=f"Median: {df['age'].median():.1f} yrs")
    ax.set_title("Actor Age Distribution", fontweight="bold")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Number of Actors")
    ax.legend()
    plt.tight_layout()
    save(fig, "04c_actor_age_distribution.png")


# ── Q4 : Cast size per movie ─────────────────────────────────────────────────
def plot_cast_sizes():
    df = query("""
        SELECT
            m.movie_name,
            m.movie_lang,
            COUNT(ma.actor_id) AS cast_size
        FROM movies m
        JOIN movies_actors ma ON m.movie_id = ma.movie_id
        GROUP BY m.movie_id, m.movie_name, m.movie_lang
        ORDER BY cast_size DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Cast Size Analysis", fontweight="bold", fontsize=13)

    # Histogram
    axes[0].hist(df["cast_size"], bins=range(1, df["cast_size"].max() + 2),
                 color="#4C72B0", edgecolor="white", linewidth=0.7, align="left")
    axes[0].axvline(df["cast_size"].mean(), color="red", linestyle="--",
                    label=f"Mean: {df['cast_size'].mean():.1f}")
    axes[0].set_title("Distribution of Cast Sizes")
    axes[0].set_xlabel("Cast Size (actors per movie)")
    axes[0].set_ylabel("Number of Movies")
    axes[0].legend()

    # Top 10 largest casts
    top = df.head(10)
    axes[1].barh(top["movie_name"], top["cast_size"],
                 color=sns.color_palette("Blues_d", len(top)))
    axes[1].invert_yaxis()
    axes[1].set_title("Top 10 Movies by Cast Size")
    axes[1].set_xlabel("Number of Actors")
    for i, val in enumerate(top["cast_size"]):
        axes[1].text(val + 0.1, i, str(val), va="center", fontsize=10)

    plt.tight_layout()
    save(fig, "04d_cast_size.png")


# ── Q5 : Average cast size by language ──────────────────────────────────────
def plot_cast_by_language():
    df = query("""
        SELECT
            m.movie_lang,
            ROUND(AVG(cast_counts.cast_size), 1) AS avg_cast_size,
            COUNT(DISTINCT m.movie_id)            AS movies
        FROM movies m
        JOIN (
            SELECT movie_id, COUNT(actor_id) AS cast_size
            FROM movies_actors
            GROUP BY movie_id
        ) cast_counts ON m.movie_id = cast_counts.movie_id
        GROUP BY m.movie_lang
        ORDER BY avg_cast_size DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x="movie_lang", y="avg_cast_size",
                palette="crest", ax=ax)
    ax.set_title("Average Cast Size by Language", fontweight="bold")
    ax.set_xlabel("Language")
    ax.set_ylabel("Average Cast Size")
    for bar, cnt in zip(ax.patches, df["movies"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f"{bar.get_height():.1f}\n({cnt} films)",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "04e_cast_size_by_language.png")


# ── Q6 : Gender representation by language (grouped bar) ─────────────────────
def plot_gender_by_language():
    df = query("""
        SELECT
            m.movie_lang,
            SUM(CASE WHEN a.gender = 'M' THEN 1 ELSE 0 END) AS male_actors,
            SUM(CASE WHEN a.gender = 'F' THEN 1 ELSE 0 END) AS female_actors
        FROM movies m
        JOIN movies_actors ma ON m.movie_id = ma.movie_id
        JOIN actors a         ON ma.actor_id = a.actor_id
        WHERE a.gender IS NOT NULL
        GROUP BY m.movie_lang
        ORDER BY SUM(CASE WHEN a.gender = 'F' THEN 1.0 ELSE 0 END)
                 / NULLIF(COUNT(*), 0) DESC
    """)

    x      = range(len(df))
    width  = 0.35
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar([i - width/2 for i in x], df["male_actors"],   width, label="Male",   color="#4C72B0")
    ax.bar([i + width/2 for i in x], df["female_actors"], width, label="Female", color="#DD8452")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["movie_lang"])
    ax.set_title("Actor Gender Representation by Movie Language", fontweight="bold")
    ax.set_xlabel("Language")
    ax.set_ylabel("Actor Appearances")
    ax.legend()
    plt.tight_layout()
    save(fig, "04f_gender_by_language.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Data — Actor Analysis")
    print("=" * 60)
    plot_gender_split()
    plot_prolific_actors()
    plot_actor_ages()
    plot_cast_sizes()
    plot_cast_by_language()
    plot_gender_by_language()
    print("\nActor analysis complete.")
