from flask_login import UserMixin

from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    role = db.Column(db.String(50), nullable=False, default="member")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    @property
    def active(self):
        return self.is_active


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.BigInteger, primary_key=True)

    code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    name = db.Column(
        db.String(255),
        nullable=False,
    )

    description = db.Column(db.Text)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

class OperationPlan(db.Model):
    __tablename__ = "operation_plans"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    plan_code = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    account_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "accounts.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    name = db.Column(
        db.String(500),
        nullable=False,
    )

    plan_type = db.Column(
        db.String(100),
        nullable=False,
    )

    description = db.Column(
        db.Text,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Planned",
    )

    owner = db.Column(
        db.String(255),
    )

    plan_date = db.Column(
        db.Date,
    )

    created_by = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    account = db.relationship(
        "Account",
        foreign_keys=[account_id],
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
    )



class PlanItem(db.Model):
    __tablename__ = "plan_items"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    plan_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "operation_plans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    check_id = db.Column(
        db.String(100),
    )

    check_type = db.Column(
        db.String(100),
    )

    check_item = db.Column(
        db.Text,
        nullable=False,
    )

    owner = db.Column(
        db.String(255),
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Planned",
    )

    result_notes = db.Column(
        db.Text,
    )

    sort_order = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    plan = db.relationship(
        "OperationPlan",
        foreign_keys=[plan_id],
    )


class ChangeRequest(db.Model):
    __tablename__ = "change_requests"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    change_code = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    account_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "accounts.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    title = db.Column(
        db.String(500),
        nullable=False,
    )

    description = db.Column(db.Text)

    change_type = db.Column(
        db.String(100),
    )

    risk_level = db.Column(
        db.String(50),
        default="Medium",
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Draft",
    )

    owner = db.Column(
        db.String(255),
    )

    implementation_plan = db.Column(db.Text)

    rollback_plan = db.Column(db.Text)

    validation_plan = db.Column(db.Text)

    scheduled_at = db.Column(
        db.DateTime(timezone=True),
    )

    completed_at = db.Column(
        db.DateTime(timezone=True),
    )

    created_by = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    account = db.relationship(
        "Account",
        foreign_keys=[account_id],
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
    )


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.BigInteger, primary_key=True)

    incident_code = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    account_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "accounts.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    title = db.Column(
        db.String(500),
        nullable=False,
    )

    description = db.Column(db.Text)

    severity = db.Column(
        db.String(50),
        nullable=False,
        default="Medium",
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Open",
    )

    owner = db.Column(db.String(255))

    root_cause = db.Column(db.Text)

    resolution = db.Column(db.Text)

    started_at = db.Column(
        db.DateTime(timezone=True)
    )

    resolved_at = db.Column(
        db.DateTime(timezone=True)
    )

    created_by = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    account = db.relationship(
        "Account",
        foreign_keys=[account_id],
    )

    creator = db.relationship(
        "User",
        foreign_keys=[created_by],
    )

class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    entity_type = db.Column(
        db.String(50),
        nullable=False,
    )

    entity_id = db.Column(
        db.BigInteger,
        nullable=False,
    )

    original_filename = db.Column(
        db.String(500),
        nullable=False,
    )

    stored_filename = db.Column(
        db.String(500),
        nullable=False,
    )

    file_path = db.Column(
        db.Text,
        nullable=False,
    )

    mime_type = db.Column(
        db.String(255),
    )

    file_size = db.Column(
        db.BigInteger,
    )

    uploaded_by = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    uploader = db.relationship(
        "User",
        foreign_keys=[uploaded_by],
    )
