"""
=============================================================================
PROJECT  : Owners & Pets Analysis
FILE     : python/03_owner_pet_relationships.py
PURPOSE  : Explore owner-pet relationships — ownership tiers, species
           preferences by state, and species diversity per owner
           Mirrors: sql/03_owner_pet_relationships.sql
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


# ── Q1 : Multi-pet vs single-pet owners ──────────────────────────────────────
def plot_ownership_tiers():
    df = query("""
        SELECT
            CASE
                WHEN pet_count = 1 THEN '1 pet'
                WHEN pet_count = 2 THEN '2 pets'
                ELSE '3+ pets'
            END AS ownership_tier,
            COUNT(*) AS owner_count
        FROM (
            SELECT o.id, COUNT(p.id) AS pet_count
            FROM owners_pets o
            LEFT JOIN pets p ON o.id = p.owner_id
            GROUP BY o.id
        ) t
        GROUP BY ownership_tier
    """)

    order  = ["1 pet", "2 pets", "3+ pets"]
    df     = df.set_index("ownership_tier").reindex(order).reset_index()
    colors = ["#55A868", "#4C72B0", "#DD8452"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(df["ownership_tier"], df["owner_count"], color=colors)
    ax.set_title("Owner Distribution by Number of Pets", fontweight="bold")
    ax.set_xlabel("Pets per Owner")
    ax.set_ylabel("Number of Owners")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(int(bar.get_height())),
                ha="center", va="bottom", fontsize=12, fontweight="bold")
    plt.tight_layout()
    save(fig, "03a_ownership_tiers.png")


# ── Q2 : Most popular species by state (horizontal grouped bar) ──────────────
def plot_species_by_state():
    df = query("""
        SELECT
            TRIM(o.state) AS state,
            p.species,
            COUNT(*) AS pet_count
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.state, p.species
    """)

    pivot = df.pivot_table(index="state", columns="species",
                           values="pet_count", fill_value=0)

    fig, ax = plt.subplots(figsize=(13, 7))
    pivot.plot(kind="bar", ax=ax, colormap="tab10", edgecolor="white", linewidth=0.5)
    ax.set_title("Pet Species Count by State", fontweight="bold")
    ax.set_xlabel("State")
    ax.set_ylabel("Number of Pets")
    ax.legend(title="Species", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    save(fig, "03b_species_by_state.png")


# ── Q3 : Species × State heatmap ────────────────────────────────────────────
def plot_species_state_heatmap():
    df = query("""
        SELECT
            TRIM(o.state) AS state,
            p.species,
            COUNT(*) AS count
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.state, p.species
    """)

    pivot = df.pivot_table(index="species", columns="state",
                           values="count", fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax,
                cbar_kws={"label": "Number of Pets"})
    ax.set_title("Pet Count: Species × State", fontweight="bold")
    ax.set_xlabel("State")
    ax.set_ylabel("Species")
    plt.xticks(rotation=0)
    plt.tight_layout()
    save(fig, "03c_species_state_heatmap.png")


# ── Q4 : Species diversity per owner ────────────────────────────────────────
def plot_species_diversity():
    df = query("""
        SELECT
            o.first_name || ' ' || o.last_name  AS owner,
            TRIM(o.state)                        AS state,
            COUNT(p.id)                          AS total_pets,
            COUNT(DISTINCT p.species)            AS unique_species
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.id, o.first_name, o.last_name, o.state
        ORDER BY unique_species DESC, total_pets DESC
        LIMIT 15
    """)

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(df["total_pets"], df["unique_species"],
                         s=120, c=df["unique_species"],
                         cmap="viridis", edgecolors="white", linewidths=0.8,
                         zorder=3)
    for _, row in df.iterrows():
        ax.annotate(row["owner"].split()[-1] + f" ({row['state']})",
                    (row["total_pets"], row["unique_species"]),
                    textcoords="offset points", xytext=(5, 4), fontsize=8)
    plt.colorbar(scatter, ax=ax, label="Unique Species Count")
    ax.set_title("Owner Species Diversity vs Total Pets", fontweight="bold")
    ax.set_xlabel("Total Number of Pets")
    ax.set_ylabel("Number of Unique Species")
    ax.set_xticks(range(1, df["total_pets"].max() + 2))
    ax.set_yticks(range(1, df["unique_species"].max() + 2))
    ax.set_axisbelow(True)
    plt.tight_layout()
    save(fig, "03d_species_diversity.png")


# ── Q5 : Top owners by species diversity (bar + annotation) ──────────────────
def plot_diversity_ranking():
    df = query("""
        SELECT
            o.first_name || ' ' || o.last_name     AS owner,
            TRIM(o.state)                           AS state,
            COUNT(p.id)                             AS total_pets,
            COUNT(DISTINCT p.species)               AS unique_species
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY o.id, o.first_name, o.last_name, o.state
        ORDER BY unique_species DESC, total_pets DESC
        LIMIT 12
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("viridis", df["unique_species"].nunique())
    color_map = {v: colors[i] for i, v in enumerate(sorted(df["unique_species"].unique(), reverse=True))}

    bars = ax.barh(df["owner"] + " (" + df["state"] + ")",
                   df["total_pets"],
                   color=[color_map[s] for s in df["unique_species"]])
    ax.invert_yaxis()
    ax.set_title("Top Owners by Species Diversity", fontweight="bold")
    ax.set_xlabel("Total Pets Owned")
    for bar, row in zip(bars, df.itertuples()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f"{row.unique_species} species",
                va="center", fontsize=9)
    plt.tight_layout()
    save(fig, "03e_diversity_ranking.png")


# ── Q6 : Pet count by species per city (grouped bar) ─────────────────────────
def plot_species_per_city():
    df = query("""
        SELECT
            TRIM(o.city)  AS city,
            p.species,
            COUNT(*)      AS pet_count
        FROM owners_pets o
        JOIN pets p ON o.id = p.owner_id
        GROUP BY TRIM(o.city), p.species
        ORDER BY city
    """)

    pivot = df.pivot_table(index="city", columns="species",
                           values="pet_count", fill_value=0)
    # only cities with 2+ owners
    city_owners = query("""
        SELECT TRIM(city) AS city, COUNT(*) AS n FROM owners_pets GROUP BY TRIM(city) HAVING COUNT(*) >= 2
    """)
    pivot = pivot[pivot.index.isin(city_owners["city"])]

    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", ax=ax, colormap="tab10", edgecolor="white", linewidth=0.4)
    ax.set_title("Pet Species Count per City (cities with 2+ owners)", fontweight="bold")
    ax.set_xlabel("City")
    ax.set_ylabel("Number of Pets")
    ax.legend(title="Species", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    save(fig, "03f_species_per_city.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Owners & Pets — Relationship Analysis")
    print("=" * 60)
    plot_ownership_tiers()
    plot_species_by_state()
    plot_species_state_heatmap()
    plot_species_diversity()
    plot_diversity_ranking()
    plot_species_per_city()
    print("\nOwner-pet relationship analysis complete.")
