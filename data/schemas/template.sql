--- Standard
BEGIN;

--- Modifications

--- Bookkeeping
UPDATE schema_versions
SET version = ?
WHERE name = ?

COMMIT;



--- Metadata
BEGIN;

--- Modifications

--- Bookkeeping
PRAGMA user_version = ?

COMMIT;