-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/03_director_analysis.sql
-- PURPOSE  : Analyse directors — nationality distribution, productivity,
--            revenue performance, and language breadth
-- DATABASE : movie_data
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Director nationality distribution
-- -----------------------------------------------------------------------------
SELECT
    nationality,
    COUNT(*)                                            AS director_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM directors
WHERE nationality IS NOT NULL
GROUP BY nationality
ORDER BY director_count DESC;


-- -----------------------------------------------------------------------------
-- Q2. Most prolific directors by number of movies in the dataset
-- -----------------------------------------------------------------------------
SELECT
    d.first_name || ' ' || d.last_name                 AS director,
    d.nationality,
    COUNT(m.movie_id)                                   AS movies_directed,
    STRING_AGG(m.movie_name, ', ' ORDER BY m.release_date) AS movie_list
FROM directors d
JOIN movies m ON d.director_id = m.director_id
GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
HAVING COUNT(m.movie_id) > 1
ORDER BY movies_directed DESC;


-- -----------------------------------------------------------------------------
-- Q3. Director revenue performance
--     (average total box-office per director, only where data exists)
-- -----------------------------------------------------------------------------
SELECT
    d.first_name || ' ' || d.last_name                 AS director,
    d.nationality,
    COUNT(DISTINCT m.movie_id)                          AS movies,
    ROUND(SUM(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS total_revenue_m,
    ROUND(AVG(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS avg_revenue_per_movie_m
FROM directors d
JOIN movies m          ON d.director_id = m.director_id
JOIN movie_revenues mr ON m.movie_id    = mr.movie_id
GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
ORDER BY total_revenue_m DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q4. Director age distribution (age at time of analysis)
-- -----------------------------------------------------------------------------
SELECT
    d.first_name || ' ' || d.last_name                 AS director,
    d.nationality,
    d.date_of_birth,
    DATE_PART('year', AGE(CURRENT_DATE, d.date_of_birth))::INTEGER AS age_years
FROM directors d
WHERE d.date_of_birth IS NOT NULL
ORDER BY age_years;


-- -----------------------------------------------------------------------------
-- Q5. English-language vs non-English directors — movie and revenue comparison
-- -----------------------------------------------------------------------------
SELECT
    CASE WHEN m.movie_lang = 'English' THEN 'English' ELSE 'Non-English' END AS lang_group,
    COUNT(DISTINCT d.director_id)   AS directors,
    COUNT(DISTINCT m.movie_id)      AS movies,
    ROUND(AVG(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                           AS avg_total_revenue_m
FROM directors d
JOIN movies m          ON d.director_id = m.director_id
LEFT JOIN movie_revenues mr ON m.movie_id = mr.movie_id
GROUP BY lang_group;


-- -----------------------------------------------------------------------------
-- Q6. Director career span — years between first and last film in the dataset
-- -----------------------------------------------------------------------------
SELECT
    d.first_name || ' ' || d.last_name         AS director,
    d.nationality,
    MIN(EXTRACT(YEAR FROM m.release_date))::INTEGER AS first_film_year,
    MAX(EXTRACT(YEAR FROM m.release_date))::INTEGER AS last_film_year,
    (MAX(EXTRACT(YEAR FROM m.release_date))
        - MIN(EXTRACT(YEAR FROM m.release_date)))::INTEGER AS career_span_years,
    COUNT(m.movie_id)                           AS films_in_dataset
FROM directors d
JOIN movies m ON d.director_id = m.director_id
WHERE m.release_date IS NOT NULL
GROUP BY d.director_id, d.first_name, d.last_name, d.nationality
ORDER BY career_span_years DESC;
