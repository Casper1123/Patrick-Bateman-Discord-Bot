BEGIN;

--- Modifications

--- Bookkeeping
UPDATE SchemaVersions
SET Version = 1
WHERE SchemaName = moderation

COMMIT;