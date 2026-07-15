BEGIN;

CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'member'
        CHECK (role IN ('admin', 'manager', 'member', 'viewer')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_code VARCHAR(100) NOT NULL UNIQUE,
    account_id BIGINT NOT NULL
        REFERENCES accounts(id) ON DELETE RESTRICT,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(50) NOT NULL DEFAULT 'Medium'
        CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Open'
        CHECK (status IN (
            'Open',
            'Investigating',
            'Monitoring',
            'Resolved',
            'Closed'
        )),
    owner VARCHAR(255),
    root_cause TEXT,
    resolution TEXT,
    started_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE change_requests (
    id BIGSERIAL PRIMARY KEY,
    change_code VARCHAR(100) NOT NULL UNIQUE,
    account_id BIGINT NOT NULL
        REFERENCES accounts(id) ON DELETE RESTRICT,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    change_type VARCHAR(100),
    risk_level VARCHAR(50) DEFAULT 'Medium'
        CHECK (risk_level IN ('Critical', 'High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Draft'
        CHECK (status IN (
            'Draft',
            'Planned',
            'Pending Approval',
            'Approved',
            'In Progress',
            'Completed',
            'Failed',
            'Cancelled'
        )),
    owner VARCHAR(255),
    implementation_plan TEXT,
    rollback_plan TEXT,
    validation_plan TEXT,
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE operation_plans (
    id BIGSERIAL PRIMARY KEY,
    plan_code VARCHAR(100) NOT NULL UNIQUE,
    account_id BIGINT NOT NULL
        REFERENCES accounts(id) ON DELETE RESTRICT,
    name VARCHAR(500) NOT NULL,
    plan_type VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Planned'
        CHECK (status IN (
            'Draft',
            'Planned',
            'In Progress',
            'Completed',
            'Cancelled'
        )),
    owner VARCHAR(255),
    plan_date DATE,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE plan_items (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL
        REFERENCES operation_plans(id) ON DELETE CASCADE,
    check_id VARCHAR(100),
    check_type VARCHAR(100),
    check_item TEXT NOT NULL,
    owner VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'Planned'
        CHECK (status IN (
            'Planned',
            'In Progress',
            'Completed',
            'Blocked',
            'Cancelled'
        )),
    result_notes TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL
        CHECK (entity_type IN (
            'incident',
            'change_request',
            'operation_plan',
            'plan_item'
        )),
    entity_id BIGINT NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    mime_type VARCHAR(255),
    file_size BIGINT,
    uploaded_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL
        CHECK (entity_type IN (
            'incident',
            'change_request',
            'operation_plan',
            'plan_item'
        )),
    entity_id BIGINT NOT NULL,
    comment_text TEXT NOT NULL,
    created_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_incidents_account
    ON incidents(account_id);

CREATE INDEX idx_incidents_status
    ON incidents(status);

CREATE INDEX idx_incidents_severity
    ON incidents(severity);

CREATE INDEX idx_change_requests_account
    ON change_requests(account_id);

CREATE INDEX idx_change_requests_status
    ON change_requests(status);

CREATE INDEX idx_operation_plans_account
    ON operation_plans(account_id);

CREATE INDEX idx_operation_plans_type
    ON operation_plans(plan_type);

CREATE INDEX idx_plan_items_plan
    ON plan_items(plan_id);

CREATE INDEX idx_plan_items_status
    ON plan_items(status);

CREATE INDEX idx_attachments_entity
    ON attachments(entity_type, entity_id);

CREATE INDEX idx_comments_entity
    ON comments(entity_type, entity_id);

CREATE INDEX idx_audit_logs_entity
    ON audit_logs(entity_type, entity_id);

CREATE INDEX idx_audit_logs_created
    ON audit_logs(created_at);

INSERT INTO schema_migrations (version)
VALUES ('001_initial_schema');

COMMIT;
