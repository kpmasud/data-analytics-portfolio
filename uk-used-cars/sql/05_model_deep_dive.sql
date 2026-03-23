-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/05_model_deep_dive.sql
-- PURPOSE  : Deep-dive into individual car models — top models per brand,
--            model value retention, mileage profile, and model price ranking
-- DATABASE : cars_uk
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Top 3 most listed models per brand (window function RANK)
-- -----------------------------------------------------------------------------
WITH model_counts AS (
    SELECT
        brand,
        model,
        COUNT(*)                                    AS listings,
        ROUND(AVG(price)::NUMERIC, 2)               AS avg_price,
        RANK() OVER (
            PARTITION BY brand ORDER BY COUNT(*) DESC
        )                                           AS rank_within_brand
    FROM cars
    GROUP BY brand, model
)
SELECT brand, model, listings, avg_price, rank_within_brand
FROM model_counts
WHERE rank_within_brand <= 3
ORDER BY brand, rank_within_brand;


-- -----------------------------------------------------------------------------
-- Q2. Models with best value retention — low mileage still affordable
--     (high listing count, moderate mileage, lower price = good value)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS listings,
    ROUND(AVG(price)::NUMERIC, 0)                   AS avg_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage,
    ROUND(AVG(price)::NUMERIC / NULLIF(AVG(mileage), 0), 4) AS price_per_mile
FROM cars
GROUP BY brand, model
HAVING COUNT(*) >= 100
ORDER BY price_per_mile ASC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q3. Most affordable models (median price ≤ £8,000, min 50 listings)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS listings,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    ROUND(AVG(mileage)::NUMERIC, 0)                 AS avg_mileage,
    ROUND(AVG(mpg)::NUMERIC, 1)                     AS avg_mpg
FROM cars
GROUP BY brand, model
HAVING COUNT(*) >= 50
    AND PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) <= 8000
ORDER BY median_price ASC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q4. Model price ranking within each brand (DENSE_RANK)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS listings,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                            AS median_price,
    DENSE_RANK() OVER (
        PARTITION BY brand
        ORDER BY PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) DESC
    )                                               AS price_rank_in_brand
FROM cars
GROUP BY brand, model
HAVING COUNT(*) >= 30
ORDER BY brand, price_rank_in_brand;


-- -----------------------------------------------------------------------------
-- Q5. Model depreciation — price decline from 2019 → 2015 stock
-- -----------------------------------------------------------------------------
WITH new_stock AS (
    SELECT brand, model,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price_2019
    FROM cars WHERE year = 2019
    GROUP BY brand, model
    HAVING COUNT(*) >= 10
),
old_stock AS (
    SELECT brand, model,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price_2015
    FROM cars WHERE year = 2015
    GROUP BY brand, model
    HAVING COUNT(*) >= 10
)
SELECT
    n.brand,
    n.model,
    ROUND(n.median_price_2019::NUMERIC, 0)          AS price_2019_stock,
    ROUND(o.median_price_2015::NUMERIC, 0)          AS price_2015_stock,
    ROUND((n.median_price_2019 - o.median_price_2015)::NUMERIC, 0) AS price_drop,
    ROUND(
        (n.median_price_2019 - o.median_price_2015) * 100.0 /
        NULLIF(n.median_price_2019, 0), 1
    )                                               AS pct_drop
FROM new_stock n
JOIN old_stock o USING (brand, model)
ORDER BY pct_drop DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q6. Model fuel efficiency league table (avg MPG, min 50 listings)
-- -----------------------------------------------------------------------------
SELECT
    brand,
    model,
    COUNT(*)                                        AS listings,
    ROUND(AVG(mpg)::NUMERIC, 1)                     AS avg_mpg,
    ROUND(AVG(engine_size)::NUMERIC, 2)             AS avg_engine_size,
    fuel_type,
    ROUND(AVG(price)::NUMERIC, 0)                   AS avg_price
FROM cars
WHERE mpg IS NOT NULL AND mpg > 0
GROUP BY brand, model, fuel_type
HAVING COUNT(*) >= 50
ORDER BY avg_mpg DESC
LIMIT 15;
