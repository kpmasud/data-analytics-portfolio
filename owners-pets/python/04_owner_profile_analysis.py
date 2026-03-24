"""
=============================================================================
PROJECT  : Owners & Pets Analysis
FILE     : python/04_owner_profile_analysis.py
PURPOSE  : Analyse owner profiles — email preferences, pet name popularity,
           age-gap households, and full owner summary
           Mirrors: sql/04_owner_profile_analysis.sql
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
    dbname   = os.getenv("PG_DATABASE", "owners_pets"),
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


# ── Q1 : Email domain distribution (pie) ─────────────────────────────────────
def plot_email_domains():
    df = query("""
        SELECT
            SUBSTRING(email FROM POSITION('@' IN email) + 1) AS email_domain,
            COUNT(*) AS owner_count
        FROM owners_pets
        WHERE email IS NOT NULL
        GROUP BY email_domain
        ORDER BY owner_count DESC
    """)

    colors = sns.color_palette("tab10", len(df))
    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, texts, autotexts = ax.pie(
        df["owner_count"], labels=df["email_domain"], colors=colors,
        autopct="%1.1f%%", startangle=140, textprops={"fontsize": 11}
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Email Provider Distribution Among Owners", fontweight="bold")
    plt.tight_layout()
    save(fig, "04a_email_domains.png")


# ── Q2 : Email domain vs avg pets owned ──────────────────────────────────────
def plot_email_vs_pets():
    df = query("""
        SELECT
            SUBSTRING(o.email FROM POSITION('@' IN o.email) + 1) AS email_domain,
            COUNT(DISTINCT o.id)                                  AS owners,
            ROUND(COUNT(p.id)::NUMERIC / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS avg_pets
        FROM owners_pets o
        LEFT JOIN pets p ON o.id = p.owner_id
        GROUP BY email_domain
        ORDER BY avg_pets DESC
    """)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("Blues_d", len(df))
    bars   = ax.bar(df["email_domain"], df["avg_pets"], color=colors)
    ax.set_title("Average Pets Owned by Email Provider", fontweight="bold")
    ax.set_xlabel("Email Provider")
    ax.set_ylabel("Average Pets per Owner")
    for bar, cnt in zip(bars, df["owners"]):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.02,
                f"{bar.get_height():.1f}\n({cnt} owners)",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "04b_email_vs_pets.png")


# ── Q3 : Most popular pet names ───────────────────────────────────────────────
def plot_popular_pet_names():
    df = query("""
        SELECT full_name, species, COUNT(*) AS name_count
        FROM pets
        WHERE full_name IS NOT NULL
        GROUP BY full_name, species
        ORDER BY name_count DESC
        LIMIT 15
    """)

    # show all names (even count=1 makes a nice display for a small dataset)
    fig, ax = plt.subplots(figsize=(10, 6))
    color_map = {s: c for s, c in zip(df["species"].unique(),
                                       sns.color_palette("tab10", df["species"].nunique()))}
    colors = [color_map[s] for s in df["species"]]
    bars   = ax.barh(df["full_name"] + " (" + df["species"] + ")",
                     df["name_count"], color=colors)
    ax.invert_yaxis()
    ax.set_title("Most Popular Pet Names in the Dataset", fontweight="bold")
    ax.set_xlabel("Count")
    ax.set_xticks([1])
    for bar in bars:
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                str(int(bar.get_width())), va="center", fontsize=9)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=s) for s, c in color_map.items()]
    ax.legend(handles=legend_elements, title="Species", loc="lower right")
    plt.tight_layout()
    save(fig, "04c_popular_pet_names.png")


# ── Q4 : Average pet name length by species ──────────────────────────────────
def plot_name_length_by_species():
    df = query("""
        SELECT
            species,
            ROUND(AVG(LENGTH(TRIM(full_name))), 1) AS avg_name_length,
            MIN(LENGTH(TRIM(full_name)))            AS shortest,
            MAX(LENGTH(TRIM(full_name)))            AS longest
        FROM pets
        WHERE full_name IS NOT NULL
        GROUP BY species
        ORDER BY avg_name_length DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, row in df.iterrows():
        ax.plot([row["shortest"], row["longest"]],
                [row["species"], row["species"]],
                "o-", linewidth=3, markersize=8, color="#4C72B0")
        ax.plot(row["avg_name_length"], row["species"], "D",
                color="#DD8452", markersize=8,
                label="Avg length" if i == 0 else "")
    ax.set_title("Pet Name Length by Species (shortest — avg — longest chars)", fontweight="bold")
    ax.set_xlabel("Name Length (characters)")
    ax.legend()
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    save(fig, "04d_name_length_by_species.png")


# ── Q5 : Pet age gap per owner (multi-pet households) ────────────────────────
def plot_pet_age_gap():
    df = query("""
        SELECT
            o.first_name || ' ' || o.last_name AS owner,
            TRIM(o.state)                       AS state,
            COUNT(p.id)                         AS total_pets,
            MIN(p.age)                          AS youngest,
            MAX(p.age)                          AS oldest,
            MAX(p.age) - MIN(p.age)             AS age_range
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.id, o.first_name, o.last_name, o.state
        HAVING COUNT(p.id) > 1
        ORDER BY age_range DESC
    """)

    fig, ax = plt.subplots(figsize=(11, 6))
    for _, row in df.iterrows():
        ax.plot([row["youngest"], row["oldest"]],
                [row["owner"], row["owner"]],
                "o-", linewidth=2.5, markersize=7, alpha=0.8)
    ax.set_title("Age Gap Between Youngest & Oldest Pet (multi-pet owners)", fontweight="bold")
    ax.set_xlabel("Pet Age (years)")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    save(fig, "04e_pet_age_gap.png")


# ── Q6 : Bubble chart — total pets vs unique species per owner ────────────────
def plot_owner_summary_bubble():
    df = query("""
        SELECT
            o.first_name || ' ' || o.last_name             AS owner,
            TRIM(o.state)                                   AS state,
            COUNT(p.id)                                     AS total_pets,
            COUNT(DISTINCT p.species)                       AS unique_species,
            ROUND(AVG(p.age), 1)                            AS avg_pet_age
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.id, o.first_name, o.last_name, o.state
        ORDER BY total_pets DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df["total_pets"], df["unique_species"],
        s=df["avg_pet_age"] * 80,
        c=df["avg_pet_age"], cmap="YlOrRd",
        edgecolors="white", linewidths=0.7, alpha=0.85, zorder=3
    )
    plt.colorbar(scatter, ax=ax, label="Avg Pet Age (years)")
    for _, row in df.iterrows():
        ax.annotate(row["owner"].split()[-1],
                    (row["total_pets"], row["unique_species"]),
                    textcoords="offset points", xytext=(5, 4), fontsize=8)
    ax.set_title("Owner Summary: Total Pets vs Species Diversity\n(bubble size = avg pet age)",
                 fontweight="bold")
    ax.set_xlabel("Total Pets Owned")
    ax.set_ylabel("Unique Species")
    ax.set_xticks(range(1, df["total_pets"].max() + 2))
    ax.set_yticks(range(1, df["unique_species"].max() + 2))
    ax.set_axisbelow(True)
    plt.tight_layout()
    save(fig, "04f_owner_summary_bubble.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Owners & Pets — Owner Profile Analysis")
    print("=" * 60)
    plot_email_domains()
    plot_email_vs_pets()
    plot_popular_pet_names()
    plot_name_length_by_species()
    plot_pet_age_gap()
    plot_owner_summary_bubble()
    print("\nOwner profile analysis complete.")
