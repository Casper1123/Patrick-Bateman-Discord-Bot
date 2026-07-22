from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.logger import LoggerConfiguration
from abstract import BotClient as _AbstractClient

class BotClient(_AbstractClient):
    def __init__(self, db: DataInterface, pref: PreferencesInterface, logger_config: LoggerConfiguration) -> None:
        super().__init__(db, pref, logger_config)

    async def setup_hook(self) -> None:
        # todo: Import Cogs here
        ...

        await super().setup_hook() # call to toolkit version.