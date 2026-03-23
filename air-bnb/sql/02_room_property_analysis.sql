-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/02_room_property_analysis.sql
-- PURPOSE  : Analyse room types and property types — listing counts,
--            pricing, and composition across boroughs
-- DATABASE : airbnb_nyc
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. How many listings exist per room type?
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(*)                                    AS total_listings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(price), 2)                        AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY price)                        AS median_price
FROM listings
GROUP BY room_type
ORDER BY total_listings DESC;


-- -----------------------------------------------------------------------------
-- Q2. What are the top 10 most common property types?
-- -----------------------------------------------------------------------------
SELECT
    property_type,
    COUNT(*)                                    AS total_listings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(price), 2)                        AS avg_price
FROM listings
GROUP BY property_type
ORDER BY total_listings DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Q3. Room type composition per borough
--     (how many entire homes vs private rooms vs shared rooms per borough?)
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    room_type,
    COUNT(*)                                    AS listings,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (PARTITION BY neighbourhood), 1) AS pct_within_borough
FROM listings
GROUP BY neighbourhood, room_type
ORDER BY neighbourhood, listings DESC;


-- -----------------------------------------------------------------------------
-- Q4. Average beds per room type
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    ROUND(AVG(beds), 2)                         AS avg_beds,
    MIN(beds)                                   AS min_beds,
    MAX(beds)                                   AS max_beds,
    COUNT(*)                                    AS listings
FROM listings
GROUP BY room_type
ORDER BY avg_beds DESC;


-- -----------------------------------------------------------------------------
-- Q5. Property type × room type cross-tab (top 5 property types)
-- -----------------------------------------------------------------------------
SELECT
    property_type,
    room_type,
    COUNT(*)                                    AS listings,
    ROUND(AVG(price), 2)                        AS avg_price
FROM listings
WHERE property_type IN (
    SELECT property_type
    FROM listings
    GROUP BY property_type
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
GROUP BY property_type, room_type
ORDER BY property_type, listings DESC;


-- -----------------------------------------------------------------------------
-- Q6. Which room type has the best review scores on average?
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(*)                                    AS listings_with_reviews,
    ROUND(AVG(review_score_rating), 2)          AS avg_review_score,
    ROUND(AVG(number_of_reviews), 1)            AS avg_num_reviews
FROM listings
WHERE review_score_rating IS NOT NULL
GROUP BY room_type
ORDER BY avg_review_score DESC;
