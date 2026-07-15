#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 03 - POSTGRESQL"
echo "========================================="

if systemctl is-active --quiet postgresql; then
    echo "PostgreSQL Service : RUNNING"
else
    echo "Installing PostgreSQL..."

    apt-get update

    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        postgresql \
        postgresql-contrib

    systemctl enable postgresql
    systemctl start postgresql
fi

echo

psql --version

echo

systemctl --no-pager --full status postgresql | head -5

echo

echo "Checking database..."

DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='voip_operations';")

if [ "$DB_EXISTS" = "1" ]; then
    echo "Database : EXISTS"
else
    echo "Database : NOT FOUND"
fi

echo

echo "Checking user..."

USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='voip_operations';")

if [ "$USER_EXISTS" = "1" ]; then
    echo "User : EXISTS"
else
    echo "User : NOT FOUND"
fi

echo

echo "STEP 03 SUCCESS"
