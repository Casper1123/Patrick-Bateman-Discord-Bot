PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS LocalFacts (
    ID          INTEGER PRIMARY KEY,
    Text        TEXT NOT NULL,
    GuildID     INTEGER NOT NULL,
    ModifiedBy  INTEGER NOT NULL,
    ModifiedAt  INTEGER NOT NULL,
    CreatedAt   INTEGER NOT NULL
);

-- Efficiently retrieve facts belonging to a guild in creation order.
CREATE INDEX IF NOT EXISTS idx_localfacts_guild_creation
ON LocalFacts (GuildID, CreatedAt, ID);


CREATE TABLE IF NOT EXISTS GlobalFacts (
    ID          INTEGER PRIMARY KEY,
    Text        TEXT NOT NULL,
    ModifiedBy  INTEGER NOT NULL,
    ModifiedAt  INTEGER NOT NULL,
    CreatedAt   INTEGER NOT NULL
);

-- Efficiently retrieve global facts in creation order.
CREATE INDEX IF NOT EXISTS idx_globalfacts_creation
ON GlobalFacts (CreatedAt, ID);