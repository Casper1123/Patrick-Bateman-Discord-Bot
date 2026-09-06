This folder contains implementation required database schemas, where `001.sql` is the first version, and any higher versions are migrations applied on top of it (in order).
Versions are tracked with a universal metadata table for each database file to enforce compatibility for multiple files, but also multiple schemas per file.
For this purpose, `metadata` is seperately applied and migrated, whose version is tracked with the `user_version` variable. This way `metadata` can also be updated to ensure that each file can get the features they need for setup and version control.

Target version specified by inheritor constructor. Migration version set by migration patch. these MUST be strictly linear (so no skipping versions).