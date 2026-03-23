-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/04_depreciation_mileage_analysis.sql
-- PURPOSE  : Analyse how price drops with age and mileage — depreciation curve,
--            mileage bands, and engine size vs price
-- DATABASE : cars_uk
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Median price by year — the depreciation curve
-- -----------------------------------------------------------------------------
SELECT
    year,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price
FROM cars
GROUP BY year
ORDER BY year DESC;


-- -----------------------------------------------------------------------------
-- Q2. Median price by mileage band
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN mileage < 10000              THEN 'Under 10k'
        WHEN mileage BETWEEN 10000 AND 24999 THEN '10k – 25k'
        WHEN mileage BETWEEN 25000 AND 49999 THEN '25k – 50k'
        WHEN mileage BETWEEN 50000 AND 74999 THEN '50k – 75k'
        ELSE '75k – 90k'
    END                                             AS mileage_band,
    COUNT(*)                                        AS listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price
FROM cars
GROUP BY mileage_band
ORDER BY MIN(mileage);


-- -----------------------------------------------------------------------------
-- Q3. Average mileage by brand
-- -----------------------------------------------------------------------------
SELECT
    brand,
    COUNT(*)                                        AS listings,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY mileage)                          AS median_mileage
FROM cars
GROUP BY brand
ORDER BY avg_mileage ASC;


-- -----------------------------------------------------------------------------
-- Q4. Price drop per year of age (depreciation rate vs newest stock)
-- -----------------------------------------------------------------------------
WITH yearly AS (
    SELECT
        year,
        PERCENTILE_CONT(0.5) WITHIN GROUP
            (ORDER BY price)                        AS median_price,
        COUNT(*)                                    AS listings
    FROM cars
    GROUP BY year
),
newest AS (
    SELECT median_price AS base_price
    FROM yearly
    WHERE year = (SELECT MAX(year) FROM yearly)
)
SELECT
    y.year,
    y.listings,
    ROUND(y.median_price::NUMERIC, 0)               AS median_price,
    ROUND((n.base_price - y.median_price)::NUMERIC, 0)  AS price_drop_vs_newest,
    ROUND(
        (n.base_price - y.median_price) * 100.0 /
        NULLIF(n.base_price, 0), 1
    )                                               AS pct_depreciation
FROM yearly y
CROSS JOIN newest n
ORDER BY y.year DESC;


-- -----------------------------------------------------------------------------
-- Q5. Engine size bands vs median price
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN engine_size < 1.0            THEN 'Under 1.0L'
        WHEN engine_size BETWEEN 1.0 AND 1.4 THEN '1.0L – 1.4L'
        WHEN engine_size BETWEEN 1.5 AND 1.9 THEN '1.5L – 1.9L'
        WHEN engine_size BETWEEN 2.0 AND 2.9 THEN '2.0L – 2.9L'
        ELSE '3.0L+'
    END                                             AS engine_band,
    COUNT(*)                                        AS listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    ROUND(AVG(mpg)::NUMERIC, 2)                     AS avg_mpg
FROM cars
GROUP BY engine_band
ORDER BY MIN(engine_size);


-- -----------------------------------------------------------------------------
-- Q6. High mileage vs low mileage price gap per brand
-- -----------------------------------------------------------------------------
SELECT
    brand,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price) FILTER (WHERE mileage < 25000) AS median_price_low_mileage,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price) FILTER (WHERE mileage >= 60000) AS median_price_high_mileage,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price) FILTER (WHERE mileage < 25000) -
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price) FILTER (WHERE mileage >= 60000) AS price_gap
FROM cars
GROUP BY brand
ORDER BY price_gap DESC;
