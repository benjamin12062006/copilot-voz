CREATE TABLE app_storage_preferences (
    user_id TEXT PRIMARY KEY NOT NULL REFERENCES app_users(id),
    retention_limit INTEGER NOT NULL CHECK (retention_limit BETWEEN 1 AND 100)
);
