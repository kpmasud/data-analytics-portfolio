-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/04_host_review_analysis.sql
-- PURPOSE  : Analyse host activity, tenure, and guest review patterns
-- DATABASE : airbnb_nyc
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. How many new hosts joined each year?
-- -----------------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM host_since)               AS join_year,
    COUNT(DISTINCT host_id)                     AS new_hosts
FROM listings
WHERE host_since IS NOT NULL
GROUP BY join_year
ORDER BY join_year;


-- -----------------------------------------------------------------------------
-- Q2. Host segmentation — how many listings does each host manage?
--     (single-listing vs multi-listing hosts)
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN listing_count = 1 THEN 'Single listing'
        WHEN listing_count BETWEEN 2 AND 5 THEN '2–5 listings'
        WHEN listing_count BETWEEN 6 AND 10 THEN '6–10 listings'
        ELSE '11+ listings'
    END                                         AS host_segment,
    COUNT(*)                                    AS host_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_hosts
FROM (
    SELECT host_id, COUNT(*) AS listing_count
    FROM listings
    GROUP BY host_id
) host_counts
GROUP BY host_segment
ORDER BY MIN(listing_count);


-- -----------------------------------------------------------------------------
-- Q3. Review score distribution — how are scores clustered?
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN review_score_rating < 60  THEN 'Below 60'
        WHEN review_score_rating BETWEEN 60 AND 69 THEN '60–69'
        WHEN review_score_rating BETWEEN 70 AND 79 THEN '70–79'
        WHEN review_score_rating BETWEEN 80 AND 89 THEN '80–89'
        WHEN review_score_rating BETWEEN 90 AND 94 THEN '90–94'
        ELSE '95–100'
    END                                         AS score_band,
    COUNT(*)                                    AS listings,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM listings
WHERE review_score_rating IS NOT NULL
GROUP BY score_band
ORDER BY MIN(review_score_rating);


-- -----------------------------------------------------------------------------
-- Q4. Average review score by borough
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood                               AS borough,
    COUNT(*)                                    AS total_listings,
    COUNT(review_score_rating)                  AS listings_with_score,
    ROUND(AVG(review_score_rating), 2)          AS avg_review_score,
    ROUND(AVG(number_of_reviews), 1)            AS avg_num_reviews
FROM listings
GROUP BY neighbourhood
ORDER BY avg_review_score DESC;


-- -----------------------------------------------------------------------------
-- Q5. Do hosts with more listings get higher or lower review scores?
--     (host portfolio size vs avg rating)
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN listing_count = 1  THEN '1 listing'
        WHEN listing_count BETWEEN 2 AND 5 THEN '2–5 listings'
        WHEN listing_count BETWEEN 6 AND 10 THEN '6–10 listings'
        ELSE '11+ listings'
    END                                         AS host_segment,
    COUNT(*)                                    AS listings,
    ROUND(AVG(review_score_rating), 2)          AS avg_review_score,
    ROUND(AVG(number_of_reviews), 1)            AS avg_num_reviews,
    ROUND(AVG(price), 2)                        AS avg_price
FROM listings l
JOIN (
    SELECT host_id, COUNT(*) AS listing_count
    FROM listings
    GROUP BY host_id
) hc ON l.host_id = hc.host_id
WHERE review_score_rating IS NOT NULL
GROUP BY host_segment
ORDER BY MIN(hc.listing_count);


-- -----------------------------------------------------------------------------
-- Q6. Top 10 most reviewed listings — who are the high-volume hosts?
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    listing_name,
    neighbourhood                               AS borough,
    room_type,
    price,
    number_of_reviews,
    review_score_rating,
    host_id
FROM listings
ORDER BY number_of_reviews DESC
LIMIT 10;
