BEGIN;

CREATE TABLE IF NOT EXISTS aliases (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    rate         INTEGER NOT NULL CHECK (rate BETWEEN 1 AND 256),
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS triggers (
    id           INTEGER PRIMARY KEY,
    alias_id     INTEGER NOT NULL,
    type         TEXT NOT NULL,
    data         TEXT NOT NULL,
    rate         INTEGER CHECK (rate BETWEEN 1 AND 256),
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,

    FOREIGN KEY (alias_id)
        REFERENCES aliases (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_triggers_alias
ON triggers (alias_id);

CREATE TABLE IF NOT EXISTS replies (
    id           INTEGER PRIMARY KEY,
    alias_id     INTEGER NOT NULL,
    type         TEXT NOT NULL,
    data         TEXT NOT NULL,
    weight       INTEGER NOT NULL CHECK (weight >= 0),
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,

    FOREIGN KEY (alias_id)
        REFERENCES aliases (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_replies_alias
ON replies (alias_id);

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('autoreplies', 1);

COMMIT;