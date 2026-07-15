#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 08 - DATABASE"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"

cd "$PROJECT_DIR"

set -a
source .env
set +a

echo
echo "Checking PostgreSQL..."

if ! systemctl is-active --quiet postgresql; then
    systemctl start postgresql
fi

echo "PostgreSQL : RUNNING"

echo
echo "Checking database user..."

if sudo -u postgres psql -tAc \
"SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" \
| grep -q 1
then
    echo "User exists."
else

    sudo -u postgres psql <<SQL
CREATE USER ${DB_USER}
WITH PASSWORD '${DB_PASSWORD}';

ALTER USER ${DB_USER}
CREATEDB;
SQL

    echo "User created."

fi

echo
echo "Checking database..."

if sudo -u postgres psql -tAc \
"SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" \
| grep -q 1
then

    echo "Database exists."

else

    sudo -u postgres createdb \
        -O "${DB_USER}" \
        "${DB_NAME}"

    echo "Database created."

fi

echo
echo "Checking schema..."

TABLES=$(PGPASSWORD="$DB_PASSWORD" \
psql \
-h "$DB_HOST" \
-U "$DB_USER" \
-d "$DB_NAME" \
-tAc \
"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")

if [ "$TABLES" -eq 0 ]; then

    echo "Importing schema..."

    PGPASSWORD="$DB_PASSWORD" \
    psql \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        < migrations/001_initial_schema.sql

    echo "Schema imported."

else

    echo "Schema already exists."

fi

echo
echo "Tables:"

PGPASSWORD="$DB_PASSWORD" \
psql \
-h "$DB_HOST" \
-U "$DB_USER" \
-d "$DB_NAME" \
-c "\dt"

echo
echo "STEP 08 SUCCESS"
