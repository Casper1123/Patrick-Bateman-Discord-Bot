Refer to [the documentation](https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki/The-Variable-system) 
for detailed information.

## Regular Variables <BR>
### User: <BR>
>user.account<BR>
>user.name<BR>
>user.id

### Channel:
>channel.name<BR>
>channel.id

### Guild:
>guild.name<BR>
>guild.name<BR>
>owner:
> >owner.account<BR>
> >owner.name<BR>
> >owner.id<BR>

### Self:
>self.name<BR>
>self.nick<BR>
>self.id

### General:
>{enter} or `\n`<BR>
>total_facts<BR>
>global_facts<BR>
>local_facts

## Command Variables <BR>
### rand:
The number generated is between the lower and upper, inclusive. <BR>
Space mandatory. <BR>
`{rand(lower, upper)}` <BR>`{rand(0, 1)}`

### choice:
Picks a random option of the strings given. <BR>
What's important to know is that these choices can have variables. <BR>
`{choice:"option",...}` <BR>
`{choice:"option 1","option 2 with {variable}"}`

### fact:
Inserts a stored fact. Index must be reachable in the given server. <BR>
Takes in numbers or other variables as parameters, but requires a number as a result. <BR>
`{fact(index)}` <BR> `{fact(0)}` <BR> `{fact(rand(0, global_facts))}` takes a random fact available.

### tru (True Random User):
Access semi-random server member information. This one's a little more complicated. <BR>
Syntax: `tru_[op]([num])`, where `[op]` is the operation or information, and `[num]` is the index. <BR>
When preparing the fact, each user is given their own randomized index, to be accessed with `[num]`.
This means that using `tru_[op](0)` repeatedly, will always give the same randomized user. <BR>
Supported operations: `acc`, `name`, `id`. <BR>
**Warning:** 
>If a number is too large, the indexing will wrap around and thus using too many different tru-indices might result in the same user.
You can't exactly have unlimited users in a server, can you.