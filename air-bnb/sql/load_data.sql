-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/load_data.sql
-- PURPOSE  : Load clean CSV into the listings table using \copy
-- DATABASE : airbnb_nyc (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d airbnb_nyc -f sql/load_data.sql
-- NOTE     : Run sql/schema.sql first to create the table
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Truncate table before loading (safe to re-run)
-- -----------------------------------------------------------------------------
TRUNCATE TABLE listings RESTART IDENTITY;


-- -----------------------------------------------------------------------------
-- Load data from clean CSV
-- \copy is a psql client-side command — no server file permission required
-- -----------------------------------------------------------------------------
\copy listings (host_id, host_since, listing_name, neighbourhood, property_type, room_type, zipcode, beds, number_of_records, number_of_reviews, price, review_score_bin, review_score_rating) FROM 'data/airbnb_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');


-- -----------------------------------------------------------------------------
-- Verify row count after load
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*)                    AS total_rows,
    COUNT(DISTINCT host_id)     AS unique_hosts,
    COUNT(DISTINCT neighbourhood) AS boroughs,
    MIN(price)                  AS min_price,
    MAX(price)                  AS max_price,
    ROUND(AVG(price), 2)        AS avg_price
FROM listings;
