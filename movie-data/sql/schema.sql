-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/schema.sql
-- PURPOSE  : DDL — Drop and recreate all tables, column comments, indexes
-- DATABASE : movie_data (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d movie_data -f sql/schema.sql
-- NOTE     : Run sql/00_create_database.sql first
-- =============================================================================


-- =============================================================================
-- ERD (Entity Relationship Diagram)
-- =============================================================================
--
--  directors
--  +---------------------+
--  | PK director_id      |<─────────────────────────────┐
--  |    first_name       |                              │
--  |    last_name        |                              │
--  |    date_of_birth    |                              │ FK
--  |    nationality      |                              │
--  +---------------------+                              │
--                                                       │
--  movies                                               │
--  +---------------------+                              │
--  | PK movie_id         |<──────────────┐              │
--  |    movie_name       |               │ FK           │
--  |    movie_length     |               │              │
--  |    movie_lang       |               │              │
--  |    release_date     |               │              │
--  |    age_certificate  |               │              │
--  | FK director_id ─────┼───────────────┼──────────────┘
--  +---------------------+               │
--                                        │
--  movie_revenues                        │       actors
--  +---------------------+               │       +---------------------+
--  | PK revenue_id       |               │       | PK actor_id         |<──┐
--  | FK movie_id ────────┼───────────────┘       |    first_name       |   │ FK
--  |    domestic_takings |                       |    last_name        |   │
--  |    intl_takings     |                       |    gender           |   │
--  +---------------------+                       |    date_of_birth    |   │
--                                                +---------------------+   │
--                                                                          │
--  movies_actors (junction)                                               │
--  +---------------------+                                                │
--  | PK,FK movie_id ─────┼────────────────────────────────────────────────┘
--  | PK,FK actor_id ─────┼──────────────────────────────────────────────────
--  +---------------------+
-- =============================================================================


-- -----------------------------------------------------------------------------
-- DROP (reverse FK order)
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS movies_actors;
DROP TABLE IF EXISTS movie_revenues;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS actors;
DROP TABLE IF EXISTS directors;


-- -----------------------------------------------------------------------------
-- CREATE
-- -----------------------------------------------------------------------------

CREATE TABLE directors (
    director_id   SERIAL          PRIMARY KEY,
    first_name    VARCHAR(30),
    last_name     VARCHAR(30)     NOT NULL,
    date_of_birth DATE,
    nationality   VARCHAR(20)
);

CREATE TABLE actors (
    actor_id      SERIAL          PRIMARY KEY,
    first_name    VARCHAR(30),
    last_name     VARCHAR(30),
    gender        CHAR(1),
    date_of_birth DATE
);

CREATE TABLE movies (
    movie_id         SERIAL          PRIMARY KEY,
    movie_name       VARCHAR(50)     NOT NULL,
    movie_length     INTEGER,
    movie_lang       VARCHAR(20),
    release_date     DATE,
    age_certificate  VARCHAR(5),
    director_id      INTEGER         REFERENCES directors(director_id)
);

CREATE TABLE movie_revenues (
    revenue_id            SERIAL          PRIMARY KEY,
    movie_id              INTEGER         REFERENCES movies(movie_id),
    domestic_takings      NUMERIC(6,2),
    international_takings NUMERIC(6,2)
);

CREATE TABLE movies_actors (
    movie_id  INTEGER  NOT NULL  REFERENCES movies(movie_id),
    actor_id  INTEGER  NOT NULL  REFERENCES actors(actor_id),
    PRIMARY KEY (movie_id, actor_id)
);


-- -----------------------------------------------------------------------------
-- COMMENTS
-- -----------------------------------------------------------------------------

COMMENT ON TABLE  directors                              IS 'One row per director';
COMMENT ON COLUMN directors.director_id                  IS 'Surrogate primary key';
COMMENT ON COLUMN directors.nationality                  IS 'Country of origin e.g. American, British, French';

COMMENT ON TABLE  actors                                 IS 'One row per actor';
COMMENT ON COLUMN actors.gender                          IS 'M = Male  |  F = Female';

COMMENT ON TABLE  movies                                 IS 'Core movie catalogue — one row per film';
COMMENT ON COLUMN movies.movie_length                    IS 'Runtime in minutes';
COMMENT ON COLUMN movies.age_certificate                 IS 'UK rating: U | PG | 12 | 15 | 18';
COMMENT ON COLUMN movies.director_id                     IS 'FK → directors.director_id';

COMMENT ON TABLE  movie_revenues                         IS 'Box-office takings — one row per movie (where available)';
COMMENT ON COLUMN movie_revenues.domestic_takings        IS 'US domestic box-office in millions USD';
COMMENT ON COLUMN movie_revenues.international_takings   IS 'International box-office in millions USD (NULL = not reported)';

COMMENT ON TABLE  movies_actors                          IS 'Junction table — many actors per movie, many movies per actor';


-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------

CREATE INDEX idx_movies_lang        ON movies (movie_lang);
CREATE INDEX idx_movies_cert        ON movies (age_certificate);
CREATE INDEX idx_movies_director    ON movies (director_id);
CREATE INDEX idx_movies_release     ON movies (release_date);
CREATE INDEX idx_directors_nat      ON directors (nationality);
CREATE INDEX idx_actors_gender      ON actors (gender);
CREATE INDEX idx_revenues_movie     ON movie_revenues (movie_id);
CREATE INDEX idx_movies_actors_act  ON movies_actors (actor_id);
