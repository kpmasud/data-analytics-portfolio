-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/load_data.sql
-- PURPOSE  : Load clean CSVs into owners_pets and pets tables using \copy
-- DATABASE : owners_pets (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d owners_pets -f sql/load_data.sql
-- NOTE     : Run sql/schema.sql first to create the tables
--            Run from the project root so relative paths resolve correctly:
--              psql -U postgres -d owners_pets -f sql/load_data.sql
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Truncate tables (pets first — FK dependency on owners_pets).
-- Safe to re-run.
-- -----------------------------------------------------------------------------
TRUNCATE TABLE pets, owners_pets RESTART IDENTITY CASCADE;


-- -----------------------------------------------------------------------------
-- Load data — owners first, then pets (parent before child)
-- \copy is a psql client-side command — no server file permission required
-- -----------------------------------------------------------------------------

\copy owners_pets (id, first_name, last_name, state, email, city) FROM 'data/owners_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy pets (id, species, full_name, age, owner_id) FROM 'data/pets_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');


-- -----------------------------------------------------------------------------
-- Reset sequences so future INSERTs don't collide with loaded IDs
-- -----------------------------------------------------------------------------
SELECT setval('owners_pets_id_seq', (SELECT MAX(id) FROM owners_pets));
SELECT setval('pets_id_seq',        (SELECT MAX(id) FROM pets));


-- -----------------------------------------------------------------------------
-- Verify row counts and basic stats after load
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*)                        AS total_owners,
    COUNT(DISTINCT state)           AS states_covered,
    COUNT(DISTINCT city)            AS cities_covered
FROM owners_pets;

SELECT
    COUNT(*)                        AS total_pets,
    COUNT(DISTINCT species)         AS unique_species,
    ROUND(AVG(age), 1)              AS avg_pet_age,
    MIN(age)                        AS youngest,
    MAX(age)                        AS oldest
FROM pets;
