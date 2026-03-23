-- =============================================================================
-- PROJECT  : AirBNB NYC Market Analysis
-- FILE     : sql/schema.sql
-- PURPOSE  : DDL — Table schema, column comments, and indexes
-- DATABASE : airbnb_nyc (PostgreSQL 17)
-- RUN AS   : psql -U postgres -d airbnb_nyc -f sql/schema.sql
-- NOTE     : Run sql/00_create_database.sql first
-- =============================================================================


-- =============================================================================
-- ERD (Entity Relationship Diagram)
-- =============================================================================
--
--  This dataset is a single denormalised flat file representing Airbnb
--  listings in New York City.  The logical model is:
--
--  +------------------------------------------------------------+
--  |                         listings                          |
--  +------------------------------------------------------------+
--  | PK  listing_id          SERIAL                            |
--  |     host_id             BIGINT       (natural key)        |
--  |     host_since          DATE                              |
--  |     listing_name        TEXT                              |
--  |     neighbourhood       VARCHAR(100)  (borough level)     |
--  |     property_type       VARCHAR(100)                      |
--  |     room_type           VARCHAR(50)                       |
--  |     zipcode             VARCHAR(10)                       |
--  |     beds                NUMERIC(4,1)                      |
--  |     number_of_records   INT                               |
--  |     number_of_reviews   INT                               |
--  |     price               INT           (USD per night)     |
--  |     review_score_bin    NUMERIC(5,2)                      |
--  |     review_score_rating NUMERIC(5,2)                      |
--  +------------------------------------------------------------+
--
--  Single-table model — all analysis is performed via aggregations
--  and window functions on this table.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- TABLE
-- -----------------------------------------------------------------------------

DROP TABLE IF EXISTS listings;

CREATE TABLE listings (
    listing_id              SERIAL          PRIMARY KEY,
    host_id                 BIGINT          NOT NULL,
    host_since              DATE,
    listing_name            TEXT,
    neighbourhood           VARCHAR(100)    NOT NULL,
    property_type           VARCHAR(100)    NOT NULL,
    room_type               VARCHAR(50)     NOT NULL,
    zipcode                 VARCHAR(10),
    beds                    NUMERIC(4,1),
    number_of_records       INT             DEFAULT 1,
    number_of_reviews       INT             DEFAULT 0,
    price                   INT             NOT NULL CHECK (price > 0),
    review_score_bin        NUMERIC(5,2),
    review_score_rating     NUMERIC(5,2)
);


-- -----------------------------------------------------------------------------
-- COMMENTS
-- -----------------------------------------------------------------------------

COMMENT ON TABLE  listings                          IS 'Airbnb NYC listings — one row per listing';
COMMENT ON COLUMN listings.host_id                  IS 'Unique identifier for the host (natural key from source)';
COMMENT ON COLUMN listings.host_since               IS 'Date the host first registered on Airbnb';
COMMENT ON COLUMN listings.listing_name             IS 'Title/name of the listing as shown on Airbnb';
COMMENT ON COLUMN listings.neighbourhood            IS 'NYC borough: Manhattan, Brooklyn, Queens, Bronx, Staten Island';
COMMENT ON COLUMN listings.property_type            IS 'Type of property e.g. Apartment, House, Townhouse';
COMMENT ON COLUMN listings.room_type                IS 'Entire home/apt | Private room | Shared room';
COMMENT ON COLUMN listings.zipcode                  IS 'US ZIP code of the listing';
COMMENT ON COLUMN listings.beds                     IS 'Number of beds in the listing';
COMMENT ON COLUMN listings.number_of_records        IS 'Source record count (always 1 per listing row)';
COMMENT ON COLUMN listings.number_of_reviews        IS 'Total number of guest reviews received';
COMMENT ON COLUMN listings.price                    IS 'Nightly price in USD';
COMMENT ON COLUMN listings.review_score_bin         IS 'Binned review score (source grouping)';
COMMENT ON COLUMN listings.review_score_rating      IS 'Actual numeric review score out of 100';


-- -----------------------------------------------------------------------------
-- INDEXES  (support the most common GROUP BY / WHERE patterns)
-- -----------------------------------------------------------------------------

CREATE INDEX idx_listings_neighbourhood   ON listings (neighbourhood);
CREATE INDEX idx_listings_room_type       ON listings (room_type);
CREATE INDEX idx_listings_property_type   ON listings (property_type);
CREATE INDEX idx_listings_price           ON listings (price);
CREATE INDEX idx_listings_host_id         ON listings (host_id);
CREATE INDEX idx_listings_host_since      ON listings (host_since);
CREATE INDEX idx_listings_zipcode         ON listings (zipcode);
