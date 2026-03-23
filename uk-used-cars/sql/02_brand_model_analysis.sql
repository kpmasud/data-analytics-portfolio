-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/02_brand_model_analysis.sql
-- PURPOSE  : Analyse market share, model popularity, and brand characteristics
-- DATABASE : cars_uk
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Listing count and market share per brand
-- -----------------------------------------------------------------------------
SELECT
    brand,
    COUNT(*)                                        AS total_listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (), 2)                   AS market_share_pct,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage
FROM cars
GROUP BY brand
ORDER BY total_listings DESC;


-- -----------------------------------------------------------------------------
-- Q2. Top 10 most listed models across all brands
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage
FROM cars
GROUP BY brand, model
ORDER BY total_listings DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q3. Top 10 most expensive models (min 50 listings)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS total_listings,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage
FROM cars
GROUP BY brand, model
HAVING COUNT(*) >= 50
ORDER BY median_price DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q4. Average mileage per brand
-- -----------------------------------------------------------------------------
SELECT
    brand,
    COUNT(*)                                        AS total_listings,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY mileage)                          AS median_mileage,
    MIN(mileage)                                    AS min_mileage,
    MAX(mileage)                                    AS max_mileage
FROM cars
GROUP BY brand
ORDER BY avg_mileage DESC;


-- -----------------------------------------------------------------------------
-- Q5. Brand × Fuel type cross-tab (listing counts)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    fuel_type,
    COUNT(*)                                        AS listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (PARTITION BY brand), 1) AS pct_within_brand
FROM cars
GROUP BY brand, fuel_type
ORDER BY brand, listings DESC;


-- -----------------------------------------------------------------------------
-- Q6. Year range per brand — newest and oldest stock
-- -----------------------------------------------------------------------------
SELECT
    brand,
    MIN(year)                                       AS oldest_year,
    MAX(year)                                       AS newest_year,
    MAX(year) - MIN(year)                           AS year_span,
    ROUND(AVG(year)::NUMERIC, 1)                    AS avg_year,
    COUNT(*)                                        AS total_listings
FROM cars
GROUP BY brand
ORDER BY avg_year DESC;
