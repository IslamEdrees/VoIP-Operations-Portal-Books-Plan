#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 06 - VOIP OPERATIONS PORTAL"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"
APP_PYTHON="$PROJECT_DIR/venv/bin/python3"

cd "$PROJECT_DIR"

echo "Creating required directories..."

mkdir -p uploads
mkdir -p uploads/incidents
mkdir -p uploads/change_requests
mkdir -p backups

touch uploads/.gitkeep
touch backups/.gitkeep

echo
echo "Installing Python dependencies..."

if [ ! -d venv ]; then
    python3 -m venv venv
fi

"$PROJECT_DIR/venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/venv/bin/pip" install -r requirements.txt

echo
echo "Checking environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from template."
else
    echo ".env already exists."
fi

echo
echo "Loading environment..."

set -a
source .env
set +a

echo
echo "Validating Flask application..."

"$APP_PYTHON" <<'PY'
from wsgi import app
print("Application Loaded Successfully")
print("UPLOAD_FOLDER =", app.config["UPLOAD_FOLDER"])
print("Database URI Loaded")
PY

echo
echo "STEP 06 SUCCESS"
