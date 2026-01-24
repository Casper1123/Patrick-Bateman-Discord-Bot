# Variables Parser
Contains files on the uuuh.. variables parser.<BR>
The old version used an in-string replacer. This time, the goal is to make a minor sandboxed environment for more options (like allowing sending multiple messages).


## Variables
Placed inside of {}. these symbols can be escaped by prepending with {
### In-place
In-placed variables may never be named equal to one of these registered values. This project will assume that the bot is used in Guild context.
