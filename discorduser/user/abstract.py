import socket

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
from discorduser.logger import GlobalLogger
from discorduser.logger.local import LocalLogger
from piss import InstructionParseError
from utilities.exceptions import CustomDiscordException, ErrorTooltip

UNLOGGED_EXCEPTION_TYPES = [InstructionParseError.__name__, CommandOnCooldown.__name__] # using __name__ to ensure that when I change the class names this updates.


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

    async def setup_hook(self) -> None:
        async def on_tree_error(interaction: Interaction, error: app_commands.AppCommandError):
            try:
                if (True):  # todo: config to make uncaught public errors hidden or not
                    await interaction.response.defer(ephemeral=True, thinking=False) # noqa
            except Exception: # noqa Shoddy attempt at hiding the error from users. todo: find better solution
                pass
            # handle exceptions
            finally:
                if (isinstance(error, aiohttp.client_exceptions.ClientConnectorDNSError)
                        or isinstance(error, socket.gaierror)):
                    return # Skip 'connection lost' exceptions, also removing them from the logging.
                    # Idk why, but for some reason my host device seems to lose connection at unknown intervals for short periods of time.
                    # So this is temporary glue fix.
                if isinstance(error, CommandOnCooldown):
                    log = type(error).__name__ not in UNLOGGED_EXCEPTION_TYPES
                    error = CustomDiscordException(message=f'Command on cooldown ({error.cooldown}s), try again in **{error.retry_after}s**.', error_type='Command on cooldown.', tooltip=ErrorTooltip.NONE)
                elif not isinstance(error, CustomDiscordException):
                    log = type(error).__name__ not in UNLOGGED_EXCEPTION_TYPES
                    error: CustomDiscordException = CustomDiscordException(cause=error, error_type=type(error).__name__)
                else:
                    assert isinstance(error, CustomDiscordException)
                    log = error.cause is None or type(error.cause).__name__ not in UNLOGGED_EXCEPTION_TYPES

                await interaction.edit_original_response(embed=error.as_embed())  # Can get more detailed information from this.
                if log:
                    await self.logger.error(interaction, error)
                    raise error


        self.tree.on_error = on_tree_error

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
