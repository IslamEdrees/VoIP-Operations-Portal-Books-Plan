from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Account, OperationPlan


operation_plans_bp = Blueprint(
    "operation_plans",
    __name__,
    url_prefix="/operation-plans",
)


PLAN_TYPES = (
    "PRE-Migration",
    "Post-Migration",
    "Migration",
    "Maintenance",
    "Upgrade",
    "Deployment",
    "General Operations",
)


PLAN_STATUSES = (
    "Draft",
    "Planned",
    "In Progress",
    "Completed",
    "Cancelled",
)


@operation_plans_bp.route("/")
@login_required
def index():
    plans = (
        OperationPlan.query
        .order_by(OperationPlan.created_at.desc())
        .all()
    )

    return render_template(
        "operation_plans/index.html",
        plans=plans,
    )


@operation_plans_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():
    accounts = (
        Account.query
        .filter_by(is_active=True)
        .order_by(Account.code.asc())
        .all()
    )

    if request.method == "POST":
        account_id = request.form.get(
            "account_id",
            type=int,
        )

        plan_code = request.form.get(
            "plan_code",
            "",
        ).strip().upper()

        name = request.form.get(
            "name",
            "",
        ).strip()

        plan_type = request.form.get(
            "plan_type",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "Planned",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip()

        plan_date_value = request.form.get(
            "plan_date",
            "",
        ).strip()

        error = None
        plan_date = None

        if not account_id:
            error = "Account is required."

        elif not plan_code:
            error = "Plan Code is required."

        elif not name:
            error = "Plan Name is required."

        elif plan_type not in PLAN_TYPES:
            error = "Invalid Plan Type."

        elif status not in PLAN_STATUSES:
            error = "Invalid Plan Status."

        if not error and plan_date_value:
            try:
                plan_date = datetime.strptime(
                    plan_date_value,
                    "%Y-%m-%d",
                ).date()

            except ValueError:
                error = "Invalid Plan Date."

        account = None

        if not error:
            account = db.session.get(
                Account,
                account_id,
            )

            if not account or not account.is_active:
                error = "Selected account is invalid."

        if error:
            flash(error, "error")

        else:
            plan = OperationPlan(
                plan_code=plan_code,
                account_id=account.id,
                name=name,
                plan_type=plan_type,
                description=description or None,
                status=status,
                owner=owner or None,
                plan_date=plan_date,
                created_by=current_user.id,
            )

            db.session.add(plan)

            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()

                flash(
                    "Plan Code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Operation Plan {plan_code} "
                    "created successfully.",
                    "success",
                )

                return redirect(
                    url_for("operation_plans.index")
                )

    return render_template(
        "operation_plans/form.html",
        page_title="Create Operation Plan",
        accounts=accounts,
        plan_types=PLAN_TYPES,
        plan_statuses=PLAN_STATUSES,
        plan=None,
    )


@operation_plans_bp.route(
    "/<int:plan_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(plan_id):
    plan = db.get_or_404(
        OperationPlan,
        plan_id,
    )

    accounts = (
        Account.query
        .order_by(Account.code.asc())
        .all()
    )

    if request.method == "POST":
        account_id = request.form.get(
            "account_id",
            type=int,
        )

        plan_code = request.form.get(
            "plan_code",
            "",
        ).strip().upper()

        name = request.form.get(
            "name",
            "",
        ).strip()

        plan_type = request.form.get(
            "plan_type",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip()

        plan_date_value = request.form.get(
            "plan_date",
            "",
        ).strip()

        error = None
        plan_date = None

        if not account_id:
            error = "Account is required."

        elif not plan_code:
            error = "Plan Code is required."

        elif not name:
            error = "Plan Name is required."

        elif plan_type not in PLAN_TYPES:
            error = "Invalid Plan Type."

        elif status not in PLAN_STATUSES:
            error = "Invalid Plan Status."

        if not error and plan_date_value:
            try:
                plan_date = datetime.strptime(
                    plan_date_value,
                    "%Y-%m-%d",
                ).date()

            except ValueError:
                error = "Invalid Plan Date."

        account = None

        if not error:
            account = db.session.get(
                Account,
                account_id,
            )

            if not account:
                error = "Selected account is invalid."

        if error:
            flash(error, "error")

        else:
            plan.plan_code = plan_code
            plan.account_id = account.id
            plan.name = name
            plan.plan_type = plan_type
            plan.description = description or None
            plan.status = status
            plan.owner = owner or None
            plan.plan_date = plan_date
            plan.updated_at = db.func.now()

            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()

                flash(
                    "Plan Code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Operation Plan {plan_code} "
                    "updated successfully.",
                    "success",
                )

                return redirect(
                    url_for("operation_plans.index")
                )

    return render_template(
        "operation_plans/form.html",
        page_title="Edit Operation Plan",
        accounts=accounts,
        plan_types=PLAN_TYPES,
        plan_statuses=PLAN_STATUSES,
        plan=plan,
    )
