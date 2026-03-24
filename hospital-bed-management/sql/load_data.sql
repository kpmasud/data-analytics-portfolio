-- =============================================================================
-- PROJECT  : Hospital Bed Management Analysis
-- FILE     : sql/load_data.sql
-- PURPOSE  : Load clean CSVs into PostgreSQL tables
-- Run from project root:
--   psql -U postgres -d hospital_db -f sql/load_data.sql
-- =============================================================================

-- Load order: staff before staff_schedule (FK dependency)
TRUNCATE TABLE staff_schedule, bed_metrics, patients, staff RESTART IDENTITY CASCADE;

\copy staff (staff_id, staff_first_name, staff_last_name, role, service) FROM 'data/staff_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy staff_schedule (week, staff_id, role, service, present) FROM 'data/schedule_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy bed_metrics (week, month, service, available_beds, patients_request, patients_admitted, patients_refused, admission_rate, patient_satisfaction, staff_morale, event) FROM 'data/bed_metrics_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

\copy patients (patient_id, name, age, arrival_date, departure_date, length_of_stay, service, satisfaction) FROM 'data/patients_clean.csv' WITH (FORMAT CSV, HEADER TRUE, NULL '');

-- Verify
SELECT 'bed_metrics'      AS tbl, COUNT(*) FROM bed_metrics
UNION ALL SELECT 'patients',       COUNT(*) FROM patients
UNION ALL SELECT 'staff',          COUNT(*) FROM staff
UNION ALL SELECT 'staff_schedule', COUNT(*) FROM staff_schedule;
