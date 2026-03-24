"""
=============================================================================
PROJECT  : Hospital Bed Management Analysis
FILE     : python/03_staff_analysis.py
PURPOSE  : Staff roster, attendance rates, and morale trend analysis
           Mirrors: sql/03_staff_analysis.sql
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


def query(sql):
    with psycopg2.connect(**PG) as conn:
        return pd.read_sql(sql, conn)


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: outputs/{name}")


# ── Q1 : Staff count by role and service ─────────────────────────────────
def plot_staff_count():
    df = query("""
        SELECT service, role, COUNT(*) AS staff_count
        FROM staff GROUP BY service, role ORDER BY service, role
    """)
    pivot = df.pivot(index="service", columns="role", values="staff_count").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax, colormap="Set2", width=0.6)
    ax.set_title("Staff Count by Role and Service", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Number of Staff")
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="Role")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=2, fontsize=9)
    plt.tight_layout()
    save(fig, "03a_staff_count_by_role_service.png")


# ── Q2 : Weekly attendance rate by service ────────────────────────────────
def plot_weekly_attendance():
    df = query("""
        SELECT ss.week, ss.service,
               ROUND(SUM(ss.present) * 100.0 / NULLIF(COUNT(*), 0), 1) AS attendance_pct
        FROM staff_schedule ss
        GROUP BY ss.week, ss.service
        ORDER BY ss.week, ss.service
    """)

    fig, ax = plt.subplots(figsize=(13, 5))
    for service, grp in df.groupby("service"):
        ax.plot(grp["week"], grp["attendance_pct"], linewidth=1.8,
                label=service, alpha=0.85)
    ax.set_title("Weekly Staff Attendance Rate by Service", fontweight="bold")
    ax.set_xlabel("Week")
    ax.set_ylabel("Attendance Rate (%)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.legend(title="Service")
    ax.set_ylim(50, 105)
    plt.tight_layout()
    save(fig, "03b_weekly_attendance_by_service.png")


# ── Q3 : Staff morale trend by month ─────────────────────────────────────
def plot_morale_trend():
    df = query("""
        SELECT month,
               ROUND(AVG(staff_morale)::NUMERIC, 1) AS avg_morale,
               ROUND(MIN(staff_morale)::NUMERIC, 1) AS min_morale,
               ROUND(MAX(staff_morale)::NUMERIC, 1) AS max_morale
        FROM bed_metrics GROUP BY month ORDER BY month
    """)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.fill_between(df["month"], df["min_morale"], df["max_morale"],
                    alpha=0.15, color="steelblue", label="Min–Max range")
    ax.plot(df["month"], df["avg_morale"], "o-", color="steelblue",
            linewidth=2.5, markersize=8, label="Avg Morale")
    ax.set_title("Staff Morale Trend by Month", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Staff Morale Score (0–100)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.set_ylim(0, 110)
    ax.legend()
    for _, row in df.iterrows():
        ax.text(row["month"], row["avg_morale"] + 2, f"{row['avg_morale']:.0f}",
                ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    save(fig, "03c_staff_morale_trend.png")


# ── Q4 : Attendance rate by role ──────────────────────────────────────────
def plot_attendance_by_role():
    df = query("""
        SELECT role,
               COUNT(*) AS total_shifts,
               SUM(present) AS attended,
               ROUND(SUM(present) * 100.0 / NULLIF(COUNT(*), 0), 1) AS attendance_pct
        FROM staff_schedule GROUP BY role ORDER BY attendance_pct DESC
    """)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = sns.color_palette("Set2", len(df))
    bars = ax.bar(df["role"], df["attendance_pct"], color=colors)
    for bar, val, shifts in zip(bars, df["attendance_pct"], df["total_shifts"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val}%\n({shifts:,} shifts)", ha="center", va="bottom", fontsize=9)
    ax.set_title("Staff Attendance Rate by Role", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Attendance Rate (%)")
    ax.set_ylim(0, 110)
    save(fig, "03d_attendance_by_role.png")


# ── Q5 : Attendance heatmap — service × month ─────────────────────────────
def plot_attendance_heatmap():
    df = query("""
        SELECT bm.month, ss.service,
               ROUND(SUM(ss.present) * 100.0 / NULLIF(COUNT(*), 0), 1) AS attendance_pct
        FROM staff_schedule ss
        JOIN (SELECT DISTINCT week, month FROM bed_metrics) bm ON ss.week = bm.week
        GROUP BY bm.month, ss.service
        ORDER BY bm.month, ss.service
    """)
    pivot = df.pivot(index="service", columns="month", values="attendance_pct")

    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn",
                linewidths=0.5, ax=ax, cbar_kws={"label": "Attendance %"},
                vmin=60, vmax=100)
    ax.set_title("Staff Attendance % — Service × Month", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("")
    plt.tight_layout()
    save(fig, "03e_attendance_heatmap.png")


# ── Q6 : Staff morale vs patient satisfaction ────────────────────────────
def plot_morale_vs_satisfaction():
    df = query("""
        SELECT week, service,
               ROUND(patient_satisfaction::NUMERIC, 1) AS patient_satisfaction,
               ROUND(staff_morale::NUMERIC, 1)         AS staff_morale
        FROM bed_metrics
    """)

    fig, ax = plt.subplots(figsize=(9, 6))
    for service, grp in df.groupby("service"):
        ax.scatter(grp["staff_morale"], grp["patient_satisfaction"],
                   label=service, alpha=0.6, s=40)
    ax.plot([0, 110], [0, 110], "k--", alpha=0.3, linewidth=1, label="y = x")
    ax.set_title("Staff Morale vs Patient Satisfaction (by Week & Service)", fontweight="bold")
    ax.set_xlabel("Staff Morale Score")
    ax.set_ylabel("Patient Satisfaction Score")
    ax.legend(title="Service")
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 110)
    plt.tight_layout()
    save(fig, "03f_morale_vs_satisfaction.png")


# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Hospital — Staff Analysis")
    print("=" * 60)
    plot_staff_count()
    plot_weekly_attendance()
    plot_morale_trend()
    plot_attendance_by_role()
    plot_attendance_heatmap()
    plot_morale_vs_satisfaction()
    print("\nStaff analysis complete.")
