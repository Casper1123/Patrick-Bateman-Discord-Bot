### *Short little legal notice or I get scared*

*Fyi I don't actually own the name or IP Patrick Bateman. If, for copyright reasons, this name has to go I will change
it asap.*

# Patrick Bateman - the Discord Bot

Patrick Bateman is.. a discord bot. Woah, who would've thought (as if it doesn't say so right there huh).
Patrick is somewhat of a soft-chatbot that you can ask for facts, who will reply to things, as well as many other
things. <BR>
Below will be a list of functionality, as well as what's available to administrators. Yes, I made things for
administrators to have fun with. Let a lad be bored in his free time okay. <BR>
<BR>
**The bot's local contents lie outside of my control as of right now and I swear if I have to implement moderation for
that I'm going to be very angry.** <BR>
About that, global contents like autoreplies, random things Patrick can say, or global facts, are added by me and a
friend. <BR>
This is however not including the local facts, which we of course didn't write.

## Invite Link

[Click here to invite a hosted version of Patrick Bateman to your discord server.](https://discord.com/oauth2/authorize?client_id=974290109186867260) <BR>
Permissions rundown: <BR>

- View Channels - Seems pretty obvious.<BR>
- Manage Nicknames - Currently unused, but might be used for a future *optional* feature.<BR>
- Send Messages - Required to interact with things. <BR>
- Send Messages in Threads - The same. <BR>
- Embed Links - Required to properly reply to messages. <BR>
- Attach Files - Required for administrative features and some replies. <BR>
- Read Message History - Required to interact with things. <BR>
- Add Reactions - For future feature possibilities.

## Features

What makes Patrick worth inviting / funny? Honestly, that's a good question. <BR>
Sometimes I wonder that too. <BR>
Anyways, Patrick comes with a couple of commands and a couple of passive features. These currently cannot be configured
as of time of writing. <BR>
Let's go through the commands one-by-one.

## Commands

### /ask (question)

*Can also be accessed by messaging 'ask @patrick {question}' into the chat*
Replies to the given question with a yes or a no. Most of the time. <BR>
There's some surprises in here.

### /chinesenukelaunchcodes

速度与激情早上好中国现在我有冰激淋 我很喜欢冰激淋但是《速度与激情9》比冰激淋……🍦

### /fact (index)

Gives a random fa
ct to the user. More information will be down below. <BR>
The optional parameter 'index' will allow you to select a specific one.

### /fact_index

Displays some information regarding the stored amount of facts.

### /sex

Yeah, no.

### /throwback

Tries to reply to a random message sent in the channels entire history. <BR>
Fun to read back a little for nostalgia purposes.

### /throwitback

Learn to type please.

## Automatic, in the background, features.

### Incrementation

If the message is only a single letter, or the first thing in a message is a number, Patrick will reply with that thing
incremented by one.

### Content Replier

If a message contains a certain piece of text, Patrick might reply something to it.

# Administrative tools to have fun with.

Administrative users get access to the /admin subcommands. <BR>
These can be used to add your own facts for Patrick to tell. <BR>
These work only in the server you add them, and there is both a fact count and character limit.

### /admin index

Gives all the 'local' (specific to this server) facts in a file for you to quickly read.

### /admin add (fact)

Adds a fact for this server only. Can use [variables](https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki).

### /admin edit (index) (fact)

Edits a local fact based on index. Comes with a decently handy index-previewer.

### /admin remove (index)

Removes a local fact based on index. Has the same previewer als /edit.

### /admin help

Gives a large hidden message displaying some documentation you can also
find [here](https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki)

### /admin preview (fact)

Shows you a preview of how your fact would be processed. Useful for testing
out [variables](https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki).

# Extra information for people who want to host their own Patrick

If you're looking to host this bot, there's a couple extra sets of commands and config you're looking at. <BR>
First of all, you'd need to create a discord application to set up an application account and get a bot token. <BR>
Secondly, you'd need to set up the constants.json file in the /json_files/ folder properly.
This is going to need some additional information to get the bot fully up and running. <BR>
The rest should be pretty obvious to one who knows how to host a bot. Otherwise, I'm willing to share my limited
knowledge (as you can see from my ass programming style) or you can find things online. <BR>
Happy Patricking!