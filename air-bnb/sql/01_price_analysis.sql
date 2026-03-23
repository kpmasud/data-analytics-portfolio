-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/01_price_analysis.sql
-- PURPOSE  : Analyse nightly pricing across neighbourhoods, room types,
--            property types, and number of beds
-- DATABASE : airbnb_nyc
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. What is the median and average nightly price per borough?
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    COUNT(*)                          AS total_listings,
    ROUND(AVG(price), 2)              AS avg_price,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY price) AS median_price,
    MIN(price)                        AS min_price,
    MAX(price)                        AS max_price
FROM listings
GROUP BY neighbourhood
ORDER BY median_price DESC;


-- -----------------------------------------------------------------------------
-- Q2. What is the median price broken down by room type?
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(*)                          AS total_listings,
    ROUND(AVG(price), 2)              AS avg_price,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY price) AS median_price
FROM listings
GROUP BY room_type
ORDER BY median_price DESC;


-- -----------------------------------------------------------------------------
-- Q3. How does the number of beds affect the nightly price?
--     (limit to 1–6 beds where sample size is meaningful)
-- -----------------------------------------------------------------------------
SELECT
    beds,
    COUNT(*)                          AS total_listings,
    ROUND(AVG(price), 2)              AS avg_price,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY price) AS median_price
FROM listings
WHERE beds BETWEEN 1 AND 6
GROUP BY beds
ORDER BY beds;


-- -----------------------------------------------------------------------------
-- Q4. Which property types command the highest median price? (top 10)
-- -----------------------------------------------------------------------------
SELECT
    property_type,
    COUNT(*)                          AS total_listings,
    ROUND(AVG(price), 2)              AS avg_price,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY price) AS median_price
FROM listings
GROUP BY property_type
HAVING COUNT(*) >= 10
ORDER BY median_price DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q5. Price distribution bucket breakdown — how are listings spread?
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN price < 50              THEN 'Under $50'
        WHEN price BETWEEN 50 AND 99 THEN '$50 – $99'
        WHEN price BETWEEN 100 AND 149 THEN '$100 – $149'
        WHEN price BETWEEN 150 AND 199 THEN '$150 – $199'
        WHEN price BETWEEN 200 AND 299 THEN '$200 – $299'
        ELSE '$300+'
    END                              AS price_bucket,
    COUNT(*)                         AS listings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM listings
GROUP BY price_bucket
ORDER BY MIN(price);


-- -----------------------------------------------------------------------------
-- Q6. Neighbourhood × Room Type — median price heatmap data
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    room_type,
    COUNT(*)                          AS listings,
    ROUND(AVG(price), 2)              AS avg_price,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY price) AS median_price
FROM listings
GROUP BY neighbourhood, room_type
ORDER BY neighbourhood, median_price DESC;
