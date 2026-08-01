from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface
from Rewrite.data.interfaces.fact import FactInterface, GlobalAdminFactInterface
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface
from Rewrite.data.interfaces.other import GlobalAdminDataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface
from Rewrite.discorduser.logger import GlobalLoggerConfig, LocalLoggerConfig, GlobalLogger
from Rewrite.discorduser.logger.local import LocalLogger
from abstract import BotClient as _AbstractClient

class BotClient(_AbstractClient):
    def __init__(self, global_logger_config: GlobalLoggerConfig, local_logger_config: LocalLoggerConfig, autoreplies: GlobalTextAutorepliesInterface, fact: GlobalAdminFactInterface, mod: GlobalAdminModerationInterface, db: GlobalAdminDataInterface, pref: PreferencesInterface, saying: GlobalAdminSayingInterface) -> None:
        super().__init__(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    async def setup_hook(self) -> None:
        # todo: Import Cogs here
        ...

        await super().setup_hook() # call to toolkit version.