-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/load_data.sql
-- PURPOSE  : Truncate table and bulk-load clean CSV via \copy
-- DATABASE : cars_uk
-- RUN AS   : psql -U postgres -d cars_uk -f sql/load_data.sql
--            (must be run from the project root: uk-used-cars/)
-- =============================================================================

TRUNCATE TABLE cars RESTART IDENTITY;

\copy cars (brand, model, year, price, transmission, mileage, fuel_type, tax, mpg, engine_size) FROM 'data/cars_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

-- Quick verification
SELECT
    COUNT(*)                        AS total_rows,
    COUNT(DISTINCT brand)           AS brands,
    COUNT(DISTINCT model)           AS models,
    MIN(year)                       AS oldest_year,
    MAX(year)                       AS newest_year,
    MIN(price)                      AS min_price,
    MAX(price)                      AS max_price,
    ROUND(AVG(price)::NUMERIC, 2)   AS avg_price
FROM cars;
