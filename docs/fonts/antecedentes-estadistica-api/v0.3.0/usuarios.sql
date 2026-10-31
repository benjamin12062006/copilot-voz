-- Equivalente histórico de migrations/001_create_app_users.sql.
CREATE TABLE app_users (
  id TEXT PRIMARY KEY NOT NULL,
  identity_issuer TEXT NOT NULL CHECK (length(identity_issuer) > 0),
  identity_subject TEXT NOT NULL CHECK (length(identity_subject) > 0),
  email TEXT,
  display_name TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (identity_issuer, identity_subject)
);
