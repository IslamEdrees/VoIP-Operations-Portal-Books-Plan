from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from .extensions import db
from .models import OperationPlan, PlanItem


check_items_bp = Blueprint(
    "check_items",
    __name__,
    url_prefix="/check-items",
)


CHECK_STATUSES = (
    "Planned",
    "In Progress",
    "Completed",
    "Blocked",
    "Cancelled",
)


@check_items_bp.route("/")
@login_required
def index():
    items = (
        PlanItem.query
        .order_by(
            PlanItem.plan_id.asc(),
            PlanItem.sort_order.asc(),
            PlanItem.id.asc(),
        )
        .all()
    )

    return render_template(
        "check_items/index.html",
        items=items,
    )


@check_items_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():
    plans = (
        OperationPlan.query
        .order_by(OperationPlan.plan_code.asc())
        .all()
    )

    if request.method == "POST":
        plan_id = request.form.get(
            "plan_id",
            type=int,
        )

        check_id = request.form.get(
            "check_id",
            "",
        ).strip().upper()

        check_type = request.form.get(
            "check_type",
            "",
        ).strip()

        check_item = request.form.get(
            "check_item",
            "",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "Planned",
        ).strip()

        result_notes = request.form.get(
            "result_notes",
            "",
        ).strip()

        sort_order = request.form.get(
            "sort_order",
            type=int,
        )

        error = None

        if not plan_id:
            error = "Operation Plan is required."

        elif not check_item:
            error = "Check Item is required."

        elif status not in CHECK_STATUSES:
            error = "Invalid Check Item Status."

        if sort_order is None:
            sort_order = 0

        plan = None

        if not error:
            plan = db.session.get(
                OperationPlan,
                plan_id,
            )

            if not plan:
                error = "Selected Operation Plan is invalid."

        if error:
            flash(error, "error")

        else:
            item = PlanItem(
                plan_id=plan.id,
                check_id=check_id or None,
                check_type=check_type or None,
                check_item=check_item,
                owner=owner or None,
                status=status,
                result_notes=result_notes or None,
                sort_order=sort_order,
            )

            db.session.add(item)
            db.session.commit()

            flash(
                "Check Item created successfully.",
                "success",
            )

            return redirect(
                url_for("check_items.index")
            )

    return render_template(
        "check_items/form.html",
        page_title="Create Check Item",
        plans=plans,
        check_statuses=CHECK_STATUSES,
        item=None,
    )


@check_items_bp.route(
    "/<int:item_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(item_id):
    item = db.get_or_404(
        PlanItem,
        item_id,
    )

    plans = (
        OperationPlan.query
        .order_by(OperationPlan.plan_code.asc())
        .all()
    )

    if request.method == "POST":
        plan_id = request.form.get(
            "plan_id",
            type=int,
        )

        check_id = request.form.get(
            "check_id",
            "",
        ).strip().upper()

        check_type = request.form.get(
            "check_type",
            "",
        ).strip()

        check_item = request.form.get(
            "check_item",
            "",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "",
        ).strip()

        result_notes = request.form.get(
            "result_notes",
            "",
        ).strip()

        sort_order = request.form.get(
            "sort_order",
            type=int,
        )

        error = None

        if not plan_id:
            error = "Operation Plan is required."

        elif not check_item:
            error = "Check Item is required."

        elif status not in CHECK_STATUSES:
            error = "Invalid Check Item Status."

        if sort_order is None:
            sort_order = 0

        plan = None

        if not error:
            plan = db.session.get(
                OperationPlan,
                plan_id,
            )

            if not plan:
                error = "Selected Operation Plan is invalid."

        if error:
            flash(error, "error")

        else:
            item.plan_id = plan.id
            item.check_id = check_id or None
            item.check_type = check_type or None
            item.check_item = check_item
            item.owner = owner or None
            item.status = status
            item.result_notes = result_notes or None
            item.sort_order = sort_order
            item.updated_at = db.func.now()

            db.session.commit()

            flash(
                "Check Item updated successfully.",
                "success",
            )

            return redirect(
                url_for("check_items.index")
            )

    return render_template(
        "check_items/form.html",
        page_title="Edit Check Item",
        plans=plans,
        check_statuses=CHECK_STATUSES,
        item=item,
    )
