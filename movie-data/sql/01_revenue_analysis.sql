-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/01_revenue_analysis.sql
-- PURPOSE  : Analyse box-office revenue — top earners, domestic vs
--            international split, revenue by language and nationality
-- DATABASE : movie_data
-- NOTE     : domestic_takings / international_takings are in millions USD
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Top 10 movies by total box-office revenue (domestic + international)
-- -----------------------------------------------------------------------------
SELECT
    m.movie_name,
    m.movie_lang,
    EXTRACT(YEAR FROM m.release_date)           AS release_year,
    COALESCE(mr.domestic_takings, 0)            AS domestic_m,
    COALESCE(mr.international_takings, 0)       AS international_m,
    COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0) AS total_revenue_m
FROM movies m
JOIN movie_revenues mr ON m.movie_id = mr.movie_id
WHERE mr.domestic_takings IS NOT NULL
   OR mr.international_takings IS NOT NULL
ORDER BY total_revenue_m DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q2. Domestic vs international revenue per movie — side-by-side comparison
--     (only movies that have both values reported)
-- -----------------------------------------------------------------------------
SELECT
    m.movie_name,
    mr.domestic_takings,
    mr.international_takings,
    ROUND(mr.international_takings /
          NULLIF(mr.domestic_takings, 0), 2)    AS intl_to_dom_ratio
FROM movies m
JOIN movie_revenues mr ON m.movie_id = mr.movie_id
WHERE mr.domestic_takings      IS NOT NULL
  AND mr.international_takings IS NOT NULL
ORDER BY (mr.domestic_takings + mr.international_takings) DESC;


-- -----------------------------------------------------------------------------
-- Q3. Revenue data coverage — how many movies have revenue records?
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*)                                        AS total_movies,
    COUNT(mr.revenue_id)                            AS movies_with_revenue,
    COUNT(*) - COUNT(mr.revenue_id)                 AS movies_missing_revenue,
    ROUND(COUNT(mr.revenue_id) * 100.0 / COUNT(*), 1) AS pct_with_revenue
FROM movies m
LEFT JOIN movie_revenues mr ON m.movie_id = mr.movie_id;


-- -----------------------------------------------------------------------------
-- Q4. Average total revenue by movie language
--     (exclude movies with no revenue data)
-- -----------------------------------------------------------------------------
SELECT
    m.movie_lang,
    COUNT(m.movie_id)                                   AS movie_count,
    ROUND(AVG(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS avg_total_revenue_m,
    ROUND(SUM(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS total_revenue_m
FROM movies m
JOIN movie_revenues mr ON m.movie_id = mr.movie_id
GROUP BY m.movie_lang
ORDER BY avg_total_revenue_m DESC;


-- -----------------------------------------------------------------------------
-- Q5. Revenue by director nationality
-- -----------------------------------------------------------------------------
SELECT
    d.nationality,
    COUNT(DISTINCT m.movie_id)                          AS movies,
    ROUND(AVG(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS avg_total_revenue_m,
    ROUND(SUM(
        COALESCE(mr.domestic_takings, 0)
        + COALESCE(mr.international_takings, 0)
    ), 2)                                               AS total_revenue_m
FROM movies m
JOIN directors d       ON m.director_id = d.director_id
JOIN movie_revenues mr ON m.movie_id    = mr.movie_id
GROUP BY d.nationality
ORDER BY total_revenue_m DESC;


-- -----------------------------------------------------------------------------
-- Q6. International dominance — movies where international beat domestic
--     (ranked by the international-minus-domestic gap)
-- -----------------------------------------------------------------------------
SELECT
    m.movie_name,
    m.movie_lang,
    mr.domestic_takings,
    mr.international_takings,
    ROUND(mr.international_takings - mr.domestic_takings, 2)    AS intl_surplus_m,
    ROUND(mr.international_takings / NULLIF(mr.domestic_takings, 0), 2) AS intl_to_dom_ratio
FROM movies m
JOIN movie_revenues mr ON m.movie_id = mr.movie_id
WHERE mr.domestic_takings      IS NOT NULL
  AND mr.international_takings IS NOT NULL
ORDER BY intl_surplus_m DESC;
