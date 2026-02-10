Database stuff has to go here.
Store global, local, and configuration data if possible.
Work out properly. Make sure to guarantee not leaking stuff.

Also like, don't forget about making a tool that translates previously added data into new db okay.




# Facts:
Each entry has:
- AuthorID (keep track of last modified user ID)
- Text
- GuildID
- ModifiedAt (UNIX Timestamp) (to order for indices)