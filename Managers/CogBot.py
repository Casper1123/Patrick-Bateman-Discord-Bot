import discord
from discord.ext import commands
from discord import app_commands


from Managers.Exceptions import FactIndexError
from .ConstantsManager import ConstantsManager

# Packages; import setup and run those
from Cogs.FactsCog import FactsCog
from Cogs.GlobalAdminCog import GlobalAdminGroup
from Cogs.AdminCog import LocalAdminGroup
from Cogs.AskPatrick import AskPatrick
from Cogs.MainCommandsCog import MainCommandsCog
from Cogs.ListenerCog import ListenerCog


class CogBot(commands.Bot):
    def __init__(self, constants_manager: ConstantsManager) -> None:
        self.cm: ConstantsManager = constants_manager

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        await self.add_cog(FactsCog(self, self.cm))
        await self.add_cog(GlobalAdminGroup(self, self.cm))
        await self.add_cog(LocalAdminGroup(self, self.cm))
        await self.add_cog(AskPatrick(self, self.cm))
        await self.add_cog(MainCommandsCog(self, self.cm))
        await self.add_cog(ListenerCog(self, self.cm))

        async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            try:
                await interaction.response.defer(ephemeral=True, thinking=False)
            except Exception as err:
                pass

            # handle exceptions
            finally:
                if isinstance(error, FactIndexError):
                    await interaction.edit_original_response(content=f"{error}")
                else:
                    await interaction.edit_original_response(content=f"An error has occurred, Please notify the application developer.\n"
                                                                     f"*{error}*")
                raise error

        self.tree.on_error = on_tree_error

        # Big stinky doodo practice
        await self.tree.sync()
        for guild_id in self.cm.global_edits_server_ids:
            try:
                await self.tree.sync(guild=discord.Object(id=guild_id))
            except discord.HTTPException:
                pass
