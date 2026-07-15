#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

clear

echo "=================================================="
echo "      VoIP Operations Portal Installer"
echo "=================================================="

echo

for STEP in \
01_system.sh \
02_python.sh \
03_postgresql.sh \
04_docker.sh \
05_bookstack.sh \
06_portal.sh \
07_systemd.sh \
08_database.sh \
09_admin.sh \
10_healthcheck.sh
do

    echo
    echo "Running $STEP"
    echo

    bash "scripts/installer/$STEP"

done

echo
echo "=================================================="
echo " INSTALLATION COMPLETED SUCCESSFULLY"
echo "=================================================="

echo
echo "Portal     : http://$(hostname -I | awk '{print $1}'):6880"
echo "BookStack  : http://$(hostname -I | awk '{print $1}'):6875"

echo
