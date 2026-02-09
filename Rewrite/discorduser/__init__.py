import aiohttp
import socket

import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.data.data_interface_abstracts import DataInterface
from Rewrite.discorduser.logger.logger import Logger
from Rewrite.utilities.exceptions import CustomDiscordException


class BotClient(commands.Bot):
    def __init__(self, db: DataInterface, logger: Logger) -> None:
        self.db: DataInterface = db
        self.logger: Logger = logger

        self.local_fact_killswitch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_killswitch = not self.local_fact_killswitch
        return self.local_fact_killswitch

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
                if not isinstance(error, CustomDiscordException):
                    error_old = error
                    error: CustomDiscordException = CustomDiscordException(cause=error_old, error_type=type(error).__name__)

                await interaction.edit_original_response(embed=error.as_embed())  # Can get more detailed information from this.
                raise error


        self.tree.on_error = on_tree_error
