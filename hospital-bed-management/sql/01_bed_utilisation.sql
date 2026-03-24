-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/01_bed_utilisation.sql
-- PURPOSE  : Bed capacity, admission rates, refusal analysis
-- =============================================================================

-- Q1: Average admission rate by service
SELECT service,
       ROUND(AVG(admission_rate)::NUMERIC, 1)   AS avg_admission_rate,
       ROUND(AVG(patients_refused)::NUMERIC, 1) AS avg_refused,
       SUM(patients_admitted)                   AS total_admitted,
       SUM(patients_refused)                    AS total_refused
FROM bed_metrics
GROUP BY service
ORDER BY avg_admission_rate DESC;


-- Q2: Weekly bed occupancy trend (all services combined)
SELECT week,
       SUM(patients_admitted)                                   AS total_admitted,
       SUM(available_beds)                                      AS total_beds,
       ROUND(SUM(patients_admitted) * 100.0 /
           NULLIF(SUM(available_beds), 0), 1)                  AS occupancy_pct
FROM bed_metrics
GROUP BY week
ORDER BY week;


-- Q3: Refusal rate by month (demand exceeding capacity)
SELECT month,
       SUM(patients_request)  AS total_requested,
       SUM(patients_admitted) AS total_admitted,
       SUM(patients_refused)  AS total_refused,
       ROUND(SUM(patients_refused) * 100.0 /
           NULLIF(SUM(patients_request), 0), 1) AS refusal_rate_pct
FROM bed_metrics
GROUP BY month
ORDER BY month;


-- Q4: Impact of events on admission rate
SELECT event,
       COUNT(*)                                        AS weeks_affected,
       ROUND(AVG(admission_rate)::NUMERIC, 1)          AS avg_admission_rate,
       ROUND(AVG(patients_refused)::NUMERIC, 1)        AS avg_refused,
       ROUND(AVG(patient_satisfaction)::NUMERIC, 1)    AS avg_satisfaction
FROM bed_metrics
GROUP BY event
ORDER BY avg_admission_rate DESC;


-- Q5: Most overcrowded service (highest average unmet demand)
SELECT service,
       ROUND(AVG(patients_refused)::NUMERIC, 1)   AS avg_refused_per_week,
       SUM(patients_refused)                       AS total_refused_annual,
       ROUND(AVG(admission_rate)::NUMERIC, 1)      AS avg_admission_rate
FROM bed_metrics
GROUP BY service
ORDER BY avg_refused_per_week DESC;


-- Q6: Bed utilisation heatmap — occupancy % by service and month
SELECT month,
       service,
       ROUND(SUM(patients_admitted) * 100.0 /
           NULLIF(SUM(available_beds), 0), 1) AS occupancy_pct
FROM bed_metrics
GROUP BY month, service
ORDER BY month, service;
