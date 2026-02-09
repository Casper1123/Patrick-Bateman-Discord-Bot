# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import discord
from discord import app_commands, Interaction
from discord.ext import commands

from ...data.data_interface_abstracts import GlobalAdminDataInterface
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor, DebugInstructionExecutor

SUPER_SERVER_IDS: list[int] = [] # todo: config input
GLOBAL_ADMIN_SERVER_IDS: list[int] = [] # todo: config input

@app_commands.default_permissions(administrator=True)
@app_commands.guilds(*[discord.Object(id=i) for i in GLOBAL_ADMIN_SERVER_IDS])
class GlobalAdminCog(commands.Cog, name='global'):
    def __init__(self, client: commands.bot,  db: GlobalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    # region facts
    # fact add
    # fact edit -> empty input removes
    # endregion

    # region factmod
    # fact modify -> other server
    # fact list [guildid]
    # fact count -> list fact number for each other server.
    # banuser
    # banguild
    # endregion


    # region autoreply
    # endregion autoreply

    # region other
    @app_commands.command(name='refresh', description='Refresh command tree. ONLY USE IF YOU KNOW WHAT YOU ARE DOING.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: True')
    async def refresh(self, interaction: Interaction, ephemeral: bool = True):
        await interaction.response.defer(ephemeral=ephemeral, thinking=False)
        await interaction.edit_original_response(content=f'Synchronizing Command Tree ...')
        await self.client.tree.sync()
        await interaction.edit_original_response(content=f'Starting Super Guild overwrites ...')
        for i, guild_id in enumerate(SUPER_SERVER_IDS):
            try:
                await self.client.tree.sync(guild=discord.Object(id=guild_id))
            except discord.HTTPException:
                pass
        await interaction.edit_original_response(content=f'Command Tree synchronization complete.')
    # endregion