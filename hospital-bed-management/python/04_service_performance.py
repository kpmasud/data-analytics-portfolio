"""
=============================================================================
PROJECT  : Hospital Bed Management Analysis
FILE     : python/04_service_performance.py
PURPOSE  : Cross-service KPIs, event impact, demand & performance trends
           Mirrors: sql/04_service_performance.sql
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


# ── Q1 : KPI summary per service ─────────────────────────────────────────
def plot_kpi_summary():
    df = query("""
        SELECT service,
               ROUND(AVG(admission_rate)::NUMERIC, 1)       AS avg_admission_rate,
               ROUND(AVG(patient_satisfaction)::NUMERIC, 1) AS avg_satisfaction,
               ROUND(AVG(staff_morale)::NUMERIC, 1)         AS avg_morale
        FROM bed_metrics GROUP BY service ORDER BY service
    """)

    metrics = ["avg_admission_rate", "avg_satisfaction", "avg_morale"]
    labels  = ["Admission Rate (%)", "Patient Satisfaction", "Staff Morale"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Key Performance Indicators by Service", fontweight="bold", fontsize=14)

    for ax, col, label in zip(axes, metrics, labels):
        colors = [SERVICE_COLOURS.get(s, "steelblue") for s in df["service"]]
        bars = ax.bar(df["service"], df[col], color=colors)
        for bar, val in zip(bars, df[col]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title(label, fontweight="bold")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=15)
        ax.set_ylim(0, 110)

    plt.tight_layout()
    save(fig, "04a_kpi_by_service.png")


# ── Q2 : Event impact on all KPIs ────────────────────────────────────────
def plot_event_kpi_impact():
    df = query("""
        SELECT event,
               ROUND(AVG(admission_rate)::NUMERIC, 1)       AS avg_admission_rate,
               ROUND(AVG(patient_satisfaction)::NUMERIC, 1) AS avg_satisfaction,
               ROUND(AVG(staff_morale)::NUMERIC, 1)         AS avg_morale
        FROM bed_metrics GROUP BY event ORDER BY avg_morale ASC
    """)

    x = range(len(df))
    width = 0.25
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar([i - width for i in x], df["avg_admission_rate"], width=width,
           label="Admission Rate (%)", color="steelblue")
    ax.bar(x,                       df["avg_satisfaction"],  width=width,
           label="Patient Satisfaction", color="seagreen")
    ax.bar([i + width for i in x], df["avg_morale"],         width=width,
           label="Staff Morale", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(df["event"])
    ax.set_title("Event Impact on Key Metrics", fontweight="bold")
    ax.set_ylabel("Score / Rate")
    ax.legend()
    ax.set_ylim(0, 110)
    plt.tight_layout()
    save(fig, "04b_event_kpi_impact.png")


# ── Q3 : Month-over-month demand growth ──────────────────────────────────
def plot_demand_growth():
    df = query("""
        WITH monthly AS (
            SELECT month,
                   SUM(patients_request)  AS total_requested,
                   SUM(patients_admitted) AS total_admitted
            FROM bed_metrics GROUP BY month
        )
        SELECT month, total_requested, total_admitted,
               ROUND(
                   (total_requested - LAG(total_requested) OVER (ORDER BY month)) * 100.0 /
                   NULLIF(LAG(total_requested) OVER (ORDER BY month), 0), 1
               ) AS demand_growth_pct
        FROM monthly ORDER BY month
    """)

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["month"], df["total_requested"], color="steelblue", alpha=0.6, label="Total Requested")
    ax1.bar(df["month"], df["total_admitted"],  color="seagreen",  alpha=0.7, label="Total Admitted")
    ax2.plot(df["month"].iloc[1:], df["demand_growth_pct"].iloc[1:],
             "o-", color="coral", linewidth=2.5, markersize=7, label="MoM Growth %")
    ax2.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    ax1.set_title("Month-over-Month Patient Demand Growth", fontweight="bold")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Patient Count")
    ax2.set_ylabel("MoM Growth (%)")
    ax1.xaxis.set_major_locator(mticker.MultipleLocator(1))
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save(fig, "04c_demand_growth.png")


# ── Q4 : High-pressure weeks — satisfaction by service ───────────────────
def plot_high_pressure_satisfaction():
    df = query("""
        WITH avg_refused AS (SELECT AVG(patients_refused) AS threshold FROM bed_metrics)
        SELECT bm.service,
               COUNT(*) AS high_pressure_weeks,
               ROUND(AVG(bm.patient_satisfaction)::NUMERIC, 1) AS avg_satisfaction,
               ROUND(AVG(bm.staff_morale)::NUMERIC, 1)         AS avg_morale
        FROM bed_metrics bm, avg_refused ar
        WHERE bm.patients_refused > ar.threshold
        GROUP BY bm.service ORDER BY avg_satisfaction DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(df))
    width = 0.35
    bars1 = ax.bar([i - width / 2 for i in x], df["avg_satisfaction"], width=width,
                   label="Patient Satisfaction", color="steelblue")
    bars2 = ax.bar([i + width / 2 for i in x], df["avg_morale"], width=width,
                   label="Staff Morale", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(df["service"], rotation=15)
    ax.set_title("Satisfaction & Morale During High-Pressure Weeks", fontweight="bold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 110)
    ax.legend()
    for bars in [bars1, bars2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{bar.get_height():.0f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    save(fig, "04d_high_pressure_satisfaction.png")


# ── Q5 : Morale vs satisfaction scatter by service ────────────────────────
def plot_morale_satisfaction_by_service():
    df = query("""
        SELECT service,
               ROUND(AVG(staff_morale)::NUMERIC, 1)          AS avg_morale,
               ROUND(AVG(patient_satisfaction)::NUMERIC, 1)  AS avg_satisfaction,
               ROUND(AVG(admission_rate)::NUMERIC, 1)        AS avg_admission_rate
        FROM bed_metrics GROUP BY service
    """)

    fig, ax = plt.subplots(figsize=(8, 6))
    for _, row in df.iterrows():
        color = SERVICE_COLOURS.get(row["service"], "grey")
        ax.scatter(row["avg_morale"], row["avg_satisfaction"],
                   s=row["avg_admission_rate"] * 15, color=color,
                   alpha=0.8, edgecolors="white", linewidth=1.5)
        ax.annotate(row["service"], (row["avg_morale"], row["avg_satisfaction"]),
                    textcoords="offset points", xytext=(8, 4), fontsize=10)
    ax.set_title("Avg Morale vs Avg Satisfaction per Service\n(bubble size = admission rate)",
                 fontweight="bold")
    ax.set_xlabel("Avg Staff Morale")
    ax.set_ylabel("Avg Patient Satisfaction")
    ax.set_xlim(50, 90)
    ax.set_ylim(50, 90)
    plt.tight_layout()
    save(fig, "04e_morale_satisfaction_scatter.png")


# ── Q6 : Best and worst performing weeks ─────────────────────────────────
def plot_weekly_composite_score():
    df = query("""
        SELECT week,
               ROUND((AVG(admission_rate) + AVG(patient_satisfaction) +
                      AVG(staff_morale)) / 3.0, 1) AS composite_score
        FROM bed_metrics GROUP BY week ORDER BY week
    """)

    fig, ax = plt.subplots(figsize=(13, 5))
    colors = ["seagreen" if s >= df["composite_score"].quantile(0.75)
              else ("coral" if s <= df["composite_score"].quantile(0.25) else "steelblue")
              for s in df["composite_score"]]
    ax.bar(df["week"], df["composite_score"], color=colors)
    ax.axhline(df["composite_score"].mean(), color="black", linestyle="--",
               linewidth=1.5, alpha=0.6, label=f"Avg: {df['composite_score'].mean():.1f}")
    ax.set_title("Weekly Composite Performance Score\n(green = top 25%, red = bottom 25%)",
                 fontweight="bold")
    ax.set_xlabel("Week")
    ax.set_ylabel("Composite Score")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.legend()
    plt.tight_layout()
    save(fig, "04f_weekly_composite_score.png")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Hospital — Service Performance Analysis")
    print("=" * 60)
    plot_kpi_summary()
    plot_event_kpi_impact()
    plot_demand_growth()
    plot_high_pressure_satisfaction()
    plot_morale_satisfaction_by_service()
    plot_weekly_composite_score()
    print("\nService performance analysis complete.")
