import aiohttp
import socket

import discord
from discord import app_commands
from discord.app_commands import CommandOnCooldown
from discord.ext import commands

from Rewrite.data.data_interface_abstracts import DataInterface
from Rewrite.discorduser.logger.logger import Logger
from Rewrite.utilities.exceptions import CustomDiscordException
from Rewrite.variables_parser import InstructionParseError

UNLOGGED_EXCEPTION_TYPES = [InstructionParseError.__name__, CommandOnCooldown.__name__] # using __name__ to ensure that when I change the class names this updates.


class BotClient(commands.Bot):
    def __init__(self, db: DataInterface, logger: Logger) -> None:
        self.db: DataInterface = db
        self.logger: Logger = logger

        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_kill_switch = not self.local_fact_kill_switch
        return self.local_fact_kill_switch

    async def setup_hook(self) -> None:
        async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            try:
                if (True):  # todo: config to make uncaught public errors hidden or not
                    await interaction.response.defer(ephemeral=True, thinking=False)
            except Exception as err: # Shoddy attempt at hiding the error from users.
                pass

            # handle exceptions
            finally:
                if (isinstance(error, aiohttp.client_exceptions.ClientConnectorDNSError)
                        or isinstance(error, socket.gaierror)):
                    return # Skip 'connection lost' exceptions, also removing them from the logging.
                    # Idk why, but for some reason my host device seems to lose connection at unknown intervals for short periods of time.
                    # So this is temporary glue fix.
                log: bool = True
                if isinstance(error, CommandOnCooldown):
                    log = type(error).__name__ not in UNLOGGED_EXCEPTION_TYPES
                    error = CustomDiscordException(message=str(error), error_type=error.__name__)
                elif not isinstance(error, CustomDiscordException):
                    log = type(error).__name__ not in UNLOGGED_EXCEPTION_TYPES
                    error_old = error
                    error: CustomDiscordException = CustomDiscordException(cause=error_old, error_type=type(error).__name__)
                else:
                    assert isinstance(error, CustomDiscordException)
                    log = type(error.cause).__name__ not in UNLOGGED_EXCEPTION_TYPES

                await interaction.edit_original_response(embed=error.as_embed())  # Can get more detailed information from this.
                if log:
                    await self.logger.log_error(error, interaction)
                raise error


        self.tree.on_error = on_tree_error
