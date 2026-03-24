"""
=============================================================================
PROJECT  : Hospital Bed Management Analysis
FILE     : python/01_bed_utilisation.py
PURPOSE  : Bed capacity, admission rates, refusal and occupancy analysis
           Mirrors: sql/01_bed_utilisation.sql
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
    "emergency":       "#e74c3c",
    "surgery":         "#3498db",
    "general_medicine": "#2ecc71",
    "ICU":             "#9b59b6",
}


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Admission rate by service ────────────────────────────────────────
def plot_admission_rate_by_service():
    df = query("""
        SELECT service,
               ROUND(AVG(admission_rate)::NUMERIC, 1)   AS avg_admission_rate,
               SUM(patients_admitted)                   AS total_admitted,
               SUM(patients_refused)                    AS total_refused
        FROM bed_metrics
        GROUP BY service
        ORDER BY avg_admission_rate DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [SERVICE_COLOURS.get(s, "steelblue") for s in df["service"]]
    bars = ax.bar(df["service"], df["avg_admission_rate"], color=colors)
    for bar, val in zip(bars, df["avg_admission_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Average Admission Rate by Service", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Avg Admission Rate (%)")
    ax.set_ylim(0, 100)
    save(fig, "01a_admission_rate_by_service.png")


# ── Q2 : Weekly occupancy trend ───────────────────────────────────────────
def plot_weekly_occupancy():
    df = query("""
        SELECT week,
               ROUND(SUM(patients_admitted) * 100.0 /
                   NULLIF(SUM(available_beds), 0), 1) AS occupancy_pct
        FROM bed_metrics
        GROUP BY week ORDER BY week
    """)

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.fill_between(df["week"], df["occupancy_pct"], alpha=0.15, color="steelblue")
    ax.plot(df["week"], df["occupancy_pct"], "o-", color="steelblue",
            linewidth=2, markersize=4)
    ax.axhline(df["occupancy_pct"].mean(), color="coral", linestyle="--",
               linewidth=1.5, label=f"Annual avg: {df['occupancy_pct'].mean():.1f}%")
    ax.set_title("Weekly Bed Occupancy Rate (All Services)", fontweight="bold")
    ax.set_xlabel("Week")
    ax.set_ylabel("Occupancy (%)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.legend()
    plt.tight_layout()
    save(fig, "01b_weekly_occupancy_trend.png")


# ── Q3 : Monthly refusal rate ─────────────────────────────────────────────
def plot_monthly_refusal_rate():
    df = query("""
        SELECT month,
               SUM(patients_request)  AS total_requested,
               SUM(patients_refused)  AS total_refused,
               ROUND(SUM(patients_refused) * 100.0 /
                   NULLIF(SUM(patients_request), 0), 1) AS refusal_rate_pct
        FROM bed_metrics
        GROUP BY month ORDER BY month
    """)

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["month"], df["total_refused"], color="coral", alpha=0.7, label="Patients Refused")
    ax2.plot(df["month"], df["refusal_rate_pct"], "o-", color="darkred",
             linewidth=2.5, markersize=7, label="Refusal Rate %")
    ax1.set_title("Monthly Patient Refusal — Count & Rate", fontweight="bold")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Patients Refused")
    ax2.set_ylabel("Refusal Rate (%)")
    ax1.xaxis.set_major_locator(mticker.MultipleLocator(1))
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save(fig, "01c_monthly_refusal_rate.png")


# ── Q4 : Event impact on admission rate ───────────────────────────────────
def plot_event_impact():
    df = query("""
        SELECT event,
               COUNT(*)                                        AS weeks_affected,
               ROUND(AVG(admission_rate)::NUMERIC, 1)         AS avg_admission_rate,
               ROUND(AVG(patients_refused)::NUMERIC, 1)       AS avg_refused,
               ROUND(AVG(patient_satisfaction)::NUMERIC, 1)   AS avg_satisfaction
        FROM bed_metrics
        GROUP BY event ORDER BY avg_admission_rate DESC
    """)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Impact of Events on Hospital Operations", fontweight="bold")
    palette = sns.color_palette("Set2", len(df))

    metrics = [
        ("avg_admission_rate", "Avg Admission Rate (%)", "01d"),
        ("avg_refused",        "Avg Patients Refused",   "01d"),
        ("avg_satisfaction",   "Avg Patient Satisfaction", "01d"),
    ]
    labels = ["Admission Rate (%)", "Avg Refused / Week", "Patient Satisfaction"]

    for ax, (col, _, _), label in zip(axes, metrics, labels):
        bars = ax.bar(df["event"], df[col], color=palette)
        for bar, val in zip(bars, df[col]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{val}", ha="center", va="bottom", fontsize=9)
        ax.set_title(label, fontweight="bold")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=15)

    plt.tight_layout()
    save(fig, "01d_event_impact.png")


# ── Q5 : Most overcrowded service ─────────────────────────────────────────
def plot_overcrowded_service():
    df = query("""
        SELECT service,
               ROUND(AVG(patients_refused)::NUMERIC, 1)  AS avg_refused_per_week,
               SUM(patients_refused)                     AS total_refused_annual
        FROM bed_metrics
        GROUP BY service ORDER BY avg_refused_per_week DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [SERVICE_COLOURS.get(s, "steelblue") for s in df["service"]]
    bars = ax.barh(df["service"], df["avg_refused_per_week"], color=colors)
    for bar, total in zip(bars, df["total_refused_annual"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"Total: {total:,}", va="center", fontsize=9)
    ax.set_title("Average Weekly Patients Refused by Service", fontweight="bold")
    ax.set_xlabel("Avg Patients Refused per Week")
    save(fig, "01e_overcrowded_service.png")


# ── Q6 : Occupancy heatmap by service × month ─────────────────────────────
def plot_occupancy_heatmap():
    df = query("""
        SELECT month, service,
               ROUND(SUM(patients_admitted) * 100.0 /
                   NULLIF(SUM(available_beds), 0), 1) AS occupancy_pct
        FROM bed_metrics
        GROUP BY month, service
        ORDER BY month, service
    """)
    pivot = df.pivot(index="service", columns="month", values="occupancy_pct")

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Occupancy %"})
    ax.set_title("Bed Occupancy % — Service × Month", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("")
    plt.tight_layout()
    save(fig, "01f_occupancy_heatmap.png")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Hospital — Bed Utilisation Analysis")
    print("=" * 60)
    plot_admission_rate_by_service()
    plot_weekly_occupancy()
    plot_monthly_refusal_rate()
    plot_event_impact()
    plot_overcrowded_service()
    plot_occupancy_heatmap()
    print("\nBed utilisation analysis complete.")
