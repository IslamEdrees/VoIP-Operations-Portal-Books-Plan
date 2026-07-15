#!/usr/bin/env bash

set -euo pipefail

echo
echo "========================================="
echo " STEP 09 - ADMIN USER"
echo "========================================="

PROJECT_DIR="/opt/voip-operations"

cd "$PROJECT_DIR"

set -a
source .env
set +a

APP_PYTHON="$PROJECT_DIR/venv/bin/python3"

echo
echo "Checking administrator..."

ADMIN_COUNT=$("$APP_PYTHON" <<'PY'
from wsgi import app
from app.models import User

with app.app_context():
    print(User.query.filter_by(username="admin").count())
PY
)

if [ "$ADMIN_COUNT" -eq 0 ]; then

    echo "Creating administrator..."

    "$APP_PYTHON" scripts/create_admin.py

    echo "Administrator created."

else

    echo "Administrator already exists."

fi

echo
echo "Installed users"

"$APP_PYTHON" <<'PY'
from wsgi import app
from app.models import User

with app.app_context():
    for u in User.query.order_by(User.id):
        print(f"{u.id:3}  {u.username}")
PY

echo
echo "STEP 09 SUCCESS"
