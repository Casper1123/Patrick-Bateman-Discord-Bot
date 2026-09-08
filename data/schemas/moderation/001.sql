BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS banned_guilds (
    guild_id           INTEGER PRIMARY KEY,
    reason       TEXT,
    banned_by    INTEGER NOT NULL,
    since        INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS banned_users (
    user_id           INTEGER PRIMARY KEY,
    reason       TEXT,
    banned_by    INTEGER NOT NULL,
    since        INTEGER NOT NULL
);

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('moderation', 1);

COMMIT;