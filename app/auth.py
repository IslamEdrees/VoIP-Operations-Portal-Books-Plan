from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from .extensions import db
from .models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if (
            user is None
            or not user.is_active
            or not check_password_hash(user.password_hash, password)
        ):
            flash("Invalid username or password.", "error")
            return render_template("login.html"), 401

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        login_user(user)

        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
