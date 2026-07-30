from Rewrite.data.interfaces.fact import FactInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.logger import GlobalLoggerConfig
from abstract import BotClient as _AbstractClient

class BotClient(_AbstractClient):
    def __init__(self, db: FactInterface, pref: PreferencesInterface, logger_config: GlobalLoggerConfig) -> None:
        super().__init__(db, pref, logger_config)

    async def setup_hook(self) -> None:
        # todo: Import Cogs here
        ...

        await super().setup_hook() # call to toolkit version.