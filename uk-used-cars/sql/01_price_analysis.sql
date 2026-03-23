-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/01_price_analysis.sql
-- PURPOSE  : Analyse asking prices across brands, fuel types, transmissions,
--            and price brackets
-- DATABASE : cars_uk
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. What is the median and average asking price per brand?
-- -----------------------------------------------------------------------------
SELECT
    brand,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    MIN(price)                                      AS min_price,
    MAX(price)                                      AS max_price
FROM cars
GROUP BY brand
ORDER BY median_price DESC;


-- -----------------------------------------------------------------------------
-- Q2. Price distribution by fuel type
-- -----------------------------------------------------------------------------
SELECT
    fuel_type,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    MIN(price)                                      AS min_price,
    MAX(price)                                      AS max_price
FROM cars
GROUP BY fuel_type
ORDER BY median_price DESC;


-- -----------------------------------------------------------------------------
-- Q3. Price distribution by transmission type
-- -----------------------------------------------------------------------------
SELECT
    transmission,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price
FROM cars
GROUP BY transmission
ORDER BY median_price DESC;


-- -----------------------------------------------------------------------------
-- Q4. Price bracket breakdown — how are listings spread?
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN price < 5000                  THEN 'Under £5k'
        WHEN price BETWEEN 5000 AND 9999   THEN '£5k – £10k'
        WHEN price BETWEEN 10000 AND 14999 THEN '£10k – £15k'
        WHEN price BETWEEN 15000 AND 19999 THEN '£15k – £20k'
        WHEN price BETWEEN 20000 AND 29999 THEN '£20k – £30k'
        ELSE '£30k+'
    END                                             AS price_bracket,
    COUNT(*)                                        AS listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (), 1)                   AS pct_of_total
FROM cars
GROUP BY price_bracket
ORDER BY MIN(price);


-- -----------------------------------------------------------------------------
-- Q5. Top 10 most expensive models (min 50 listings)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price
FROM cars
GROUP BY brand, model
HAVING COUNT(*) >= 50
ORDER BY median_price DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q6. Brand × Transmission — median price heatmap data
-- -----------------------------------------------------------------------------
SELECT
    brand,
    transmission,
    COUNT(*)                                        AS listings,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price
FROM cars
GROUP BY brand, transmission
ORDER BY brand, transmission;
