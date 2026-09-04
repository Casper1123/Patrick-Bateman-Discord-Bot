BEGIN;

CREATE TABLE IF NOT EXISTS LocalFact (
    id           INTEGER PRIMARY KEY,
    text         TEXT NOT NULL,
    guild_id     INTEGER NOT NULL,
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,
    created_at   INTEGER NOT NULL
);

-- Efficiently retrieve facts belonging to a guild in creation order.
CREATE INDEX IF NOT EXISTS idx_localfact_guild_creation
ON LocalFact (guild_id, created_at, id);


CREATE TABLE IF NOT EXISTS GlobalFact (
    id           INTEGER PRIMARY KEY,
    text         TEXT NOT NULL,
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,
    created_at   INTEGER NOT NULL
);

-- Efficiently retrieve global facts in creation order.
CREATE INDEX IF NOT EXISTS idx_globalfact_creation
ON GlobalFact (created_at, id);

UPDATE SchemaVersions
SET Version = 1
WHERE SchemaName = fact

COMMIT;