# P.I.S.S.
**P**rocedural<BR>
**I**nstruction<BR>
**S**equence<BR>
**S**tring<BR>
<BR>
P.I.S.S. is a system that allows for embedding context information or other function calls into strings, 
which are used to build Discord message(s) by **procedural**ly parsing the input **string** into a **sequence** of **Instruction**s.
This follows the formatting style notated below and is usable in either Message or Instruction contexts (guild only as of writing).


# Format
Inside string input, Instruction blocks can be embedded. These can contain a number of Instructions (see Instructions chapter), delimited by `;`.
These blocks can contribute to the string building by ending with an Instruction that returns a string-convertible piece of data.<BR>
An example: `Test that will be built using {A; B; C; D} into a Discord message.` becomes, 
            `Test that will be built using D into a Discord message.`
(given that Instructions A, B and C perform other actions than returning data).
You can recognize these data-only Instructions by their signature in the Instructions chapter,
as well as direct calls to memory entries with types convertible to `str`.

## Main text
Main text is parsed for instruction blocks by checking for opening characters `{`,
counting them and closing the block as soon as it has closed all the counted `{` characters using `}`.

### Symbols
- `{` Instruction block opening symbol. Must be closed with a `}`.
- `}` Instruction block closing symbol. Must first be opened with a `{`.
- `\` Escape symbol to use certain identifiers inside of strings. (to use `{` or `}` inside of text blocks, make sure to escape them!)


## Instruction Block
Contain instructions, separated by `;`. Multiple instructions, when chained together,
may only use statements that result in a value at the end of the instruction block.


# Instructions
The following instructions are listed in order of parsing.
If any input matches multiple signatures, the one higher up the list is matched first.<BR>

## Build
> Signature: **None**

Special Instruction created using text outside of Instruction block context.<BR>
Appends given text to the currently built output.

## Push
> Signature: `push(pingable: {0, 1, 2})`

Sends currently built text into Interaction channel. For given parameter `pingable`, determine who can have a notification ping:
- `0`: None
- `1`: The user the bot is replying to. Really only applicable when the Interaction context is that of a Message.
- `2`: `@everyone`, `@here`, roles, users
Pingable carries over all previous properties, so `2` also replies to the author.
Obviously cannot ping a role (or `@everyone` / `@here`) if the bot does not have the proper permissions.

## Random (Number)
> Signature:
> `rand(a: int, b: int)`
> `random(a: int, b: int)`

Generates a random number between `a` and `b` (both inclusive), where `a <= b` and both integers.

## Random (User)
> Signature:
> `tru(a: int, attr: {id, name, account, created_at, roles, mutual_guilds})`

For a given `a` (0-indexed), gets the corresponding attribute of a random user in the server's member list.
Repeatedly using the same value of `a` will retrieve information for the same user.
`a` may be negative, or larger than the size of the server as `a % member_count` is used. **Note: this means that for smaller servers, using too many identifiers, or using negatives, may retrieve the data of the same user.**

- `id`: The Snowflake user ID of the user. Ping them with `<@id>`, or use it for other purposes.
- `name`: Gets the user's display name.
- `account`: Gets the user's account name.
- `created_at`: Gets the ISO-formatted `(YYYY-MM-DD HH:MM)` creation date of the user, down to the minute.
- `roles`: the **number** of roles this user has.
- `mutual_guilds`: the **number** of guilds this user shares with the bot.

## Sleep
> Signature: `sleep(t: int | float)`

Sleeps execution for `t` seconds, where `0.5 <= t <= 3600` and is parsed either as a whole number 
or as a number `t = a.b` for `a` being an int of 0-4 digits, and `b` being an int with 1-2 digits (ex: `aaaa.bb`).

## Writing
> Signature: `writing(t: text)`

Executes the following text block while contributing to the '`x` is writing' for the channel.
Note that `t` is of type `text`, and not of type `code`, meaning that strings can be constructed inside of a `writing` block and sent using multiple `push` statements.
**Cannot use `writing` inside of a `writing` block.**

Example usage: `writing(This is sent after two seconds!{sleep(2)})`


## Choice
> Signature: `choice(*opt: see below)`

Non-deterministically picks one of the given text blocks and executes it in its place.
Text blocks specified as Python strings, seperated by `,`. Requires at least 2 options.
Example: `choice('a', "b with a \"", "{sleep(5)}")`. For opening and closing a string, either `"` or `'` may be used, just make sure to **escape** your symbol if you want to use it in text.

## Clear
> Signature: `clear()`

Removes currently built text, emptying out the buffer.

## Memory
> Signature: **None**

Special Instruction created by calling a memory variable at the **end** of an Instruction block. Inserts the variable's value as the built text.<BR>
Will fail at compile time if either
1. The memory entry does not exist
2. The entry does not have a compatible type.

The memory comes pre-filled with entries.

# Execution and Testing


