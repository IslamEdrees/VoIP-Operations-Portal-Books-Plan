#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 05 - BOOKSTACK"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"

cd "$PROJECT_DIR"

if docker ps --format '{{.Names}}' | grep -q '^voip-kb-app$'; then
    echo "BookStack already running."

    docker ps \
        --filter name=voip-kb \
        --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo
    echo "STEP 05 SUCCESS"

    exit 0
fi

echo "Starting BookStack..."

docker compose \
    -f docker/docker-compose.yml \
    up -d

echo

echo "Waiting for containers..."

sleep 10

docker ps \
    --filter name=voip-kb \
    --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo

echo "STEP 05 SUCCESS"
