-- =============================================================================
-- PROJECT  : Movie Data Analysis
-- FILE     : sql/load_data.sql
-- PURPOSE  : Load clean CSVs into all five movie_data tables using \copy
-- DATABASE : movie_data (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d movie_data -f sql/load_data.sql
-- NOTE     : Run sql/schema.sql first to create the tables
--            Run from the project root so relative paths resolve correctly:
--              psql -U postgres -d movie_data -f sql/load_data.sql
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Truncate all tables (cascade handles FK dependencies).
-- Safe to re-run.
-- -----------------------------------------------------------------------------
TRUNCATE TABLE movies_actors, movie_revenues, movies, actors, directors
    RESTART IDENTITY CASCADE;


-- -----------------------------------------------------------------------------
-- Load data — dependency order (parents before children)
-- \copy is a psql client-side command — no server file permission required
-- -----------------------------------------------------------------------------

\copy directors (director_id, first_name, last_name, date_of_birth, nationality) FROM 'data/directors_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy actors (actor_id, first_name, last_name, gender, date_of_birth) FROM 'data/actors_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy movies (movie_id, movie_name, movie_length, movie_lang, release_date, age_certificate, director_id) FROM 'data/movies_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy movie_revenues (revenue_id, movie_id, domestic_takings, international_takings) FROM 'data/movie_revenues_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy movies_actors (movie_id, actor_id) FROM 'data/movies_actors_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');


-- -----------------------------------------------------------------------------
-- Reset sequences so future INSERTs don't collide with loaded IDs
-- -----------------------------------------------------------------------------
SELECT setval('directors_director_id_seq',   (SELECT MAX(director_id) FROM directors));
SELECT setval('actors_actor_id_seq',         (SELECT MAX(actor_id)    FROM actors));
SELECT setval('movies_movie_id_seq',         (SELECT MAX(movie_id)    FROM movies));
SELECT setval('movie_revenues_revenue_id_seq',(SELECT MAX(revenue_id) FROM movie_revenues));


-- -----------------------------------------------------------------------------
-- Verify row counts after load
-- -----------------------------------------------------------------------------
SELECT
    'directors'     AS table_name, COUNT(*) AS rows FROM directors  UNION ALL
SELECT 'actors',                              COUNT(*) FROM actors        UNION ALL
SELECT 'movies',                              COUNT(*) FROM movies        UNION ALL
SELECT 'movie_revenues',                      COUNT(*) FROM movie_revenues UNION ALL
SELECT 'movies_actors',                       COUNT(*) FROM movies_actors
ORDER BY table_name;
