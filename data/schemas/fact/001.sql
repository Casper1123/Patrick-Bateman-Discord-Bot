BEGIN;

CREATE TABLE IF NOT EXISTS localfact (
    id           INTEGER PRIMARY KEY,
    text         TEXT NOT NULL,
    guild_id     INTEGER NOT NULL,
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,
    created_at   INTEGER NOT NULL
);

-- Efficiently retrieve facts belonging to a guild in creation order.
CREATE INDEX IF NOT EXISTS idx_localfact_guild_creation
ON localfact (guild_id, created_at, id);


CREATE TABLE IF NOT EXISTS globalfact (
    id           INTEGER PRIMARY KEY,
    text         TEXT NOT NULL,
    modified_by  INTEGER NOT NULL,
    modified_at  INTEGER NOT NULL,
    created_at   INTEGER NOT NULL
);

-- Efficiently retrieve global facts in creation order.
CREATE INDEX IF NOT EXISTS idx_globalfact_creation
ON globalfact (created_at, id);

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('fact', 1);

COMMIT;