"""
=============================================================================
PROJECT  : Hospital Bed Management Analysis
FILE     : python/02_patient_analysis.py
PURPOSE  : Patient demographics, length of stay, and satisfaction analysis
           Mirrors: sql/02_patient_analysis.sql
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
    dbname   = os.getenv("PG_DATABASE", "hospital_db"),
)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)

SERVICE_COLOURS = {
    "emergency":        "#e74c3c",
    "surgery":          "#3498db",
    "general_medicine": "#2ecc71",
    "ICU":              "#9b59b6",
}


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Age distribution ─────────────────────────────────────────────────
def plot_age_distribution():
    df = query("SELECT age FROM patients WHERE age IS NOT NULL")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["age"], bins=18, color="steelblue", edgecolor="white", linewidth=0.5)
    ax.axvline(df["age"].median(), color="coral", linestyle="--",
               linewidth=2, label=f"Median age: {df['age'].median():.0f}")
    ax.set_title("Age Distribution of Patients", fontweight="bold")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Number of Patients")
    ax.legend()
    save(fig, "02a_patient_age_distribution.png")


# ── Q2 : Length of stay by service ───────────────────────────────────────
def plot_los_by_service():
    df = query("SELECT service, length_of_stay FROM patients")
    order = df.groupby("service")["length_of_stay"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="service", y="length_of_stay", order=order,
                palette=SERVICE_COLOURS, ax=ax,
                flierprops=dict(marker="o", markersize=3, alpha=0.4))
    ax.set_title("Length of Stay by Service", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Length of Stay (days)")
    save(fig, "02b_length_of_stay_by_service.png")


# ── Q3 : Patient satisfaction by service ─────────────────────────────────
def plot_satisfaction_by_service():
    df = query("""
        SELECT service,
               ROUND(AVG(satisfaction)::NUMERIC, 1) AS avg_satisfaction,
               COUNT(*) AS patients
        FROM patients
        GROUP BY service ORDER BY avg_satisfaction DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [SERVICE_COLOURS.get(s, "steelblue") for s in df["service"]]
    bars = ax.bar(df["service"], df["avg_satisfaction"], color=colors)
    ax.axhline(df["avg_satisfaction"].mean(), color="black", linestyle="--",
               linewidth=1.5, alpha=0.6, label=f"Overall avg: {df['avg_satisfaction'].mean():.1f}")
    for bar, val, cnt in zip(bars, df["avg_satisfaction"], df["patients"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val}\n(n={cnt})", ha="center", va="bottom", fontsize=9)
    ax.set_title("Average Patient Satisfaction by Service", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Avg Satisfaction Score")
    ax.set_ylim(0, 105)
    ax.legend()
    save(fig, "02c_satisfaction_by_service.png")


# ── Q4 : Monthly admissions ───────────────────────────────────────────────
def plot_monthly_admissions():
    df = query("""
        SELECT EXTRACT(MONTH FROM arrival_date)::INT AS month,
               COUNT(*) AS admissions,
               ROUND(AVG(length_of_stay)::NUMERIC, 1) AS avg_los
        FROM patients
        GROUP BY month ORDER BY month
    """)

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["month"], df["admissions"], color="steelblue", alpha=0.7, label="Admissions")
    ax2.plot(df["month"], df["avg_los"], "o-", color="coral",
             linewidth=2.5, markersize=7, label="Avg LOS (days)")
    ax1.set_title("Monthly Patient Admissions & Average Length of Stay", fontweight="bold")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Admissions")
    ax2.set_ylabel("Avg Length of Stay (days)")
    ax1.xaxis.set_major_locator(mticker.MultipleLocator(1))
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save(fig, "02d_monthly_admissions.png")


# ── Q5 : Age group × service heatmap ─────────────────────────────────────
def plot_age_group_service():
    df = query("""
        SELECT
            CASE
                WHEN age < 18  THEN 'Under 18'
                WHEN age < 35  THEN '18-34'
                WHEN age < 50  THEN '35-49'
                WHEN age < 65  THEN '50-64'
                ELSE '65+'
            END AS age_group,
            service,
            COUNT(*) AS patients
        FROM patients
        GROUP BY age_group, service
        ORDER BY MIN(age), service
    """)
    pivot = df.pivot(index="age_group", columns="service", values="patients").fillna(0)
    age_order = ["Under 18", "18-34", "35-49", "50-64", "65+"]
    pivot = pivot.reindex([a for a in age_order if a in pivot.index])

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Patients"})
    ax.set_title("Patient Count — Age Group × Service", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Age Group")
    plt.tight_layout()
    save(fig, "02e_age_group_service_heatmap.png")


# ── Q6 : Satisfaction by length-of-stay band ─────────────────────────────
def plot_satisfaction_by_stay_band():
    df = query("""
        SELECT
            CASE
                WHEN length_of_stay <= 3  THEN 'Short (1-3d)'
                WHEN length_of_stay <= 7  THEN 'Medium (4-7d)'
                WHEN length_of_stay <= 11 THEN 'Long (8-11d)'
                ELSE 'Extended (12+d)'
            END                                          AS stay_band,
            COUNT(*)                                     AS patients,
            ROUND(AVG(satisfaction)::NUMERIC, 1)        AS avg_satisfaction
        FROM patients
        GROUP BY stay_band
        ORDER BY MIN(length_of_stay)
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = sns.color_palette("coolwarm_r", len(df))
    bars = ax.bar(df["stay_band"], df["avg_satisfaction"], color=colors)
    for bar, cnt, val in zip(bars, df["patients"], df["avg_satisfaction"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val}\n(n={cnt})", ha="center", va="bottom", fontsize=9)
    ax.set_title("Patient Satisfaction by Length-of-Stay Band", fontweight="bold")
    ax.set_xlabel("Stay Duration")
    ax.set_ylabel("Avg Satisfaction Score")
    ax.set_ylim(0, 105)
    save(fig, "02f_satisfaction_by_stay_band.png")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Hospital — Patient Analysis")
    print("=" * 60)
    plot_age_distribution()
    plot_los_by_service()
    plot_satisfaction_by_service()
    plot_monthly_admissions()
    plot_age_group_service()
    plot_satisfaction_by_stay_band()
    print("\nPatient analysis complete.")
