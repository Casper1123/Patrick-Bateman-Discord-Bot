BEGIN;

--- Modifications
CREATE TABLE IF NOT EXISTS pref_user (
    user_id INTEGER PRIMARY KEY,
    saying  BIT NOT NULL,
    text    BIT NOT NULL,
    letter  BIT NOT NULL,
    number  BIT NOT NULL,
);

--- Can have many channels in same guild, so guild cannot be pk
CREATE TABLE IF NOT EXISTS pref_guild (
    id         INTEGER PRIMARY KEY
    guild_id   INTEGER NOT NULL,
    channel_id INTEGER,
    saying     BIT NOT NULL,
    text       BIT NOT NULL,
    letter     BIT NOT NULL,
    number     BIT NOT NULL,
);

CREATE INDEX IF NOT EXISTS idx_pref_guild_channel
ON pref_guild (guild_id, channel_id, id);

--- Bookkeeping
UPDATE schema_versions
SET version = 1
WHERE name = pref

COMMIT;