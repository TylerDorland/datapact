#!/bin/bash
set -e

# This script is run by PostgreSQL on container initialization
# It creates the separate databases for each service

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create database for Contract Service
    CREATE DATABASE contracts;
    GRANT ALL PRIVILEGES ON DATABASE contracts TO datapact;

    -- Create database for Template Data Service
    CREATE DATABASE template_data;
    GRANT ALL PRIVILEGES ON DATABASE template_data TO datapact;

    -- Create database for Notification Service (Phase 5)
    CREATE DATABASE notifications;
    GRANT ALL PRIVILEGES ON DATABASE notifications TO datapact;
EOSQL

echo "Created databases: contracts, template_data, notifications"
