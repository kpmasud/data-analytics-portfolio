"""
=============================================================================
PROJECT  : Owners & Pets Analysis
FILE     : python/01_pet_demographics.py
PURPOSE  : Analyse the pet population — species distribution, age profiles,
           and pets-per-owner breakdown
           Mirrors: sql/01_pet_demographics.sql
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


# ── Q1 : Species distribution ────────────────────────────────────────────────
def plot_species_distribution():
    df = query("""
        SELECT species, COUNT(*) AS pet_count
        FROM pets
        GROUP BY species
        ORDER BY pet_count DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Pet Species Distribution", fontweight="bold", fontsize=13)

    colors = sns.color_palette("tab10", len(df))
    sns.barplot(data=df, x="species", y="pet_count", palette=colors, ax=axes[0])
    axes[0].set_title("Pet Count by Species")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Number of Pets")
    axes[0].tick_params(axis="x", rotation=20)
    for bar in axes[0].patches:
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.1,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=10)

    axes[1].pie(df["pet_count"], labels=df["species"], colors=colors,
                autopct="%1.1f%%", startangle=140,
                textprops={"fontsize": 9})
    axes[1].set_title("Species Share")

    plt.tight_layout()
    save(fig, "01a_species_distribution.png")


# ── Q2 : Average age by species ──────────────────────────────────────────────
def plot_avg_age_by_species():
    df = query("""
        SELECT
            species,
            COUNT(*)             AS pet_count,
            ROUND(AVG(age), 1)   AS avg_age,
            MIN(age)             AS youngest,
            MAX(age)             AS oldest
        FROM pets
        WHERE age IS NOT NULL
        GROUP BY species
        ORDER BY avg_age DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = sns.barplot(data=df, x="species", y="avg_age",
                       palette="crest", ax=ax)
    ax.set_title("Average Pet Age by Species", fontweight="bold")
    ax.set_xlabel("Species")
    ax.set_ylabel("Average Age (years)")
    for bar, row in zip(ax.patches, df.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{bar.get_height():.1f} yrs\n({row.pet_count} pets)",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "01b_avg_age_by_species.png")


# ── Q3 : Age distribution (boxplot by species) ───────────────────────────────
def plot_age_distribution():
    df = query("SELECT species, age FROM pets WHERE age IS NOT NULL")

    order = df.groupby("species")["age"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=df, x="species", y="age", order=order,
                palette="Set2", ax=ax,
                flierprops=dict(marker="o", markersize=5, alpha=0.6))
    ax.axhline(df["age"].median(), color="red", linestyle="--", linewidth=1,
               label=f"Overall median: {df['age'].median():.0f} yr")
    ax.set_title("Pet Age Distribution by Species", fontweight="bold")
    ax.set_xlabel("Species")
    ax.set_ylabel("Age (years)")
    ax.legend()
    plt.tight_layout()
    save(fig, "01c_age_distribution_by_species.png")


# ── Q4 : Pets per owner ──────────────────────────────────────────────────────
def plot_pets_per_owner():
    df = query("""
        SELECT
            o.first_name || ' ' || o.last_name AS owner,
            o.state,
            COUNT(p.id) AS pet_count
        FROM owners_pets o
        LEFT JOIN pets p ON o.id = p.owner_id
        GROUP BY o.id, o.first_name, o.last_name, o.state
        ORDER BY pet_count DESC
    """)

    tier_counts = (
        df["pet_count"]
        .map(lambda x: "1 pet" if x == 1 else ("2 pets" if x == 2 else "3+ pets"))
        .value_counts()
        .reindex(["1 pet", "2 pets", "3+ pets"], fill_value=0)
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Pets Per Owner", fontweight="bold", fontsize=13)

    # Top owners bar chart
    top = df.head(12)
    colors = sns.color_palette("Blues_d", len(top))
    axes[0].barh(top["owner"] + " (" + top["state"].str.strip() + ")", top["pet_count"],
                 color=colors)
    axes[0].invert_yaxis()
    axes[0].set_title("Owners with Most Pets")
    axes[0].set_xlabel("Number of Pets")
    for i, val in enumerate(top["pet_count"]):
        axes[0].text(val + 0.05, i, str(val), va="center", fontsize=10)

    # Ownership tier
    colors2 = ["#55A868", "#4C72B0", "#DD8452"]
    axes[1].bar(tier_counts.index, tier_counts.values, color=colors2)
    axes[1].set_title("Ownership Tier Distribution")
    axes[1].set_xlabel("Pets per Owner")
    axes[1].set_ylabel("Number of Owners")
    for bar in axes[1].patches:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.1,
                     str(int(bar.get_height())),
                     ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    save(fig, "01d_pets_per_owner.png")


# ── Q5 : Species × age group heatmap ────────────────────────────────────────
def plot_species_age_heatmap():
    df = query("""
        SELECT
            species,
            CASE
                WHEN age BETWEEN 0 AND 2 THEN '0-2 yrs'
                WHEN age BETWEEN 3 AND 5 THEN '3-5 yrs'
                WHEN age BETWEEN 6 AND 9 THEN '6-9 yrs'
                ELSE '10+ yrs'
            END AS age_group,
            COUNT(*) AS pet_count
        FROM pets
        WHERE age IS NOT NULL
        GROUP BY species, age_group
    """)

    pivot = df.pivot_table(index="species", columns="age_group",
                           values="pet_count", fill_value=0)
    age_order = [c for c in ["0-2 yrs", "3-5 yrs", "6-9 yrs", "10+ yrs"] if c in pivot.columns]
    pivot = pivot[age_order]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax,
                cbar_kws={"label": "Number of Pets"})
    ax.set_title("Pet Count: Species × Age Group", fontweight="bold")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Species")
    plt.xticks(rotation=0)
    plt.tight_layout()
    save(fig, "01e_species_age_heatmap.png")


# ── Q6 : Youngest and oldest per species (range bar) ─────────────────────────
def plot_species_age_range():
    df = query("""
        SELECT
            species,
            MIN(age)           AS youngest,
            MAX(age)           AS oldest,
            ROUND(AVG(age), 1) AS avg_age
        FROM pets
        WHERE age IS NOT NULL
        GROUP BY species
        ORDER BY avg_age DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, row in df.iterrows():
        ax.plot([row["youngest"], row["oldest"]],
                [row["species"], row["species"]],
                "o-", linewidth=3, markersize=8, color="#4C72B0")
        ax.plot(row["avg_age"], row["species"], "D",
                color="#DD8452", markersize=8, label="Avg" if i == 0 else "")
    ax.set_title("Pet Age Range by Species (youngest — avg — oldest)", fontweight="bold")
    ax.set_xlabel("Age (years)")
    ax.legend()
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    save(fig, "01f_species_age_range.png")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Owners & Pets — Pet Demographics")
    print("=" * 60)
    plot_species_distribution()
    plot_avg_age_by_species()
    plot_age_distribution()
    plot_pets_per_owner()
    plot_species_age_heatmap()
    plot_species_age_range()
    print("\nPet demographics analysis complete.")
