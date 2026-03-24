-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/02_movie_catalog_analysis.sql
-- PURPOSE  : Analyse the movie catalogue — language distribution, age
--            certificates, movie lengths, and release decade trends
-- DATABASE : movie_data
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Movie count and percentage by language
-- -----------------------------------------------------------------------------
SELECT
    movie_lang,
    COUNT(*)                                            AS movie_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM movies
GROUP BY movie_lang
ORDER BY movie_count DESC;


-- -----------------------------------------------------------------------------
-- Q2. Age certificate breakdown — count, avg length, avg cast size
-- -----------------------------------------------------------------------------
SELECT
    m.age_certificate,
    COUNT(DISTINCT m.movie_id)                          AS movie_count,
    ROUND(AVG(m.movie_length), 1)                       AS avg_length_mins,
    ROUND(AVG(cast_counts.cast_size), 1)                AS avg_cast_size
FROM movies m
LEFT JOIN (
    SELECT movie_id, COUNT(actor_id) AS cast_size
    FROM movies_actors
    GROUP BY movie_id
) cast_counts ON m.movie_id = cast_counts.movie_id
GROUP BY m.age_certificate
ORDER BY movie_count DESC;


-- -----------------------------------------------------------------------------
-- Q3. Movie length statistics by language
-- -----------------------------------------------------------------------------
SELECT
    movie_lang,
    COUNT(*)                                            AS movies,
    ROUND(AVG(movie_length), 1)                         AS avg_length_mins,
    MIN(movie_length)                                   AS min_length_mins,
    MAX(movie_length)                                   AS max_length_mins,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY movie_length)            AS median_length_mins
FROM movies
WHERE movie_length IS NOT NULL
GROUP BY movie_lang
ORDER BY avg_length_mins DESC;


-- -----------------------------------------------------------------------------
-- Q4. Movies released by decade
-- -----------------------------------------------------------------------------
SELECT
    (EXTRACT(YEAR FROM release_date) / 10 * 10)::INTEGER AS decade,
    COUNT(*)                                             AS movie_count,
    ROUND(AVG(movie_length), 1)                          AS avg_length_mins
FROM movies
WHERE release_date IS NOT NULL
GROUP BY decade
ORDER BY decade;


-- -----------------------------------------------------------------------------
-- Q5. Age certificate vs average movie length (matrix / heatmap data)
-- -----------------------------------------------------------------------------
SELECT
    age_certificate,
    movie_lang,
    COUNT(*)                        AS movies,
    ROUND(AVG(movie_length), 1)     AS avg_length_mins
FROM movies
WHERE movie_length IS NOT NULL
GROUP BY age_certificate, movie_lang
ORDER BY age_certificate, avg_length_mins DESC;


-- -----------------------------------------------------------------------------
-- Q6. Movies per year — release trend by language
--     (useful for spotting which era each language dominated)
-- -----------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM release_date)::INTEGER    AS release_year,
    movie_lang,
    COUNT(*)                                    AS movie_count
FROM movies
WHERE release_date IS NOT NULL
GROUP BY release_year, movie_lang
ORDER BY release_year, movie_count DESC;
