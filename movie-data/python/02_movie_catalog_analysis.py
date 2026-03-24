"""
=============================================================================
PROJECT  : Movie Data Analysis
FILE     : python/02_movie_catalog_analysis.py
PURPOSE  : Analyse the movie catalogue — language mix, age certificates,
           movie lengths, and release decade trends
           Mirrors: sql/02_movie_catalog_analysis.sql
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


# ── Q1 : Language distribution (bar + pie) ───────────────────────────────────
def plot_language_distribution():
    df = query("""
        SELECT movie_lang, COUNT(*) AS movie_count
        FROM movies
        GROUP BY movie_lang
        ORDER BY movie_count DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Movie Language Distribution", fontweight="bold", fontsize=13)

    # Bar chart
    sns.barplot(data=df, x="movie_lang", y="movie_count",
                palette="tab10", ax=axes[0])
    axes[0].set_title("Movie Count by Language")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Number of Movies")
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.3,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=10)

    # Pie chart
    colors = sns.color_palette("tab10", len(df))
    axes[1].pie(df["movie_count"], labels=df["movie_lang"], colors=colors,
                autopct="%1.1f%%", startangle=140,
                textprops={"fontsize": 9})
    axes[1].set_title("Language Share")

    plt.tight_layout()
    save(fig, "02a_language_distribution.png")


# ── Q2 : Age certificate breakdown ──────────────────────────────────────────
def plot_age_certificate():
    df = query("""
        SELECT
            m.age_certificate,
            COUNT(DISTINCT m.movie_id)  AS movie_count,
            ROUND(AVG(m.movie_length), 1) AS avg_length_mins
        FROM movies m
        GROUP BY m.age_certificate
        ORDER BY movie_count DESC
    """)

    cert_order = ["U", "PG", "12", "15", "18"]
    df["age_certificate"] = pd.Categorical(df["age_certificate"], categories=cert_order, ordered=True)
    df = df.sort_values("age_certificate")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Age Certificate Analysis", fontweight="bold", fontsize=13)

    palette = {"U": "#2ecc71", "PG": "#3498db", "12": "#f1c40f", "15": "#e67e22", "18": "#e74c3c"}
    colors  = [palette.get(c, "#95a5a6") for c in df["age_certificate"]]

    # Count
    bars = axes[0].bar(df["age_certificate"].astype(str), df["movie_count"], color=colors)
    axes[0].set_title("Movie Count by Age Certificate")
    axes[0].set_xlabel("Certificate")
    axes[0].set_ylabel("Number of Movies")
    for bar in bars:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.2,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=10)

    # Avg length
    bars2 = axes[1].bar(df["age_certificate"].astype(str), df["avg_length_mins"], color=colors)
    axes[1].set_title("Avg Movie Length by Certificate (mins)")
    axes[1].set_xlabel("Certificate")
    axes[1].set_ylabel("Average Length (minutes)")
    for bar, val in zip(bars2, df["avg_length_mins"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.5,
                     f"{val:.0f} min",
                     ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    save(fig, "02b_age_certificate.png")


# ── Q3 : Movie length box plot by language ───────────────────────────────────
def plot_length_by_language():
    df = query("""
        SELECT movie_lang, movie_length
        FROM movies
        WHERE movie_length IS NOT NULL
    """)

    order = df.groupby("movie_lang")["movie_length"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=df, x="movie_lang", y="movie_length", order=order,
                palette="Set2", ax=ax,
                flierprops=dict(marker="o", markersize=4, alpha=0.5))
    ax.set_title("Movie Length Distribution by Language", fontweight="bold")
    ax.set_xlabel("Language")
    ax.set_ylabel("Movie Length (minutes)")
    ax.axhline(df["movie_length"].median(), color="red", linestyle="--",
               linewidth=1, label=f"Overall median: {df['movie_length'].median():.0f} min")
    ax.legend()
    plt.tight_layout()
    save(fig, "02c_length_by_language.png")


# ── Q4 : Movies released by decade ──────────────────────────────────────────
def plot_movies_by_decade():
    df = query("""
        SELECT
            (EXTRACT(YEAR FROM release_date) / 10 * 10)::INTEGER AS decade,
            COUNT(*) AS movie_count
        FROM movies
        WHERE release_date IS NOT NULL
        GROUP BY decade
        ORDER BY decade
    """)

    df["decade_label"] = df["decade"].astype(str) + "s"

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = sns.color_palette("crest", len(df))
    bars   = ax.bar(df["decade_label"], df["movie_count"], color=colors)
    ax.set_title("Movies Released by Decade", fontweight="bold")
    ax.set_xlabel("Decade")
    ax.set_ylabel("Number of Movies")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.2,
                str(int(bar.get_height())),
                ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    save(fig, "02d_movies_by_decade.png")


# ── Q5 : Heatmap — language × age certificate ───────────────────────────────
def plot_lang_cert_heatmap():
    df = query("""
        SELECT
            movie_lang,
            age_certificate,
            COUNT(*) AS movies
        FROM movies
        GROUP BY movie_lang, age_certificate
    """)

    pivot = df.pivot(index="movie_lang", columns="age_certificate", values="movies").fillna(0)
    cert_order = [c for c in ["U", "PG", "12", "15", "18"] if c in pivot.columns]
    pivot = pivot[cert_order]

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax,
                cbar_kws={"label": "Number of Movies"})
    ax.set_title("Movie Count: Language × Age Certificate", fontweight="bold")
    ax.set_xlabel("Age Certificate")
    ax.set_ylabel("Language")
    plt.xticks(rotation=0)
    plt.tight_layout()
    save(fig, "02e_language_cert_heatmap.png")


# ── Q6 : Movies per year by language (stacked bar) ───────────────────────────
def plot_release_trend_by_language():
    df = query("""
        SELECT
            EXTRACT(YEAR FROM release_date)::INTEGER AS release_year,
            movie_lang,
            COUNT(*) AS movie_count
        FROM movies
        WHERE release_date IS NOT NULL
        GROUP BY release_year, movie_lang
        ORDER BY release_year
    """)

    pivot = df.pivot_table(index="release_year", columns="movie_lang",
                           values="movie_count", fill_value=0)

    fig, ax = plt.subplots(figsize=(13, 5))
    pivot.plot(kind="bar", ax=ax, stacked=True, colormap="tab10",
               edgecolor="white", linewidth=0.4)
    ax.set_title("Movies Released Per Year by Language", fontweight="bold")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Movies")
    ax.legend(title="Language", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    save(fig, "02f_release_trend_by_language.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Data — Catalog Analysis")
    print("=" * 60)
    plot_language_distribution()
    plot_age_certificate()
    plot_length_by_language()
    plot_movies_by_decade()
    plot_lang_cert_heatmap()
    plot_release_trend_by_language()
    print("\nCatalog analysis complete.")
