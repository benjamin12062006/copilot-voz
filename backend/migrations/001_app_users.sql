CREATE TABLE app_users (
    id TEXT PRIMARY KEY NOT NULL,
    identity_issuer TEXT NOT NULL,
    identity_subject TEXT NOT NULL,
    email TEXT,
    display_name TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT app_users_identity_unique UNIQUE (identity_issuer, identity_subject)
);
