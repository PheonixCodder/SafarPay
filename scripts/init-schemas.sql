-- SafarPay PostgreSQL schema initialisation
-- Run once on first DB start via docker-entrypoint-initdb.d

-- Enable PostGIS for spatial queries (location + geospatial services)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create per-service schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS bidding;
CREATE SCHEMA IF NOT EXISTS verification;
CREATE SCHEMA IF NOT EXISTS geospatial;
CREATE SCHEMA IF NOT EXISTS location;

-- Grant privileges
GRANT ALL ON SCHEMA auth         TO safarpay;
GRANT ALL ON SCHEMA bidding      TO safarpay;
GRANT ALL ON SCHEMA verification TO safarpay;
GRANT ALL ON SCHEMA geospatial   TO safarpay;
GRANT ALL ON SCHEMA location     TO safarpay;
