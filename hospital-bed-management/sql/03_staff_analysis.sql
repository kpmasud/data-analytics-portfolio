-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/03_staff_analysis.sql
-- PURPOSE  : Staff roster, attendance rates, morale trends
-- =============================================================================

-- Q1: Staff count by role and service
SELECT service, role,
       COUNT(*) AS staff_count
FROM staff
GROUP BY service, role
ORDER BY service, role;


-- Q2: Weekly attendance rate by service
SELECT ss.week,
       ss.service,
       COUNT(*)                                              AS scheduled,
       SUM(ss.present)                                      AS present,
       ROUND(SUM(ss.present) * 100.0 / NULLIF(COUNT(*), 0), 1) AS attendance_pct
FROM staff_schedule ss
GROUP BY ss.week, ss.service
ORDER BY ss.week, ss.service;


-- Q3: Staff morale trend by month (from bed_metrics)
SELECT month,
       ROUND(AVG(staff_morale)::NUMERIC, 1)    AS avg_morale,
       ROUND(MIN(staff_morale)::NUMERIC, 1)    AS min_morale,
       ROUND(MAX(staff_morale)::NUMERIC, 1)    AS max_morale
FROM bed_metrics
GROUP BY month
ORDER BY month;


-- Q4: Attendance rate by role across all weeks
SELECT role,
       COUNT(*)                                              AS total_shifts,
       SUM(present)                                         AS attended,
       ROUND(SUM(present) * 100.0 / NULLIF(COUNT(*), 0), 1) AS attendance_pct
FROM staff_schedule
GROUP BY role
ORDER BY attendance_pct DESC;


-- Q5: Attendance heatmap — service × month (via week → month mapping from bed_metrics)
SELECT bm.month,
       ss.service,
       COUNT(ss.present)                                          AS scheduled,
       SUM(ss.present)                                           AS attended,
       ROUND(SUM(ss.present) * 100.0 / NULLIF(COUNT(*), 0), 1)  AS attendance_pct
FROM staff_schedule ss
JOIN (SELECT DISTINCT week, month FROM bed_metrics) bm
    ON ss.week = bm.week
GROUP BY bm.month, ss.service
ORDER BY bm.month, ss.service;


-- Q6: Staff morale vs patient satisfaction — weekly comparison by service
SELECT week, service,
       ROUND(patient_satisfaction::NUMERIC, 1) AS patient_satisfaction,
       ROUND(staff_morale::NUMERIC, 1)         AS staff_morale,
       ROUND((patient_satisfaction - staff_morale)::NUMERIC, 1) AS gap
FROM bed_metrics
ORDER BY ABS(patient_satisfaction - staff_morale) DESC
LIMIT 20;
