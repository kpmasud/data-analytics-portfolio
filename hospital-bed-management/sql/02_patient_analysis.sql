-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/02_patient_analysis.sql
-- PURPOSE  : Patient demographics, length of stay, satisfaction
-- =============================================================================

-- Q1: Age group distribution of patients
SELECT
    CASE
        WHEN age < 18  THEN 'Under 18'
        WHEN age < 35  THEN '18 – 34'
        WHEN age < 50  THEN '35 – 49'
        WHEN age < 65  THEN '50 – 64'
        ELSE '65+'
    END                   AS age_group,
    COUNT(*)              AS patient_count,
    ROUND(AVG(satisfaction)::NUMERIC, 1) AS avg_satisfaction
FROM patients
GROUP BY age_group
ORDER BY MIN(age);


-- Q2: Average length of stay by service
SELECT service,
       COUNT(*)                                         AS patients,
       ROUND(AVG(length_of_stay)::NUMERIC, 1)          AS avg_los_days,
       PERCENTILE_CONT(0.5) WITHIN GROUP
           (ORDER BY length_of_stay)                   AS median_los_days,
       MAX(length_of_stay)                             AS max_los_days
FROM patients
GROUP BY service
ORDER BY avg_los_days DESC;


-- Q3: Patient satisfaction by service
SELECT service,
       COUNT(*)                                         AS patients,
       ROUND(AVG(satisfaction)::NUMERIC, 1)            AS avg_satisfaction,
       PERCENTILE_CONT(0.5) WITHIN GROUP
           (ORDER BY satisfaction)                     AS median_satisfaction,
       MIN(satisfaction)                               AS min_satisfaction,
       MAX(satisfaction)                               AS max_satisfaction
FROM patients
GROUP BY service
ORDER BY avg_satisfaction DESC;


-- Q4: Monthly admissions volume (by arrival month)
SELECT EXTRACT(MONTH FROM arrival_date)::INT AS month,
       COUNT(*)                               AS admissions,
       ROUND(AVG(length_of_stay)::NUMERIC, 1) AS avg_los,
       ROUND(AVG(satisfaction)::NUMERIC, 1)   AS avg_satisfaction
FROM patients
GROUP BY month
ORDER BY month;


-- Q5: Age group vs service — where each age group goes
SELECT
    CASE
        WHEN age < 18  THEN 'Under 18'
        WHEN age < 35  THEN '18 – 34'
        WHEN age < 50  THEN '35 – 49'
        WHEN age < 65  THEN '50 – 64'
        ELSE '65+'
    END      AS age_group,
    service,
    COUNT(*) AS patients
FROM patients
GROUP BY age_group, service
ORDER BY MIN(age), service;


-- Q6: Long stay vs short stay patients — satisfaction gap
SELECT
    CASE
        WHEN length_of_stay <= 3  THEN 'Short (1–3 days)'
        WHEN length_of_stay <= 7  THEN 'Medium (4–7 days)'
        WHEN length_of_stay <= 11 THEN 'Long (8–11 days)'
        ELSE 'Extended (12+ days)'
    END                                             AS stay_band,
    COUNT(*)                                        AS patients,
    ROUND(AVG(satisfaction)::NUMERIC, 1)            AS avg_satisfaction,
    ROUND(AVG(length_of_stay)::NUMERIC, 1)          AS avg_los
FROM patients
GROUP BY stay_band
ORDER BY MIN(length_of_stay);
