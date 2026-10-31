CREATE TABLE app_voice_preferences (
    user_id TEXT PRIMARY KEY NOT NULL REFERENCES app_users(id),
    auto_read_mode TEXT NOT NULL CHECK (auto_read_mode IN ('off', 'agent', 'all'))
);
