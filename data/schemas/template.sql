--- Standard
BEGIN;

--- Modifications

--- Bookkeeping
UPDATE SchemaVersions
SET Version = ?
WHERE SchemaName = ?

COMMIT;



--- Metadata
BEGIN;

--- Modifications

--- Bookkeeping
PRAGMA user_version = ?

COMMIT;