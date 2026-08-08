import discord

from data.interfaces.autoreplies import GlobalTextAutoreplyInterface
from data.interfaces.fact import GlobalAdminFactInterface
from data.interfaces.moderation import GlobalAdminModerationInterface
from data.interfaces.other import LocalAdminDataInterface
from data.interfaces.pref import PreferencesInterface
from data.interfaces.saying import GlobalAdminSayingInterface
from discorduser.cogs.local.admin import LocalAdminCog
from discorduser.cogs.regular.ask import AskPatrick
from discorduser.cogs.regular.autoreply.letters import LetterAutoreplyCog
from discorduser.cogs.regular.autoreply.numbers import NumberAutoreplyCog
from discorduser.cogs.regular.autoreply.sayings import RandomAutoreplyCog
from discorduser.cogs.regular.autoreply.text import MessageContentAutoreplyCog
from discorduser.cogs.regular.facts import FactsCog
from discorduser.cogs.regular.fun import MainCommandsCog
from discorduser.cogs.regular.preferences import UserPreferenceCog
from discorduser.cogs.universal.autoreply import attach_cogs as attach_autoreply_cogs
from discorduser.cogs.universal.factmod import GlobalFactAdminCog, GlobalAdminCog
from discorduser.cogs.universal.saying import GlobalAdminSayingCog
from discorduser.cogs.utilities import ListenerCog
from configuration.logger import GlobalLoggerConfig, LocalLoggerConfig
from .abstract import BotClient as _AbstractClient
from configuration.global_config import CFG


class BotClient(_AbstractClient):
    def __init__(self, global_logger_config: GlobalLoggerConfig, local_logger_config: LocalLoggerConfig, autoreplies: GlobalTextAutoreplyInterface, fact: GlobalAdminFactInterface, mod: GlobalAdminModerationInterface, db: LocalAdminDataInterface, pref: PreferencesInterface, saying: GlobalAdminSayingInterface) -> None:
        super().__init__(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    async def setup_hook(self) -> None:
        # Util
        await self.add_cog(ListenerCog(self, self.logger))

        # Global
        await attach_autoreply_cogs(self, self.autoreplies, self.logger)
        await self.add_cog(GlobalFactAdminCog(self, self.fact, self.logger))
        await self.add_cog(GlobalAdminCog(self, self.fact, self.mod, self.db, self.logger))
        await self.add_cog(GlobalAdminSayingCog(self, self.saying, self.logger))

        # Local
        await self.add_cog(LocalAdminCog(self, self.fact, self.mod, self.pref, self.db, self.logger, self.local_logger))

        # Common
        # await self.add_cog(AskPatrick(self))
        await self.add_cog(FactsCog(self, self.fact))
        await self.add_cog(MainCommandsCog(self))
        await self.add_cog(UserPreferenceCog(self, self.pref))

        # Auto
        await self.add_cog(LetterAutoreplyCog(self, self.pref))
        await self.add_cog(NumberAutoreplyCog(self, self.pref))
        await self.add_cog(RandomAutoreplyCog(self, self.saying, self.pref))
        await self.add_cog(MessageContentAutoreplyCog(self, self.pref, self.autoreplies))

        # Finalize
        await super().setup_hook() # call to toolkit version.

        await self.tree.sync() # Attach created and added hooks to discord.
        await self.tree.sync(guild=discord.Object(id=CFG.GLOBAL_ADMIN_SERVER_ID))