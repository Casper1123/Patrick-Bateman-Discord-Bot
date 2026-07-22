# What?
Okay so you know how you can import things in Python right.<BR>
Yeah so, I wanted to import the cogs into the bot (duuh, obviously) so I can attach the commands and stuff.<BR>
However, I ran into an issue; I also want some universally used tools attached to the bot. If I were to import the bot itself to gain access to those Bot-class bound tools, I get circular imports.
Solution: Have one class that has the tools, and then inherit from it to attach the cogs. This way, both the actual bot that imports the cogs, as well as the cogs themselves, can use one class I use for general toolkit and stuff.
You know, as the `__init__/BotClient` inherits from `abstract/BotClient` both are BotClients just one has cogs attached. `__init__` contains the full implementation as that is implied by importing `discorduser/user`, meanwhile importing `discorduser/user/abstract` proves you want something more specific.