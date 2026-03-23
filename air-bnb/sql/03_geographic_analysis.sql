-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/03_geographic_analysis.sql
-- PURPOSE  : Analyse listing distribution and pricing across NYC boroughs
--            and ZIP codes
-- DATABASE : airbnb_nyc
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. How many listings and what is the average price per borough?
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood                               AS borough,
    COUNT(*)                                    AS total_listings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(price), 2)                        AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                        AS median_price,
    COUNT(DISTINCT host_id)                     AS unique_hosts
FROM listings
GROUP BY neighbourhood
ORDER BY total_listings DESC;


-- -----------------------------------------------------------------------------
-- Q2. How many unique hosts operate in each borough?
--     (hosts with listings in multiple boroughs)
-- -----------------------------------------------------------------------------
SELECT
    host_id,
    COUNT(DISTINCT neighbourhood)               AS boroughs_active_in,
    COUNT(*)                                    AS total_listings,
    ROUND(AVG(price), 2)                        AS avg_price
FROM listings
GROUP BY host_id
HAVING COUNT(DISTINCT neighbourhood) > 1
ORDER BY boroughs_active_in DESC, total_listings DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Q3. Top 15 ZIP codes by listing count with median price
-- -----------------------------------------------------------------------------
SELECT
    zipcode,
    neighbourhood                               AS borough,
    COUNT(*)                                    AS total_listings,
    ROUND(AVG(price), 2)                        AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                        AS median_price
FROM listings
WHERE zipcode IS NOT NULL
GROUP BY zipcode, neighbourhood
ORDER BY total_listings DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q4. Most expensive ZIP codes (min 20 listings)
-- -----------------------------------------------------------------------------
SELECT
    zipcode,
    neighbourhood                               AS borough,
    COUNT(*)                                    AS total_listings,
    ROUND(AVG(price), 2)                        AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                        AS median_price
FROM listings
WHERE zipcode IS NOT NULL
GROUP BY zipcode, neighbourhood
HAVING COUNT(*) >= 20
ORDER BY median_price DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q5. Borough-level supply vs demand proxy
--     (listings per host as a measure of commercialisation)
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood                               AS borough,
    COUNT(*)                                    AS total_listings,
    COUNT(DISTINCT host_id)                     AS unique_hosts,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT host_id), 2) AS listings_per_host,
    ROUND(AVG(number_of_reviews), 1)            AS avg_reviews,
    ROUND(AVG(price), 2)                        AS avg_price
FROM listings
GROUP BY neighbourhood
ORDER BY listings_per_host DESC;


-- -----------------------------------------------------------------------------
-- Q6. Price ranking of boroughs using window function
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood                               AS borough,
    ROUND(AVG(price), 2)                        AS avg_price,
    RANK() OVER (ORDER BY AVG(price) DESC)      AS price_rank,
    ROUND(AVG(price) - AVG(AVG(price)) OVER (), 2) AS diff_from_city_avg
FROM listings
GROUP BY neighbourhood
ORDER BY price_rank;
