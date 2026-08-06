import socket
import sys
from typing import Literal

import aiohttp
import discord
from discord import app_commands, Colour, Interaction
from discord.app_commands import CommandOnCooldown
from discord.ext import commands

from data.interfaces.autoreplies import GlobalTextAutorepliesInterface
from data.interfaces.fact import GlobalAdminFactInterface
from data.interfaces.moderation import GlobalAdminModerationInterface
from data.interfaces.other import LocalAdminDataInterface
from data.interfaces.pref import PreferencesInterface
from data.interfaces.saying import GlobalAdminSayingInterface
from configuration.logger import LocalLoggerConfig, GlobalLoggerConfig
from discorduser.logger import GlobalLogger, LoggableErrorContext
from discorduser.logger.errors import ErrorSource, ListenerErrorContext, AppCommandErrorContext, \
    AutocompleteErrorContext
from discorduser.logger.local import LocalLogger
from utilities.exceptions import CustomDiscordException, ErrorTooltip


class BotClient(commands.Bot):
    """
    Bot-inherited class with toolkit installed.
    WARNING: DOES NOT CONTAIN COGS.
    """
    def __init__(self, global_logger_config: GlobalLoggerConfig, local_logger_config: LocalLoggerConfig, autoreplies: GlobalTextAutorepliesInterface, fact: GlobalAdminFactInterface, mod: GlobalAdminModerationInterface, db: LocalAdminDataInterface, pref: PreferencesInterface, saying: GlobalAdminSayingInterface) -> None:
        self.logger: GlobalLogger = GlobalLogger(self, global_logger_config)
        self.local_logger: LocalLogger = LocalLogger(local_logger_config, db)
        self.autoreplies: GlobalTextAutorepliesInterface = autoreplies
        self.fact: GlobalAdminFactInterface = fact
        self.mod: GlobalAdminModerationInterface = mod
        self.db: LocalAdminDataInterface = db
        self.pref: PreferencesInterface = pref
        self.saying: GlobalAdminSayingInterface = saying

        intents = discord.Intents.default()
        intents.message_content = True # Required for autoreplies
        intents.members = True
        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

        async def on_error(event, *args, **kwargs):
            error = sys.exc_info()[1]
            if error is None:
                return
            if not isinstance(error, Exception):
                raise error

            # todo: parse params based on given event.
            await self.handle_exception(error_context=ListenerErrorContext(
                error=error, event=event, params='[]'
            ))

        self.on_error = on_error

    # region error-handling
    async def setup_hook(self) -> None:
        async def on_tree_error(interaction: Interaction, error: app_commands.AppCommandError):
            try:
                await interaction.response.defer(ephemeral=True, thinking=False) # noqa
            except Exception: # noqa Shoddy attempt at hiding the error from users. todo: find better solution
                pass
            # handle exceptions
            finally:
                await self.handle_exception(AppCommandErrorContext(error=error, interaction=interaction))
        # fixme: solution: decorate autocompletes
        self.tree.on_error = on_tree_error


    async def handle_exception(self, error_context: LoggableErrorContext) -> None:
        # TODO: FIXME: Holy shit holy fucking shitty shit do NOT log Autocomplete errors they will SPAM EVERYTHING
        if isinstance(error_context, AutocompleteErrorContext):
            error_context.log = False # FUUUUUCK I gotta find a timeout for this or a reason to mute it. Cool the tech exists, but now what.

        if error_context.log:
            await self.logger.error(error_context)

        if isinstance(error_context, AppCommandErrorContext):
            await error_context.interaction.edit_original_response(embed=error_context.error.as_embed())


    # endregion

    async def user_feedback(self, interaction: Interaction | discord.Message, title: str = None, desc: str = None, ephemeral: bool = False) -> None: # noqa
        """
        Sends the following title and (optional) description in a standardized embed to the user.
        :param interaction: Interaction or Message to reply to.
        :param title: Title of the embed.
        :param desc: Text body of the embed.
        :param ephemeral: If Interaction, ephemeral?
        """
        e = discord.Embed(title=title, description=desc, colour=Colour.blue())
        if isinstance(interaction, Interaction):
            try:
                await interaction.response.send_message(embed=e, ephemeral=ephemeral) # noqa
            except discord.InteractionResponded:
                await interaction.edit_original_response(embed=e) # ephemeral not supported.
        else:
            await interaction.reply(embed=e, mention_author=False)
