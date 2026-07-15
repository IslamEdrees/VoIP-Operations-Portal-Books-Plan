#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 07 - SYSTEMD SERVICE"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"

cp systemd/voip-operations.service \
    /etc/systemd/system/voip-operations.service

systemctl daemon-reload

systemctl enable voip-operations

systemctl restart voip-operations

sleep 5

echo

systemctl --no-pager --full status voip-operations

echo

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
http://127.0.0.1:6880/api/health)

echo "Health HTTP : $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    echo
    echo "FAILED"
    exit 1
fi

echo
echo "STEP 07 SUCCESS"
