from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
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
from .models import Account, Attachment, Incident


incidents_bp = Blueprint(
    "incidents",
    __name__,
    url_prefix="/incidents",
)


SEVERITIES = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


STATUSES = (
    "Open",
    "Investigating",
    "Monitoring",
    "Resolved",
    "Closed",
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


def get_incident_attachments(incident_id):
    return (
        Attachment.query
        .filter_by(
            entity_type="incident",
            entity_id=incident_id,
        )
        .order_by(
            Attachment.created_at.desc(),
            Attachment.id.desc(),
        )
        .all()
    )


def validate_attachment(file):
    if file is None or not file.filename:
        return None

    original_filename = Path(file.filename).name

    if not original_filename:
        raise ValueError(
            "Invalid attachment filename."
        )

    if "." not in original_filename:
        raise ValueError(
            "Attachment must have a file extension."
        )

    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValueError(
            "Unsupported attachment type. "
            "Allowed: PDF, DOC, DOCX, XLS, XLSX, "
            "CSV, TXT, PNG, JPG and JPEG."
        )

    return original_filename, extension


def save_incident_attachment(incident, file):
    validated = validate_attachment(file)

    if validated is None:
        return None

    original_filename, extension = validated

    incident_directory = (
        Path(current_app.config["UPLOAD_DIR"])
        / "incidents"
        / str(incident.id)
    )

    incident_directory.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o750,
    )

    stored_filename = (
        f"{uuid4().hex}.{extension}"
    )

    absolute_path = (
        incident_directory
        / stored_filename
    )

    file.save(absolute_path)

    file_size = absolute_path.stat().st_size

    if file_size <= 0:
        absolute_path.unlink(missing_ok=True)

        raise ValueError(
            "Empty attachments are not allowed."
        )

    relative_path = str(
        Path("incidents")
        / str(incident.id)
        / stored_filename
    )

    attachment = Attachment(
        entity_type="incident",
        entity_id=incident.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=relative_path,
        mime_type=file.mimetype or None,
        file_size=file_size,
        uploaded_by=current_user.id,
    )

    db.session.add(attachment)

    return attachment


def parse_datetime_local(value):
    value = (value or "").strip()

    if not value:
        return None

    return datetime.fromisoformat(value)


def get_active_accounts():
    return (
        Account.query
        .filter_by(is_active=True)
        .order_by(Account.code.asc())
        .all()
    )


@incidents_bp.route("/")
@login_required
def index():
    incidents = (
        Incident.query
        .order_by(
            Incident.created_at.desc(),
            Incident.id.desc(),
        )
        .all()
    )

    return render_template(
        "incidents/index.html",
        incidents=incidents,
    )


@incidents_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():
    accounts = get_active_accounts()

    if request.method == "POST":
        incident_code = (
            request.form.get("incident_code", "")
            .strip()
            .upper()
        )

        account_id = request.form.get(
            "account_id",
            type=int,
        )

        title = request.form.get(
            "title",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip() or None

        severity = request.form.get(
            "severity",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip() or None

        root_cause = request.form.get(
            "root_cause",
            "",
        ).strip() or None

        resolution = request.form.get(
            "resolution",
            "",
        ).strip() or None

        started_at_raw = request.form.get(
            "started_at",
            "",
        )

        resolved_at_raw = request.form.get(
            "resolved_at",
            "",
        )

        if not incident_code:
            flash(
                "Incident Code is required.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if not account_id:
            flash(
                "Account is required.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        account = db.session.get(
            Account,
            account_id,
        )

        if account is None or not account.is_active:
            flash(
                "Selected Account is invalid.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if not title:
            flash(
                "Title is required.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if severity not in SEVERITIES:
            flash(
                "Invalid Severity.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if status not in STATUSES:
            flash(
                "Invalid Status.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        try:
            started_at = parse_datetime_local(
                started_at_raw
            )

            resolved_at = parse_datetime_local(
                resolved_at_raw
            )
        except ValueError:
            flash(
                "Invalid date or time value.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        incident = Incident(
            incident_code=incident_code,
            account_id=account_id,
            title=title,
            description=description,
            severity=severity,
            status=status,
            owner=owner,
            root_cause=root_cause,
            resolution=resolution,
            started_at=started_at,
            resolved_at=resolved_at,
            created_by=current_user.id,
        )

        db.session.add(incident)

        try:
            db.session.flush()

            attachment_file = request.files.get(
                "attachment"
            )

            save_incident_attachment(
                incident,
                attachment_file,
            )

            db.session.commit()

        except ValueError as exc:
            db.session.rollback()

            flash(
                str(exc),
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        except IntegrityError:
            db.session.rollback()

            flash(
                "Incident Code already exists.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=None,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        flash(
            f"Incident {incident.incident_code} "
            "created successfully.",
            "success",
        )

        return redirect(
            url_for("incidents.index")
        )

    return render_template(
        "incidents/form.html",
        incident=None,
        accounts=accounts,
        severities=SEVERITIES,
        statuses=STATUSES,
    )


@incidents_bp.route(
    "/<int:incident_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(incident_id):
    incident = db.get_or_404(
        Incident,
        incident_id,
    )

    accounts = get_active_accounts()

    if request.method == "POST":
        incident_code = (
            request.form.get("incident_code", "")
            .strip()
            .upper()
        )

        account_id = request.form.get(
            "account_id",
            type=int,
        )

        title = request.form.get(
            "title",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip() or None

        severity = request.form.get(
            "severity",
            "",
        ).strip()

        status = request.form.get(
            "status",
            "",
        ).strip()

        owner = request.form.get(
            "owner",
            "",
        ).strip() or None

        root_cause = request.form.get(
            "root_cause",
            "",
        ).strip() or None

        resolution = request.form.get(
            "resolution",
            "",
        ).strip() or None

        started_at_raw = request.form.get(
            "started_at",
            "",
        )

        resolved_at_raw = request.form.get(
            "resolved_at",
            "",
        )

        account = db.session.get(
            Account,
            account_id,
        ) if account_id else None

        if not incident_code:
            flash(
                "Incident Code is required.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if account is None or not account.is_active:
            flash(
                "Selected Account is invalid.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if not title:
            flash(
                "Title is required.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if severity not in SEVERITIES:
            flash(
                "Invalid Severity.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        if status not in STATUSES:
            flash(
                "Invalid Status.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        try:
            started_at = parse_datetime_local(
                started_at_raw
            )

            resolved_at = parse_datetime_local(
                resolved_at_raw
            )
        except ValueError:
            flash(
                "Invalid date or time value.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        incident.incident_code = incident_code
        incident.account_id = account_id
        incident.title = title
        incident.description = description
        incident.severity = severity
        incident.status = status
        incident.owner = owner
        incident.root_cause = root_cause
        incident.resolution = resolution
        incident.started_at = started_at
        incident.resolved_at = resolved_at
        incident.updated_at = db.func.now()

        try:
            attachment_file = request.files.get(
                "attachment"
            )

            save_incident_attachment(
                incident,
                attachment_file,
            )

            db.session.commit()

        except ValueError as exc:
            db.session.rollback()

            flash(
                str(exc),
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
                attachments=get_incident_attachments(
                    incident.id
                ),
            )

        except IntegrityError:
            db.session.rollback()

            flash(
                "Incident Code already exists.",
                "error",
            )

            return render_template(
                "incidents/form.html",
                incident=incident,
                accounts=accounts,
                severities=SEVERITIES,
                statuses=STATUSES,
            )

        flash(
            f"Incident {incident.incident_code} "
            "updated successfully.",
            "success",
        )

        return redirect(
            url_for("incidents.index")
        )

    return render_template(
        "incidents/form.html",
        incident=incident,
        accounts=accounts,
        severities=SEVERITIES,
        statuses=STATUSES,
        attachments=get_incident_attachments(
            incident.id
        ),
    )


@incidents_bp.route(
    "/<int:incident_id>/attachments/"
    "<int:attachment_id>/download"
)
@login_required
def download_attachment(
    incident_id,
    attachment_id,
):
    incident = db.get_or_404(
        Incident,
        incident_id,
    )

    attachment = db.get_or_404(
        Attachment,
        attachment_id,
    )

    if (
        attachment.entity_type != "incident"
        or attachment.entity_id != incident.id
    ):
        return (
            "Attachment does not belong "
            "to this Incident.",
            404,
        )

    incident_directory = (
        Path(current_app.config["UPLOAD_DIR"])
        / "incidents"
        / str(incident.id)
    )

    return send_from_directory(
        incident_directory,
        attachment.stored_filename,
        as_attachment=True,
        download_name=attachment.original_filename,
    )
