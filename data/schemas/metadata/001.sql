-- Required to maintain easy migration to other versions. Base information for DB files.
CREATE TABLE IF NOT EXISTS SchemaVersions (
    SchemaName TEXT PRIMARY KEY,
    Version    INTEGER NOT NULL
);

PRAGMA user_version = 1;