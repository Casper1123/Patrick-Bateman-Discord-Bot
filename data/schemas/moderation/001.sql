BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS banned_guilds (
    id           INTEGER PRIMARY KEY,
    reason       TEXT,
    banned_by    INTEGER NOT NULL,
    since        INTEGER NOT NULL,
);

CREATE TABLE IF NOT EXISTS banned_users (
    id           INTEGER PRIMARY KEY,
    reason       TEXT,
    banned_by    INTEGER NOT NULL,
    since        INTEGER NOT NULL,
);

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('moderation', 1);

COMMIT;