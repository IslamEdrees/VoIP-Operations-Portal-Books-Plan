#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 10 - FINAL HEALTH CHECK"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"

cd "$PROJECT_DIR"

set -a
source .env
set +a

echo
echo "Checking PostgreSQL..."

systemctl is-active postgresql

echo
echo "Checking Docker..."

systemctl is-active docker

echo
echo "Checking Portal..."

systemctl is-active voip-operations

echo
echo "Checking BookStack..."

docker ps \
--filter name=voip-kb \
--format "table {{.Names}}\t{{.Status}}"

echo
echo "Checking HTTP..."

curl -fsS http://127.0.0.1:6880/api/health | python3 -m json.tool

echo
echo "Checking Upload Directories..."

test -d uploads
test -d uploads/incidents
test -d uploads/change_requests

echo "Upload directories OK"

echo
echo "Checking Database..."

PGPASSWORD="$DB_PASSWORD" \
psql \
-h "$DB_HOST" \
-U "$DB_USER" \
-d "$DB_NAME" \
-c "select count(*) as users from users;"

echo
echo "Checking Gunicorn..."

pgrep -fa gunicorn

echo
echo "========================================="
echo " INSTALLATION VERIFIED SUCCESSFULLY"
echo "========================================="
