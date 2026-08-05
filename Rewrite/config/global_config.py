# File contains a bunch of universally used datapoints.
# Leaving this here, implemented this way, until I find a better solution.

# Global
GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: make this a json config thing
REPLY_WEIGHT_UPPER_BOUND: int = 1024


# Local
    # Url to where information on debugger output can be found.
DEBUGGER_OUTPUT_WIKI_URL: str = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'
FACT_COUNT_MAXIMUM: int = 50
FACT_CHAR_LIMIT: int = 256

PREVIEW_COOLDOWN_SECONDS: float = 5.0
DELETE_COOLDOWN_SECONDS: float = 5.0
EDIT_COOLDOWN_SECONDS: float = 5.0
ADD_COOLDOWN_SECONDS: float = 5.0

# Regular
FACT_COOLDOWN: float = 1.0 # Seconds

# Autoreply
SAYING_PROBABILIY: int = 300 # 1 / probability listed here, per message.

# Other
EPHEMERAL_DESCRIPTION: str = 'Hide this command from other users.'