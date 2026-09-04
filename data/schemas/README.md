Contains schemas for each schema name required.
Schema `001` is the base schema, all others are patches applied on top.
Each ends with their own version definition, available by loading metadata.

# standard
BEGIN;

Alterations
> CREATE TABLE, ALTER TABLE, CREATE INDEX, INSERT, UPDATE, DELETE supported
> others might be finnicky

Bookkeeping
```sql
UPDATE SchemaVersions
SET Version = ?
WHERE SchemaName = ?
```

COMMIT;