-- =============================================================================
-- PROJECT  : UK Used Car Market Analysis
-- FILE     : sql/schema.sql
-- PURPOSE  : DDL — Table schema, column comments, and indexes
-- DATABASE : cars_uk (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d cars_uk -f sql/schema.sql
-- NOTE     : Run sql/00_create_database.sql first
-- =============================================================================


-- =============================================================================
-- ERD (Entity Relationship Diagram)
-- =============================================================================
--
--  This dataset is a single denormalised flat file representing used car
--  listings from 9 major UK brands.  The logical model is:
--
--  +------------------------------------------------------------+
--  |                           cars                             |
--  +------------------------------------------------------------+
--  | PK  car_id        SERIAL                                   |
--  |     brand         VARCHAR(50)   (Audi, BMW, Ford …)        |
--  |     model         VARCHAR(100)  (A1, 3 Series, Fiesta …)   |
--  |     year          SMALLINT      (1998–2020)                 |
--  |     price         INT           (GBP asking price)          |
--  |     transmission  VARCHAR(50)   (Manual / Automatic)        |
--  |     mileage       INT           (miles on the clock)        |
--  |     fuel_type     VARCHAR(50)   (Petrol / Diesel / Hybrid …)|
--  |     tax           INT           (annual road tax in GBP)    |
--  |     mpg           NUMERIC(6,2)  (miles per gallon)          |
--  |     engine_size   NUMERIC(4,2)  (litres)                    |
--  +------------------------------------------------------------+
--
--  Single-table model — all analysis is performed via aggregations
--  and window functions on this table.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- TABLE
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS cars;

CREATE TABLE cars (
    car_id        SERIAL          PRIMARY KEY,
    brand         VARCHAR(50)     NOT NULL,
    model         VARCHAR(100)    NOT NULL,
    year          SMALLINT        NOT NULL,
    price         INT             NOT NULL CHECK (price > 0),
    transmission  VARCHAR(50)     NOT NULL,
    mileage       INT             NOT NULL CHECK (mileage >= 0),
    fuel_type     VARCHAR(50)     NOT NULL,
    tax           INT,
    mpg           NUMERIC(6,2),
    engine_size   NUMERIC(4,2)    NOT NULL
);


-- -----------------------------------------------------------------------------
-- COMMENTS
-- -----------------------------------------------------------------------------

COMMENT ON TABLE  cars               IS 'UK used car listings — 9 brands, ~96k rows';
COMMENT ON COLUMN cars.brand         IS 'Car manufacturer: Audi, BMW, Ford, Hyundai, Mercedes, Skoda, Toyota, Vauxhall, Volkswagen';
COMMENT ON COLUMN cars.model         IS 'Specific model name e.g. A3, 3 Series, Focus';
COMMENT ON COLUMN cars.year          IS 'Year of manufacture (1998–2020)';
COMMENT ON COLUMN cars.price         IS 'Asking price in GBP';
COMMENT ON COLUMN cars.transmission  IS 'Gearbox type: Manual or Automatic';
COMMENT ON COLUMN cars.mileage       IS 'Odometer reading in miles';
COMMENT ON COLUMN cars.fuel_type     IS 'Fuel type: Petrol, Diesel, Hybrid, Electric, Other';
COMMENT ON COLUMN cars.tax           IS 'Annual road tax cost in GBP (nullable for some brands)';
COMMENT ON COLUMN cars.mpg           IS 'Fuel efficiency in miles per gallon (nullable for some brands)';
COMMENT ON COLUMN cars.engine_size   IS 'Engine displacement in litres';


-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------

CREATE INDEX idx_cars_brand         ON cars (brand);
CREATE INDEX idx_cars_model         ON cars (model);
CREATE INDEX idx_cars_year          ON cars (year);
CREATE INDEX idx_cars_price         ON cars (price);
CREATE INDEX idx_cars_transmission  ON cars (transmission);
CREATE INDEX idx_cars_fuel_type     ON cars (fuel_type);
CREATE INDEX idx_cars_engine_size   ON cars (engine_size);
