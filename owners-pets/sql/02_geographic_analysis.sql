-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/02_geographic_analysis.sql
-- PURPOSE  : Analyse the geographic spread of owners and their pets —
--            by US state and city, and email domain preferences
-- DATABASE : owners_pets
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Owners by state
-- -----------------------------------------------------------------------------
SELECT
    state,
    COUNT(*)                                            AS owner_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_owners
FROM owners_pets
GROUP BY state
ORDER BY owner_count DESC;


-- -----------------------------------------------------------------------------
-- Q2. Pets by state (joined through owner)
-- -----------------------------------------------------------------------------
SELECT
    o.state,
    COUNT(p.id)                                         AS pet_count,
    ROUND(AVG(p.age), 1)                                AS avg_pet_age
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.state
ORDER BY pet_count DESC;


-- -----------------------------------------------------------------------------
-- Q3. Owners and pets by city
-- -----------------------------------------------------------------------------
SELECT
    o.city,
    o.state,
    COUNT(DISTINCT o.id)    AS owners,
    COUNT(p.id)             AS pets,
    ROUND(COUNT(p.id)::NUMERIC / NULLIF(COUNT(DISTINCT o.id), 0), 1) AS avg_pets_per_owner
FROM owners_pets o
LEFT JOIN pets p ON o.id = p.owner_id
GROUP BY o.city, o.state
ORDER BY pets DESC;


-- -----------------------------------------------------------------------------
-- Q4. Email domain distribution
-- -----------------------------------------------------------------------------
SELECT
    SUBSTRING(email FROM POSITION('@' IN email) + 1) AS email_domain,
    COUNT(*)                                          AS owner_count
FROM owners_pets
WHERE email IS NOT NULL
GROUP BY email_domain
ORDER BY owner_count DESC;


-- -----------------------------------------------------------------------------
-- Q5. US region grouping — Northeast / South / Midwest / West
-- -----------------------------------------------------------------------------
SELECT
    CASE TRIM(state)
        WHEN 'NY' THEN 'Northeast'  WHEN 'MA' THEN 'Northeast'
        WHEN 'PA' THEN 'Northeast'  WHEN 'NJ' THEN 'Northeast'
        WHEN 'CT' THEN 'Northeast'  WHEN 'ME' THEN 'Northeast'
        WHEN 'FL' THEN 'South'      WHEN 'GA' THEN 'South'
        WHEN 'NC' THEN 'South'      WHEN 'TN' THEN 'South'
        WHEN 'TX' THEN 'South'      WHEN 'VA' THEN 'South'
        WHEN 'IL' THEN 'Midwest'    WHEN 'OH' THEN 'Midwest'
        WHEN 'MI' THEN 'Midwest'    WHEN 'MN' THEN 'Midwest'
        WHEN 'WI' THEN 'Midwest'    WHEN 'MO' THEN 'Midwest'
        WHEN 'CA' THEN 'West'       WHEN 'WA' THEN 'West'
        WHEN 'CO' THEN 'West'       WHEN 'AZ' THEN 'West'
        WHEN 'OR' THEN 'West'       WHEN 'NV' THEN 'West'
        ELSE 'Other'
    END AS region,
    COUNT(DISTINCT o.id)    AS owners,
    COUNT(p.id)             AS pets
FROM owners_pets o
LEFT JOIN pets p ON o.id = p.owner_id
GROUP BY region
ORDER BY owners DESC;


-- -----------------------------------------------------------------------------
-- Q6. Pets per owner ratio — ranked by state
-- -----------------------------------------------------------------------------
SELECT
    TRIM(o.state)                                       AS state,
    COUNT(DISTINCT o.id)                                AS owners,
    COUNT(p.id)                                         AS pets,
    ROUND(COUNT(p.id)::NUMERIC / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS pets_per_owner
FROM owners_pets o
LEFT JOIN pets p ON o.id = p.owner_id
GROUP BY TRIM(o.state)
ORDER BY pets_per_owner DESC;
