Database stuff has to go here.
Store global, local, and configuration data if possible.
Work out properly. Make sure to guarantee not leaking stuff.

Also like, don't forget about making a tool that translates previously added data into new db okay.


db:
`getFact(guild_id: int, index: bool | None) -> str`
> Gets a fact. If given an index, will raise an IndexError
getFactCount(guild_id: int | None) -> int
> Gets the number of facts of the given guild_id. If the id is none, it gets global instead.