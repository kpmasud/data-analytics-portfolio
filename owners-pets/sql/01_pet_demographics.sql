-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/01_pet_demographics.sql
-- PURPOSE  : Analyse the pet population — species distribution, age
--            profiles, and average age by species
-- DATABASE : owners_pets
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. Species distribution — count and percentage
-- -----------------------------------------------------------------------------
SELECT
    species,
    COUNT(*)                                            AS pet_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM pets
GROUP BY species
ORDER BY pet_count DESC;


-- -----------------------------------------------------------------------------
-- Q2. Average and median age by species
-- -----------------------------------------------------------------------------
SELECT
    species,
    COUNT(*)                                            AS pet_count,
    ROUND(AVG(age), 1)                                  AS avg_age_years,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY age)                     AS median_age_years,
    MIN(age)                                            AS youngest,
    MAX(age)                                            AS oldest
FROM pets
WHERE age IS NOT NULL
GROUP BY species
ORDER BY avg_age_years DESC;


-- -----------------------------------------------------------------------------
-- Q3. Age distribution across all pets (bucket breakdown)
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN age = 0             THEN 'Under 1 yr'
        WHEN age BETWEEN 1 AND 2 THEN '1-2 yrs'
        WHEN age BETWEEN 3 AND 5 THEN '3-5 yrs'
        WHEN age BETWEEN 6 AND 9 THEN '6-9 yrs'
        ELSE '10+ yrs'
    END AS age_group,
    COUNT(*) AS pet_count
FROM pets
GROUP BY age_group
ORDER BY MIN(age);


-- -----------------------------------------------------------------------------
-- Q4. Pets per owner — distribution
-- -----------------------------------------------------------------------------
SELECT
    o.first_name || ' ' || o.last_name         AS owner,
    o.state,
    COUNT(p.id)                                AS pet_count
FROM owners_pets o
LEFT JOIN pets p ON o.id = p.owner_id
GROUP BY o.id, o.first_name, o.last_name, o.state
ORDER BY pet_count DESC;


-- -----------------------------------------------------------------------------
-- Q5. Species × age group matrix (heatmap data)
-- -----------------------------------------------------------------------------
SELECT
    species,
    CASE
        WHEN age BETWEEN 0 AND 2 THEN '0-2 yrs'
        WHEN age BETWEEN 3 AND 5 THEN '3-5 yrs'
        WHEN age BETWEEN 6 AND 9 THEN '6-9 yrs'
        ELSE '10+ yrs'
    END AS age_group,
    COUNT(*) AS pet_count
FROM pets
WHERE age IS NOT NULL
GROUP BY species, age_group
ORDER BY species, age_group;


-- -----------------------------------------------------------------------------
-- Q6. Youngest and oldest pet per species
-- -----------------------------------------------------------------------------
SELECT
    species,
    MIN(age)                AS youngest_age,
    MAX(age)                AS oldest_age,
    ROUND(AVG(age), 1)      AS avg_age,
    COUNT(*)                AS total_pets
FROM pets
WHERE age IS NOT NULL
GROUP BY species
ORDER BY avg_age DESC;
