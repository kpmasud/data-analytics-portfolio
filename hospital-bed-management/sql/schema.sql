-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/schema.sql
-- PURPOSE  : Create tables for hospital operational data
-- =============================================================================
--
-- ERD (simplified):
--
--   staff ──────────────────────────── staff_schedule
--   staff_id (PK)                      week
--   staff_first_name                   staff_id (FK → staff)
--   staff_last_name                    role
--   role                               service
--   service                            present
--
--   bed_metrics                        patients
--   week                               patient_id (PK)
--   month                              name
--   service  ◄── joins on service ──►  age
--   available_beds                     arrival_date
--   patients_request                   departure_date
--   patients_admitted                  length_of_stay
--   patients_refused                   service
--   admission_rate                     satisfaction
--   patient_satisfaction
--   staff_morale
--   event
-- =============================================================================

-- ── staff ──────────────────────────────────────────────────────────────────
CREATE TABLE staff (
    staff_id          VARCHAR(20)  PRIMARY KEY,
    staff_first_name  VARCHAR(50)  NOT NULL,
    staff_last_name   VARCHAR(50)  NOT NULL,
    role              VARCHAR(50)  NOT NULL,
    service           VARCHAR(50)  NOT NULL
);

-- ── staff_schedule ─────────────────────────────────────────────────────────
CREATE TABLE staff_schedule (
    id       SERIAL       PRIMARY KEY,
    week     SMALLINT     NOT NULL,
    staff_id VARCHAR(20)  NOT NULL,
    role     VARCHAR(50)  NOT NULL,
    service  VARCHAR(50)  NOT NULL,
    present  SMALLINT     NOT NULL CHECK (present IN (0, 1))
);

-- ── bed_metrics ────────────────────────────────────────────────────────────
CREATE TABLE bed_metrics (
    id                   SERIAL        PRIMARY KEY,
    week                 SMALLINT      NOT NULL,
    month                SMALLINT      NOT NULL,
    service              VARCHAR(50)   NOT NULL,
    available_beds       INT           NOT NULL,
    patients_request     INT           NOT NULL,
    patients_admitted    INT           NOT NULL,
    patients_refused     INT           NOT NULL,
    admission_rate       NUMERIC(5,1),
    patient_satisfaction NUMERIC(5,1),
    staff_morale         NUMERIC(5,1),
    event                VARCHAR(50)   DEFAULT 'none'
);

-- ── patients ───────────────────────────────────────────────────────────────
CREATE TABLE patients (
    patient_id      VARCHAR(20)  PRIMARY KEY,
    name            VARCHAR(100),
    age             SMALLINT,
    arrival_date    DATE         NOT NULL,
    departure_date  DATE         NOT NULL,
    length_of_stay  SMALLINT     NOT NULL,
    service         VARCHAR(50)  NOT NULL,
    satisfaction    SMALLINT
);

-- ── indexes ────────────────────────────────────────────────────────────────
CREATE INDEX idx_bed_metrics_service ON bed_metrics(service);
CREATE INDEX idx_bed_metrics_week    ON bed_metrics(week);
CREATE INDEX idx_bed_metrics_month   ON bed_metrics(month);
CREATE INDEX idx_bed_metrics_event   ON bed_metrics(event);
CREATE INDEX idx_patients_service    ON patients(service);
CREATE INDEX idx_patients_arrival    ON patients(arrival_date);
CREATE INDEX idx_schedule_staff      ON staff_schedule(staff_id);
CREATE INDEX idx_schedule_week       ON staff_schedule(week);
CREATE INDEX idx_schedule_service    ON staff_schedule(service);
