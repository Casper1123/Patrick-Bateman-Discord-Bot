import aiohttp
import socket

import discord
from discord import app_commands
from discord.ext import commands


class CogBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            try:
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
                else:
                    await interaction.edit_original_response(
                        content=f"An error has occurred, Please notify the application developer.\n"
                                f"*{error}*")
                    raise error

        self.tree.on_error = on_tree_error

        # Big stinky doodo practice TODO: Find another way to fix this please.
        await self.tree.sync()
        return

        for guild_id in self.cm.global_edits_server_ids:
            try:
                await self.tree.sync(guild=discord.Object(id=guild_id))
            except discord.HTTPException:
                pass
