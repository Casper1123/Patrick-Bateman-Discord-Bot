BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS pref_user (
    user_id INTEGER PRIMARY KEY,
    saying  INTEGER NOT NULL CHECK (saying IN (0, 1)),
    text    INTEGER NOT NULL CHECK (text IN (0, 1)),
    letter  INTEGER NOT NULL CHECK (letter IN (0, 1)),
    number  INTEGER NOT NULL CHECK (number IN (0, 1))
);

--- Can have many channels in same guild, so guild cannot be pk
CREATE TABLE IF NOT EXISTS pref_guild (
    id         INTEGER PRIMARY KEY,
    guild_id   INTEGER NOT NULL,
    channel_id INTEGER,
    saying  INTEGER NOT NULL CHECK (saying IN (0, 1)),
    text    INTEGER NOT NULL CHECK (text IN (0, 1)),
    letter  INTEGER NOT NULL CHECK (letter IN (0, 1)),
    number  INTEGER NOT NULL CHECK (number IN (0, 1))
);

CREATE UNIQUE INDEX idx_pref_guild_channel
ON pref_guild (guild_id, channel_id)
WHERE channel_id IS NOT NULL;

CREATE UNIQUE INDEX idx_pref_guild_all_channels
ON pref_guild (guild_id)
WHERE channel_id IS NULL;

--- Bookkeeping
INSERT INTO schema_versions (name, version)
VALUES ('pref', 1);

COMMIT;