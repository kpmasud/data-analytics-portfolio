-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/04_actor_analysis.sql
-- PURPOSE  : Analyse actors — gender split, prolific performers, age
--            demographics, and cast size patterns
-- DATABASE : movie_data
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Actor gender distribution
-- -----------------------------------------------------------------------------
SELECT
    CASE gender WHEN 'M' THEN 'Male' WHEN 'F' THEN 'Female' ELSE 'Unknown' END AS gender,
    COUNT(*)                                            AS actor_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM actors
GROUP BY gender;


-- -----------------------------------------------------------------------------
-- Q2. Most prolific actors — top 15 by movie appearances
-- -----------------------------------------------------------------------------
SELECT
    a.first_name || ' ' || a.last_name                 AS actor,
    CASE a.gender WHEN 'M' THEN 'Male' ELSE 'Female'   END AS gender,
    DATE_PART('year', AGE(CURRENT_DATE, a.date_of_birth))::INTEGER AS age,
    COUNT(ma.movie_id)                                 AS movies_appeared_in
FROM actors a
JOIN movies_actors ma ON a.actor_id = ma.actor_id
GROUP BY a.actor_id, a.first_name, a.last_name, a.gender, a.date_of_birth
ORDER BY movies_appeared_in DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q3. Actor age distribution (decade buckets)
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN age < 30             THEN 'Under 30'
        WHEN age BETWEEN 30 AND 39 THEN '30s'
        WHEN age BETWEEN 40 AND 49 THEN '40s'
        WHEN age BETWEEN 50 AND 59 THEN '50s'
        WHEN age BETWEEN 60 AND 69 THEN '60s'
        WHEN age BETWEEN 70 AND 79 THEN '70s'
        ELSE '80+'
    END AS age_group,
    COUNT(*) AS actor_count
FROM (
    SELECT DATE_PART('year', AGE(CURRENT_DATE, date_of_birth))::INTEGER AS age
    FROM actors
    WHERE date_of_birth IS NOT NULL
) ages
GROUP BY age_group
ORDER BY MIN(age);


-- -----------------------------------------------------------------------------
-- Q4. Cast size per movie
-- -----------------------------------------------------------------------------
SELECT
    m.movie_name,
    m.movie_lang,
    m.age_certificate,
    COUNT(ma.actor_id) AS cast_size
FROM movies m
JOIN movies_actors ma ON m.movie_id = ma.movie_id
GROUP BY m.movie_id, m.movie_name, m.movie_lang, m.age_certificate
ORDER BY cast_size DESC;


-- -----------------------------------------------------------------------------
-- Q5. Average cast size by language and age certificate
-- -----------------------------------------------------------------------------
SELECT
    m.movie_lang,
    m.age_certificate,
    COUNT(DISTINCT m.movie_id)          AS movies,
    ROUND(AVG(cast_counts.cast_size), 1) AS avg_cast_size
FROM movies m
JOIN (
    SELECT movie_id, COUNT(actor_id) AS cast_size
    FROM movies_actors
    GROUP BY movie_id
) cast_counts ON m.movie_id = cast_counts.movie_id
GROUP BY m.movie_lang, m.age_certificate
ORDER BY avg_cast_size DESC;


-- -----------------------------------------------------------------------------
-- Q6. Gender representation by movie language
--     (male vs female actor count per language)
-- -----------------------------------------------------------------------------
SELECT
    m.movie_lang,
    SUM(CASE WHEN a.gender = 'M' THEN 1 ELSE 0 END) AS male_actors,
    SUM(CASE WHEN a.gender = 'F' THEN 1 ELSE 0 END) AS female_actors,
    COUNT(*)                                         AS total_appearances,
    ROUND(SUM(CASE WHEN a.gender = 'F' THEN 1 ELSE 0 END) * 100.0
          / NULLIF(COUNT(*), 0), 1)                  AS pct_female
FROM movies m
JOIN movies_actors ma ON m.movie_id = ma.movie_id
JOIN actors a         ON ma.actor_id = a.actor_id
WHERE a.gender IS NOT NULL
GROUP BY m.movie_lang
ORDER BY pct_female DESC;
