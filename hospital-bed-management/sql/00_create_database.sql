-- Run as: psql -U postgres -f sql/00_create_database.sql

DROP DATABASE IF EXISTS hospital_db;

CREATE DATABASE hospital_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0;
