-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/03_fuel_transmission_analysis.sql
-- PURPOSE  : Analyse fuel type trends, transmission mix, MPG, tax, and
--            engine size patterns
-- DATABASE : cars_uk
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Fuel type distribution across the market
-- -----------------------------------------------------------------------------
SELECT
    fuel_type,
    COUNT(*)                                        AS total_listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (), 2)                   AS market_share_pct,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage
FROM cars
GROUP BY fuel_type
ORDER BY total_listings DESC;


-- -----------------------------------------------------------------------------
-- Q2. Transmission type breakdown
-- -----------------------------------------------------------------------------
SELECT
    transmission,
    COUNT(*)                                        AS total_listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (), 2)                   AS market_share_pct,
    ROUND(AVG(price)::NUMERIC, 2)                   AS avg_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage
FROM cars
GROUP BY transmission
ORDER BY total_listings DESC;


-- -----------------------------------------------------------------------------
-- Q3. Average MPG by fuel type (where data available)
-- -----------------------------------------------------------------------------
SELECT
    fuel_type,
    COUNT(*)                                        AS listings_with_mpg,
    ROUND(AVG(mpg)::NUMERIC, 2)                     AS avg_mpg,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY mpg)                              AS median_mpg,
    MIN(mpg)                                        AS min_mpg,
    MAX(mpg)                                        AS max_mpg
FROM cars
WHERE mpg IS NOT NULL AND mpg > 0
GROUP BY fuel_type
ORDER BY avg_mpg DESC;


-- -----------------------------------------------------------------------------
-- Q4. Average annual road tax by fuel type
-- -----------------------------------------------------------------------------
SELECT
    fuel_type,
    COUNT(*)                                        AS listings_with_tax,
    ROUND(AVG(tax)::NUMERIC, 2)                     AS avg_tax,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY tax)                              AS median_tax,
    MIN(tax)                                        AS min_tax,
    MAX(tax)                                        AS max_tax
FROM cars
WHERE tax IS NOT NULL
GROUP BY fuel_type
ORDER BY avg_tax DESC;


-- -----------------------------------------------------------------------------
-- Q5. Fuel type trend by year — how has the mix shifted over time?
-- -----------------------------------------------------------------------------
SELECT
    year,
    fuel_type,
    COUNT(*)                                        AS listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (PARTITION BY year), 1) AS pct_of_year
FROM cars
WHERE year >= 2010
GROUP BY year, fuel_type
ORDER BY year, listings DESC;


-- -----------------------------------------------------------------------------
-- Q6. Engine size distribution by fuel type
-- -----------------------------------------------------------------------------
SELECT
    fuel_type,
    COUNT(*)                                        AS listings,
    ROUND(AVG(engine_size)::NUMERIC, 2)             AS avg_engine_size,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY engine_size)                      AS median_engine_size,
    MIN(engine_size)                                AS min_engine_size,
    MAX(engine_size)                                AS max_engine_size
FROM cars
GROUP BY fuel_type
ORDER BY avg_engine_size DESC;
