BEGIN;

PRAGMA foreign_keys = ON

-- Required to maintain easy migration to other versions. Base information for DB files.
CREATE TABLE IF NOT EXISTS schema_versions (
    name    TEXT PRIMARY KEY,
    version INTEGER NOT NULL
);

PRAGMA user_version = 1;

COMMIT;