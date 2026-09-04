This is here such that the folder exists in git.
Each schema has its own folder.

# standard
BEGIN;

Alterations
> CREATE TABLE, ALTER TABLE, CREATE INDEX, INSERT, UPDATE, DELETE supported
> others might be finnicky

Bookkeeping
> UPDATE SchemaVersions
> SET Version = ?
> WHERE SchemaName = ?

COMMIT;