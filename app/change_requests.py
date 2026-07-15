from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Account, Attachment, ChangeRequest


change_requests_bp = Blueprint(
    "change_requests",
    __name__,
    url_prefix="/change-requests",
)


CHANGE_TYPES = (
    "Application",
    "Infrastructure",
    "Network",
    "VoIP",
    "Aheeva",
    "Database",
    "Security",
    "Maintenance",
    "Upgrade",
    "Migration",
    "Deployment",
    "Configuration",
    "General Operations",
)


RISK_LEVELS = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


CHANGE_STATUSES = (
    "Draft",
    "Planned",
    "Pending Approval",
    "Approved",
    "In Progress",
    "Completed",
    "Failed",
    "Cancelled",
)


ALLOWED_ATTACHMENT_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "txt",
    "png",
    "jpg",
    "jpeg",
}


def allowed_attachment(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_ATTACHMENT_EXTENSIONS
    )


def save_change_request_attachment(change, uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        return None

    original_filename = Path(
        uploaded_file.filename
    ).name

    if not original_filename:
        raise ValueError("Invalid attachment filename.")

    if not allowed_attachment(original_filename):
        raise ValueError(
            "Invalid attachment file type."
        )

    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )

    stored_filename = (
        f"{uuid4().hex}.{extension}"
    )

    relative_directory = Path(
        "change_requests"
    ) / str(change.id)

    absolute_directory = (
        Path(current_app.config["UPLOAD_FOLDER"])
        / relative_directory
    )

    absolute_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    absolute_path = (
        absolute_directory
        / stored_filename
    )

    uploaded_file.save(absolute_path)

    file_size = absolute_path.stat().st_size

    relative_path = (
        relative_directory
        / stored_filename
    )

    attachment = Attachment(
        entity_type="change_request",
        entity_id=change.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(relative_path),
        mime_type=uploaded_file.mimetype or None,
        file_size=file_size,
        uploaded_by=current_user.id,
    )

    db.session.add(attachment)

    return attachment


def parse_datetime_local(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M",
        )

    except ValueError:
        return None


@change_requests_bp.route("/")
@login_required
def index():
    changes = (
        ChangeRequest.query
        .order_by(ChangeRequest.created_at.desc())
        .all()
    )

    return render_template(
        "change_requests/index.html",
        changes=changes,
    )


@change_requests_bp.route(
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

        change_code = request.form.get(
            "change_code",
            "",
        ).strip().upper()

        title = request.form.get(
            "title",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        change_type = request.form.get(
            "change_type",
            "",
        ).strip()

        risk_level = request.form.get(
            "risk_level",
            "Medium",
        ).strip()

        status = request.form.get(
            "status",
            "Draft",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip()

        implementation_plan = request.form.get(
            "implementation_plan",
            "",
        ).strip()

        rollback_plan = request.form.get(
            "rollback_plan",
            "",
        ).strip()

        validation_plan = request.form.get(
            "validation_plan",
            "",
        ).strip()

        scheduled_at_value = request.form.get(
            "scheduled_at",
            "",
        ).strip()

        completed_at_value = request.form.get(
            "completed_at",
            "",
        ).strip()

        error = None

        if not account_id:
            error = "Account is required."

        elif not change_code:
            error = "Change Code is required."

        elif not title:
            error = "Title is required."

        elif risk_level not in RISK_LEVELS:
            error = "Invalid Risk Level."

        elif status not in CHANGE_STATUSES:
            error = "Invalid Change Request Status."

        scheduled_at = None
        completed_at = None

        if not error and scheduled_at_value:
            scheduled_at = parse_datetime_local(
                scheduled_at_value
            )

            if scheduled_at is None:
                error = "Invalid Scheduled Date and Time."

        if not error and completed_at_value:
            completed_at = parse_datetime_local(
                completed_at_value
            )

            if completed_at is None:
                error = "Invalid Completed Date and Time."

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
            change = ChangeRequest(
                change_code=change_code,
                account_id=account.id,
                title=title,
                description=description or None,
                change_type=change_type or None,
                risk_level=risk_level,
                status=status,
                owner=owner or None,
                implementation_plan=implementation_plan or None,
                rollback_plan=rollback_plan or None,
                validation_plan=validation_plan or None,
                scheduled_at=scheduled_at,
                completed_at=completed_at,
                created_by=current_user.id,
            )

            db.session.add(change)

            try:
                db.session.flush()

                uploaded_file = request.files.get(
                    "attachment"
                )

                if (
                    uploaded_file
                    and uploaded_file.filename
                ):
                    save_change_request_attachment(
                        change,
                        uploaded_file,
                    )

                db.session.commit()

            except ValueError as exc:
                db.session.rollback()

                flash(
                    str(exc),
                    "error",
                )

            except IntegrityError:
                db.session.rollback()

                flash(
                    "Change Code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Change Request {change_code} "
                    "created successfully.",
                    "success",
                )

                return redirect(
                    url_for("change_requests.index")
                )

    return render_template(
        "change_requests/form.html",
        page_title="Create Change Request",
        accounts=accounts,
        change_types=CHANGE_TYPES,
        risk_levels=RISK_LEVELS,
        change_statuses=CHANGE_STATUSES,
        change=None,
    )


@change_requests_bp.route(
    "/<int:change_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(change_id):
    change = db.get_or_404(
        ChangeRequest,
        change_id,
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

        change_code = request.form.get(
            "change_code",
            "",
        ).strip().upper()

        title = request.form.get(
            "title",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        change_type = request.form.get(
            "change_type",
            "",
        ).strip()

        risk_level = request.form.get(
            "risk_level",
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

        implementation_plan = request.form.get(
            "implementation_plan",
            "",
        ).strip()

        rollback_plan = request.form.get(
            "rollback_plan",
            "",
        ).strip()

        validation_plan = request.form.get(
            "validation_plan",
            "",
        ).strip()

        scheduled_at_value = request.form.get(
            "scheduled_at",
            "",
        ).strip()

        completed_at_value = request.form.get(
            "completed_at",
            "",
        ).strip()

        error = None

        if not account_id:
            error = "Account is required."

        elif not change_code:
            error = "Change Code is required."

        elif not title:
            error = "Title is required."

        elif risk_level not in RISK_LEVELS:
            error = "Invalid Risk Level."

        elif status not in CHANGE_STATUSES:
            error = "Invalid Change Request Status."

        scheduled_at = None
        completed_at = None

        if not error and scheduled_at_value:
            scheduled_at = parse_datetime_local(
                scheduled_at_value
            )

            if scheduled_at is None:
                error = "Invalid Scheduled Date and Time."

        if not error and completed_at_value:
            completed_at = parse_datetime_local(
                completed_at_value
            )

            if completed_at is None:
                error = "Invalid Completed Date and Time."

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
            change.change_code = change_code
            change.account_id = account.id
            change.title = title
            change.description = description or None
            change.change_type = change_type or None
            change.risk_level = risk_level
            change.status = status
            change.owner = owner or None
            change.implementation_plan = (
                implementation_plan or None
            )
            change.rollback_plan = rollback_plan or None
            change.validation_plan = validation_plan or None
            change.scheduled_at = scheduled_at
            change.completed_at = completed_at
            change.updated_at = db.func.now()

            try:
                uploaded_file = request.files.get(
                    "attachment"
                )

                if (
                    uploaded_file
                    and uploaded_file.filename
                ):
                    save_change_request_attachment(
                        change,
                        uploaded_file,
                    )

                db.session.commit()

            except ValueError as exc:
                db.session.rollback()

                flash(
                    str(exc),
                    "error",
                )

            except IntegrityError:
                db.session.rollback()

                flash(
                    "Change Code already exists.",
                    "error",
                )

            else:
                flash(
                    f"Change Request {change_code} "
                    "updated successfully.",
                    "success",
                )

                return redirect(
                    url_for("change_requests.index")
                )

    attachments = (
        Attachment.query
        .filter_by(
            entity_type="change_request",
            entity_id=change.id,
        )
        .order_by(Attachment.created_at.desc())
        .all()
    )

    return render_template(
        "change_requests/form.html",
        page_title="Edit Change Request",
        accounts=accounts,
        change_types=CHANGE_TYPES,
        risk_levels=RISK_LEVELS,
        change_statuses=CHANGE_STATUSES,
        change=change,
        attachments=attachments,
    )


@change_requests_bp.route(
    "/<int:change_id>/attachments/"
    "<int:attachment_id>/download"
)
@login_required
def download_attachment(
    change_id,
    attachment_id,
):
    change = db.get_or_404(
        ChangeRequest,
        change_id,
    )

    attachment = db.get_or_404(
        Attachment,
        attachment_id,
    )

    if (
        attachment.entity_type != "change_request"
        or attachment.entity_id != change.id
    ):
        abort(404)

    absolute_path = (
        Path(current_app.config["UPLOAD_FOLDER"])
        / attachment.file_path
    )

    if not absolute_path.is_file():
        abort(404)

    return send_from_directory(
        absolute_path.parent,
        absolute_path.name,
        as_attachment=True,
        download_name=attachment.original_filename,
    )
