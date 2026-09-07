BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS local_log_channels (
    guild_id   INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL,
);

--- Bookkeeping
UPDATE schema_versions
SET version = 1
WHERE name = other

COMMIT;