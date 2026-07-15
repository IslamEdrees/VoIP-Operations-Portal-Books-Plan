from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from .extensions import db


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    counts = {}

    for table in (
        "accounts",
        "incidents",
        "change_requests",
        "operation_plans",
        "plan_items",
    ):
        result = db.session.execute(
            db.text(f"SELECT COUNT(*) FROM {table}")
        ).scalar_one()

        counts[table] = result

    return render_template(
        "dashboard.html",
        counts=counts,
        user=current_user,
    )


@main_bp.route("/api/health")
def health():
    database_status = "down"

    try:
        db.session.execute(db.text("SELECT 1"))
        database_status = "up"
    except Exception:
        database_status = "down"

    status_code = 200 if database_status == "up" else 503

    return jsonify(
        {
            "application": "VoIP Operations Portal",
            "status": "up",
            "database": database_status,
        }
    ), status_code
