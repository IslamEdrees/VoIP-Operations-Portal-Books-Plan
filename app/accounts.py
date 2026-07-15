from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Account


accounts_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/accounts",
)


def admin_required():
    if current_user.role != "admin":
        abort(403)


@accounts_bp.route("/")
@login_required
def index():
    accounts = Account.query.order_by(
        Account.code.asc()
    ).all()

    return render_template(
        "accounts/index.html",
        accounts=accounts,
        user=current_user,
    )


@accounts_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    admin_required()

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        description = request.form.get(
            "description",
            "",
        ).strip()

        if not code:
            flash("Account code is required.", "error")

        elif not name:
            flash("Account name is required.", "error")

        else:
            account = Account(
                code=code,
                name=name,
                description=description or None,
                is_active=True,
            )

            db.session.add(account)

            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                flash(
                    "Account code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Account {code} created successfully.",
                    "success",
                )

                return redirect(
                    url_for("accounts.index")
                )

    return render_template(
        "accounts/form.html",
        account=None,
        page_title="Create Account",
        user=current_user,
    )


@accounts_bp.route(
    "/<int:account_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(account_id):
    admin_required()

    account = db.get_or_404(Account, account_id)

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        description = request.form.get(
            "description",
            "",
        ).strip()

        if not code:
            flash("Account code is required.", "error")

        elif not name:
            flash("Account name is required.", "error")

        else:
            account.code = code
            account.name = name
            account.description = description or None

            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                flash(
                    "Account code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Account {code} updated successfully.",
                    "success",
                )

                return redirect(
                    url_for("accounts.index")
                )

    return render_template(
        "accounts/form.html",
        account=account,
        page_title="Edit Account",
        user=current_user,
    )


@accounts_bp.route(
    "/<int:account_id>/toggle",
    methods=["POST"],
)
@login_required
def toggle(account_id):
    admin_required()

    account = db.get_or_404(Account, account_id)

    account.is_active = not account.is_active

    db.session.commit()

    state = "enabled" if account.is_active else "disabled"

    flash(
        f"Account {account.code} {state}.",
        "success",
    )

    return redirect(
        url_for("accounts.index")
    )
