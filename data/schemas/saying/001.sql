BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS saying (
    id           INTEGER PRIMARY KEY,
    text         TEXT NOT NULL,
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,
    created_at   INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_saying_creation
ON saying (created_at, id);

--- Bookkeeping
UPDATE schema_versions
SET version = 1
WHERE name = saying

COMMIT;