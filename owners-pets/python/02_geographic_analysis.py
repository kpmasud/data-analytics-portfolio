"""
=============================================================================
PROJECT  : Owners & Pets Analysis
FILE     : python/02_geographic_analysis.py
PURPOSE  : Analyse the geographic spread of owners and pets across
           US states and cities, and email domain preferences
           Mirrors: sql/02_geographic_analysis.sql
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


# ── Q1 : Owners by state ─────────────────────────────────────────────────────
def plot_owners_by_state():
    df = query("""
        SELECT state, COUNT(*) AS owner_count
        FROM owners_pets
        GROUP BY state
        ORDER BY owner_count DESC
    """)
    df["state"] = df["state"].str.strip()

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = sns.color_palette("Blues_d", len(df))
    bars   = ax.bar(df["state"], df["owner_count"], color=colors)
    ax.set_title("Owner Count by US State", fontweight="bold")
    ax.set_xlabel("State")
    ax.set_ylabel("Number of Owners")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                str(int(bar.get_height())),
                ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    save(fig, "02a_owners_by_state.png")


# ── Q2 : Pets by state ───────────────────────────────────────────────────────
def plot_pets_by_state():
    df = query("""
        SELECT
            o.state,
            COUNT(p.id)         AS pet_count,
            ROUND(AVG(p.age), 1) AS avg_pet_age
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.state
        ORDER BY pet_count DESC
    """)
    df["state"] = df["state"].str.strip()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Pet Distribution by State", fontweight="bold", fontsize=13)

    colors = sns.color_palette("Greens_d", len(df))
    axes[0].bar(df["state"], df["pet_count"], color=colors)
    axes[0].set_title("Pet Count by State")
    axes[0].set_xlabel("State")
    axes[0].set_ylabel("Number of Pets")
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.05,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=9)

    colors2 = sns.color_palette("Oranges_d", len(df))
    axes[1].bar(df["state"], df["avg_pet_age"], color=colors2)
    axes[1].set_title("Average Pet Age by State (years)")
    axes[1].set_xlabel("State")
    axes[1].set_ylabel("Average Age (years)")
    for bar, val in zip(axes[1].patches, df["avg_pet_age"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.05,
                     f"{val:.1f}",
                     ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    save(fig, "02b_pets_by_state.png")


# ── Q3 : Owners and pets by city ─────────────────────────────────────────────
def plot_city_overview():
    df = query("""
        SELECT
            TRIM(o.city)               AS city,
            TRIM(o.state)              AS state,
            COUNT(DISTINCT o.id)       AS owners,
            COUNT(p.id)                AS pets
        FROM owners_pets o
        LEFT JOIN pets p ON o.id = p.owner_id
        GROUP BY o.city, o.state
        ORDER BY pets DESC
    """)
    df["city_state"] = df["city"] + " (" + df["state"] + ")"

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Owners and Pets by City", fontweight="bold", fontsize=13)

    colors1 = sns.color_palette("Blues_d", len(df))
    axes[0].barh(df["city_state"], df["owners"], color=colors1)
    axes[0].invert_yaxis()
    axes[0].set_title("Owners per City")
    axes[0].set_xlabel("Number of Owners")
    for i, val in enumerate(df["owners"]):
        axes[0].text(val + 0.05, i, str(val), va="center", fontsize=9)

    colors2 = sns.color_palette("Greens_d", len(df))
    axes[1].barh(df["city_state"], df["pets"], color=colors2)
    axes[1].invert_yaxis()
    axes[1].set_title("Pets per City")
    axes[1].set_xlabel("Number of Pets")
    for i, val in enumerate(df["pets"]):
        axes[1].text(val + 0.05, i, str(val), va="center", fontsize=9)

    plt.tight_layout()
    save(fig, "02c_city_overview.png")


# ── Q4 : Email domain distribution ───────────────────────────────────────────
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

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("tab10", len(df))
    wedges, texts, autotexts = ax.pie(
        df["owner_count"], labels=df["email_domain"], colors=colors,
        autopct="%1.1f%%", startangle=140,
        textprops={"fontsize": 11}
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Email Provider Distribution Among Owners", fontweight="bold")
    plt.tight_layout()
    save(fig, "02d_email_domains.png")


# ── Q5 : US region analysis ───────────────────────────────────────────────────
def plot_region_analysis():
    df = query("""
        SELECT
            CASE TRIM(state)
                WHEN 'NY' THEN 'Northeast' WHEN 'MA' THEN 'Northeast'
                WHEN 'PA' THEN 'Northeast' WHEN 'NJ' THEN 'Northeast'
                WHEN 'FL' THEN 'South'     WHEN 'GA' THEN 'South'
                WHEN 'NC' THEN 'South'     WHEN 'TN' THEN 'South'
                WHEN 'TX' THEN 'South'
                WHEN 'IL' THEN 'Midwest'   WHEN 'OH' THEN 'Midwest'
                WHEN 'MI' THEN 'Midwest'
                WHEN 'CA' THEN 'West'      WHEN 'WA' THEN 'West'
                WHEN 'CO' THEN 'West'      WHEN 'AZ' THEN 'West'
                ELSE 'Other'
            END AS region,
            COUNT(DISTINCT o.id) AS owners,
            COUNT(p.id)          AS pets
        FROM owners_pets o
        LEFT JOIN pets p ON o.id = p.owner_id
        GROUP BY region
        ORDER BY owners DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Owner & Pet Distribution by US Region", fontweight="bold", fontsize=13)

    colors = sns.color_palette("Set2", len(df))
    axes[0].bar(df["region"], df["owners"], color=colors)
    axes[0].set_title("Owners by Region")
    axes[0].set_ylabel("Number of Owners")
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     str(int(bar.get_height())), ha="center", va="bottom", fontsize=10)

    axes[1].bar(df["region"], df["pets"], color=colors)
    axes[1].set_title("Pets by Region")
    axes[1].set_ylabel("Number of Pets")
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     str(int(bar.get_height())), ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    save(fig, "02e_region_analysis.png")


# ── Q6 : Pets per owner ratio ranked by state ─────────────────────────────────
def plot_pets_per_owner_by_state():
    df = query("""
        SELECT
            TRIM(o.state)                                               AS state,
            COUNT(DISTINCT o.id)                                        AS owners,
            COUNT(p.id)                                                 AS pets,
            ROUND(COUNT(p.id)::NUMERIC / NULLIF(COUNT(DISTINCT o.id),0), 2) AS pets_per_owner
        FROM owners_pets o
        LEFT JOIN pets p ON o.id = p.owner_id
        GROUP BY TRIM(o.state)
        ORDER BY pets_per_owner DESC
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = sns.color_palette("crest", len(df))
    bars   = ax.bar(df["state"], df["pets_per_owner"], color=colors)
    ax.set_title("Average Pets Per Owner by State", fontweight="bold")
    ax.set_xlabel("State")
    ax.set_ylabel("Pets per Owner")
    for bar, cnt in zip(bars, df["owners"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{bar.get_height():.1f}\n({cnt} owner{'s' if cnt>1 else ''})",
                ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    save(fig, "02f_pets_per_owner_by_state.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Owners & Pets — Geographic Analysis")
    print("=" * 60)
    plot_owners_by_state()
    plot_pets_by_state()
    plot_city_overview()
    plot_email_domains()
    plot_region_analysis()
    plot_pets_per_owner_by_state()
    print("\nGeographic analysis complete.")
