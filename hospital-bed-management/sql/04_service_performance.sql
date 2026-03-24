-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/04_service_performance.sql
-- PURPOSE  : Cross-service KPIs, event impact, demand & satisfaction trends
-- =============================================================================

-- Q1: Overall KPI summary per service
SELECT service,
       ROUND(AVG(admission_rate)::NUMERIC, 1)        AS avg_admission_rate,
       ROUND(AVG(patient_satisfaction)::NUMERIC, 1)  AS avg_patient_satisfaction,
       ROUND(AVG(staff_morale)::NUMERIC, 1)          AS avg_staff_morale,
       SUM(patients_admitted)                        AS total_admitted,
       SUM(patients_refused)                         AS total_refused
FROM bed_metrics
GROUP BY service
ORDER BY avg_admission_rate DESC;


-- Q2: Event impact on all KPIs
SELECT event,
       COUNT(*)                                        AS occurrences,
       ROUND(AVG(admission_rate)::NUMERIC, 1)         AS avg_admission_rate,
       ROUND(AVG(patient_satisfaction)::NUMERIC, 1)   AS avg_satisfaction,
       ROUND(AVG(staff_morale)::NUMERIC, 1)           AS avg_morale,
       ROUND(AVG(patients_refused)::NUMERIC, 1)       AS avg_refused
FROM bed_metrics
GROUP BY event
ORDER BY avg_morale ASC;


-- Q3: Month-over-month demand growth
WITH monthly AS (
    SELECT month,
           SUM(patients_request)  AS total_requested,
           SUM(patients_admitted) AS total_admitted
    FROM bed_metrics
    GROUP BY month
)
SELECT month,
       total_requested,
       total_admitted,
       LAG(total_requested) OVER (ORDER BY month)  AS prev_month_requested,
       ROUND(
           (total_requested - LAG(total_requested) OVER (ORDER BY month)) * 100.0 /
           NULLIF(LAG(total_requested) OVER (ORDER BY month), 0), 1
       )                                           AS demand_growth_pct
FROM monthly
ORDER BY month;


-- Q4: Service with highest satisfaction during high-pressure weeks
--     (weeks where refusals exceed the annual average)
WITH avg_refused AS (
    SELECT AVG(patients_refused) AS threshold FROM bed_metrics
)
SELECT bm.service,
       COUNT(*)                                        AS high_pressure_weeks,
       ROUND(AVG(bm.patient_satisfaction)::NUMERIC, 1) AS avg_satisfaction,
       ROUND(AVG(bm.staff_morale)::NUMERIC, 1)        AS avg_morale
FROM bed_metrics bm, avg_refused ar
WHERE bm.patients_refused > ar.threshold
GROUP BY bm.service
ORDER BY avg_satisfaction DESC;


-- Q5: Correlation proxy — staff morale vs patient satisfaction by service
SELECT service,
       ROUND(AVG(staff_morale)::NUMERIC, 1)          AS avg_morale,
       ROUND(AVG(patient_satisfaction)::NUMERIC, 1)  AS avg_satisfaction,
       ROUND(AVG(admission_rate)::NUMERIC, 1)        AS avg_admission_rate
FROM bed_metrics
GROUP BY service
ORDER BY avg_morale DESC;


-- Q6: Best and worst performing weeks — composite score
SELECT week,
       ROUND(AVG(admission_rate)::NUMERIC, 1)       AS avg_admission_rate,
       ROUND(AVG(patient_satisfaction)::NUMERIC, 1) AS avg_satisfaction,
       ROUND(AVG(staff_morale)::NUMERIC, 1)         AS avg_morale,
       ROUND((AVG(admission_rate) + AVG(patient_satisfaction) +
              AVG(staff_morale)) / 3.0, 1)          AS composite_score
FROM bed_metrics
GROUP BY week
ORDER BY composite_score DESC;
