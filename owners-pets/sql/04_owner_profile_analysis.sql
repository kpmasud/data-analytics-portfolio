-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/04_owner_profile_analysis.sql
-- PURPOSE  : Analyse owner profiles — email preferences, regional patterns,
--            pet name popularity, and multi-pet household insights
-- DATABASE : owners_pets
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Email domain preference — which providers do owners use most?
-- -----------------------------------------------------------------------------
SELECT
    SUBSTRING(email FROM POSITION('@' IN email) + 1)   AS email_domain,
    COUNT(*)                                            AS owner_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM owners_pets
WHERE email IS NOT NULL
GROUP BY email_domain
ORDER BY owner_count DESC;


-- -----------------------------------------------------------------------------
-- Q2. Email domain vs average pets owned
--     (do Gmail users have more pets than Yahoo users?)
-- -----------------------------------------------------------------------------
SELECT
    SUBSTRING(o.email FROM POSITION('@' IN o.email) + 1) AS email_domain,
    COUNT(DISTINCT o.id)                                  AS owners,
    COUNT(p.id)                                           AS total_pets,
    ROUND(COUNT(p.id)::NUMERIC / NULLIF(COUNT(DISTINCT o.id), 0), 2) AS avg_pets_per_owner
FROM owners_pets o
LEFT JOIN pets p ON o.id = p.owner_id
GROUP BY email_domain
ORDER BY avg_pets_per_owner DESC;


-- -----------------------------------------------------------------------------
-- Q3. Most popular pet names across the entire dataset
-- -----------------------------------------------------------------------------
SELECT
    full_name,
    species,
    COUNT(*) AS name_count
FROM pets
WHERE full_name IS NOT NULL
GROUP BY full_name, species
ORDER BY name_count DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Q4. Pet name length distribution — short vs long names by species
-- -----------------------------------------------------------------------------
SELECT
    species,
    ROUND(AVG(LENGTH(TRIM(full_name))), 1)  AS avg_name_length,
    MIN(LENGTH(TRIM(full_name)))            AS shortest,
    MAX(LENGTH(TRIM(full_name)))            AS longest
FROM pets
WHERE full_name IS NOT NULL
GROUP BY species
ORDER BY avg_name_length DESC;


-- -----------------------------------------------------------------------------
-- Q5. Owners with pets spanning multiple age groups
--     (youngest and oldest pet gap per owner)
-- -----------------------------------------------------------------------------
SELECT
    o.first_name || ' ' || o.last_name     AS owner,
    TRIM(o.state)                           AS state,
    COUNT(p.id)                             AS total_pets,
    MIN(p.age)                              AS youngest_pet_age,
    MAX(p.age)                              AS oldest_pet_age,
    MAX(p.age) - MIN(p.age)                AS age_range_years
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.id, o.first_name, o.last_name, o.state
HAVING COUNT(p.id) > 1
ORDER BY age_range_years DESC;


-- -----------------------------------------------------------------------------
-- Q6. Full owner summary — pets, species, avg age, state, email domain
-- -----------------------------------------------------------------------------
SELECT
    o.first_name || ' ' || o.last_name                     AS owner,
    TRIM(o.state)                                           AS state,
    TRIM(o.city)                                            AS city,
    SUBSTRING(o.email FROM POSITION('@' IN o.email) + 1)   AS email_domain,
    COUNT(p.id)                                             AS total_pets,
    COUNT(DISTINCT p.species)                               AS unique_species,
    ROUND(AVG(p.age), 1)                                    AS avg_pet_age,
    STRING_AGG(p.full_name, ', ' ORDER BY p.full_name)      AS pet_names
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.id, o.first_name, o.last_name, o.state, o.city, o.email
ORDER BY total_pets DESC, owner;
