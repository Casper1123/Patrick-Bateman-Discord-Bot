# Loggers
Loggers are an injected dependency that are called on certain loggable actions to log to console and/or targetted discord channels.
## Configuration
JSON-maintained logging configuration to configure what gets logged where. Must be complete otherwise the application will not start up (as to make sure all logging happens properly).

## Channel Logging guarantee
To guarantee that important things can be logged to their corresponding channel, if something is misconfigured the application closes immediately. This is done to not lose any information, and is easy to see represented on Discord as the application goes offline.


## Why an injected dependency
As of time of writing, `BotClient`'s abstract variation requires knowing about the logger for the on-tree-error logic.
This however, means that the Logger cannot perform important operations *as* the client.