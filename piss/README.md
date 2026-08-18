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
Main text is not counted as a recursion for the recursion limit.

### Symbols
- `{` Instruction block opening symbol. Must be closed with a `}`.
- `}` Instruction block closing symbol. Must first be opened with a `{`.
- `\` Escape symbol. 


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

## Memory
> Signature: **None**

Special Instruction created by calling a memory variable at the **end** of an Instruction block. Inserts the variable's value as the built text.<BR>
Will fail at compile time if either
1. The memory entry does not exist
2. The entry does not have a compatible type.



# Execution and Testing


