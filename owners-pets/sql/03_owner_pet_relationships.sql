-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/03_owner_pet_relationships.sql
-- PURPOSE  : Explore owner-pet relationships — multi-pet households,
--            species diversity per state, and species preferences by city
-- DATABASE : owners_pets
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Multi-pet vs single-pet owners
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN pet_count = 0 THEN 'No pets'
        WHEN pet_count = 1 THEN '1 pet'
        WHEN pet_count = 2 THEN '2 pets'
        ELSE '3+ pets'
    END AS ownership_tier,
    COUNT(*) AS owner_count
FROM (
    SELECT o.id, COUNT(p.id) AS pet_count
    FROM owners_pets o
    LEFT JOIN pets p ON o.id = p.owner_id
    GROUP BY o.id
) owner_pet_counts
GROUP BY ownership_tier
ORDER BY MIN(pet_count);


-- -----------------------------------------------------------------------------
-- Q2. Most popular species by state
-- -----------------------------------------------------------------------------
SELECT
    o.state,
    p.species,
    COUNT(*)            AS pet_count
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.state, p.species
ORDER BY o.state, pet_count DESC;


-- -----------------------------------------------------------------------------
-- Q3. Species diversity per owner
--     (how many different species does each owner have?)
-- -----------------------------------------------------------------------------
SELECT
    o.first_name || ' ' || o.last_name  AS owner,
    o.state,
    COUNT(p.id)                          AS total_pets,
    COUNT(DISTINCT p.species)            AS unique_species
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.id, o.first_name, o.last_name, o.state
ORDER BY unique_species DESC, total_pets DESC;


-- -----------------------------------------------------------------------------
-- Q4. Species vs state heatmap data
-- -----------------------------------------------------------------------------
SELECT
    o.state,
    p.species,
    COUNT(*) AS count
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.state, p.species
ORDER BY o.state, p.species;


-- -----------------------------------------------------------------------------
-- Q5. Owners with the most species diversity (unique species per owner)
-- -----------------------------------------------------------------------------
SELECT
    o.first_name || ' ' || o.last_name     AS owner,
    TRIM(o.state)                           AS state,
    COUNT(p.id)                             AS total_pets,
    COUNT(DISTINCT p.species)               AS unique_species,
    STRING_AGG(DISTINCT p.species, ', '
        ORDER BY p.species)                 AS species_list
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY o.id, o.first_name, o.last_name, o.state
ORDER BY unique_species DESC, total_pets DESC;


-- -----------------------------------------------------------------------------
-- Q6. Pet count by species per city
-- -----------------------------------------------------------------------------
SELECT
    TRIM(o.city)    AS city,
    TRIM(o.state)   AS state,
    p.species,
    COUNT(*)        AS pet_count
FROM owners_pets o
JOIN pets p ON o.id = p.owner_id
GROUP BY TRIM(o.city), TRIM(o.state), p.species
ORDER BY city, pet_count DESC;
