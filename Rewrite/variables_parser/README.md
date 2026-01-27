# Variables Parser
Contains files on the uuuh.. variables parser.<BR>
The old version used an in-string replacer. This time, the goal is to make a minor sandboxed environment for more options (like allowing sending multiple messages).


## Variables
Placed inside of {}. these symbols can be escaped by prepending with \<BR>
When one has multiple non-substitute calls in one variable block, they can be separated by ;, if not prepended by \
### In-place
In-placed variables may never be named equal to one of these registered values. This project will assume that the bot is used in Guild context.


'This is regular text {guild.id}{push}{sleep(5)}'
'{a = 5; b = 5; c = a*b; c}'