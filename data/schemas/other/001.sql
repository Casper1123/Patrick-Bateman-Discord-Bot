BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS local_log_channels (
    guild_id   INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL
);

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('other', 1);

COMMIT;