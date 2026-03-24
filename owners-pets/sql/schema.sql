-- =============================================================================
-- PROJECT  : Owners & Pets Analysis
-- FILE     : sql/schema.sql
-- PURPOSE  : DDL — Drop and recreate all tables, column comments, indexes
-- DATABASE : owners_pets (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d owners_pets -f sql/schema.sql
-- NOTE     : Run sql/00_create_database.sql first
-- =============================================================================


-- =============================================================================
-- ERD (Entity Relationship Diagram)
-- =============================================================================
--
--  owners_pets
--  +---------------------+
--  | PK id               |<─────────────────────┐
--  |    first_name       |                      │ FK
--  |    last_name        |                      │
--  |    state  (2-char)  |                      │
--  |    email            |                      │
--  |    city   (3-char)  |                      │
--  +---------------------+                      │
--                                               │
--  pets                                         │
--  +---------------------+                      │
--  | PK id               |                      │
--  |    species          |                      │
--  |    full_name        |                      │
--  |    age              |                      │
--  | FK owner_id ────────┼──────────────────────┘
--  +---------------------+
-- =============================================================================


-- -----------------------------------------------------------------------------
-- DROP (reverse FK order)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS owners_pets;


-- -----------------------------------------------------------------------------
-- CREATE
-- -----------------------------------------------------------------------------

CREATE TABLE owners_pets (
    id          SERIAL          PRIMARY KEY,
    first_name  VARCHAR(30),
    last_name   VARCHAR(30),
    state       CHAR(2),
    email       VARCHAR(50),
    city        CHAR(3)
);

CREATE TABLE pets (
    id        SERIAL          PRIMARY KEY,
    species   VARCHAR(30),
    full_name VARCHAR(30),
    age       INTEGER         CHECK (age >= 0),
    owner_id  INTEGER         REFERENCES owners_pets(id)
);


-- -----------------------------------------------------------------------------
-- COMMENTS
-- -----------------------------------------------------------------------------

COMMENT ON TABLE  owners_pets            IS 'Pet owners — one row per owner';
COMMENT ON COLUMN owners_pets.state      IS '2-letter US state code e.g. NY, CA, TX';
COMMENT ON COLUMN owners_pets.city       IS '3-letter city abbreviation e.g. NYC, LAX, CHI';
COMMENT ON COLUMN owners_pets.email      IS 'Owner contact email address';

COMMENT ON TABLE  pets                   IS 'Pets — one row per pet; many pets can belong to one owner';
COMMENT ON COLUMN pets.species           IS 'Animal species e.g. Dog, Cat, Rabbit, Bird';
COMMENT ON COLUMN pets.full_name         IS 'Pet name as given by the owner';
COMMENT ON COLUMN pets.age              IS 'Pet age in years';
COMMENT ON COLUMN pets.owner_id          IS 'FK → owners_pets.id';


-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------

CREATE INDEX idx_owners_state   ON owners_pets (state);
CREATE INDEX idx_owners_city    ON owners_pets (city);
CREATE INDEX idx_pets_species   ON pets (species);
CREATE INDEX idx_pets_owner     ON pets (owner_id);
CREATE INDEX idx_pets_age       ON pets (age);
