This folder contains implementation required database schemas, where `001.sql` is the first version, and any higher versions are migrations applied on top of it (in order).
Versions are tracked with a universal metadata table for each database file to enforce compatibility for multiple files, but also multiple schemas per file.
For this purpose, `metadata` is seperately applied and migrated, whose version is tracked with the `user_version` variable. This way `metadata` can also be updated to ensure that each file can get the features they need for setup and version control.

Target version specified by inheritor constructor. Migration version set by migration patch. these MUST be strictly linear (so no skipping versions).

# Slop disclosure
Unfortunately I'm inexperienced, and I used LLMs with limited project context to help me set up the schemas.
Every line audited by me, only copy-pasted if I understood and approved (hence why the alignment of the attribute types in the schemas, though I'll admit it looks good), but usually something more basic was shaped into what it needed to be.
Idk if I have to explain that I took courses on database design I just did not know the sql syntax or usage for implementation purposes.