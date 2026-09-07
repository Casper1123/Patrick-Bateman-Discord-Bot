BEGIN;

--- Modifications

--- Bookkeeping
UPDATE schema_versions
SET version = 1
WHERE name = moderation

COMMIT;