import io
import json as _json

import discord
from discord import app_commands, Interaction, Colour, Embed
from discord.app_commands import Choice
from discord.ext import commands

from configuration.global_config import CFG
from data.interfaces.saying import GlobalAdminSayingInterface, SimpleSayingEditorData, SayingEditorData
from discorduser.logger import GlobalLogger
from discorduser.user.abstract import BotClient
from discorduser.user.custom_cog import CustomGroupCog
from piss.testing import test_raw_input as input_test
from utilities.selection_window import selection_window

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=CFG.GLOBAL_ADMIN_SERVER_ID))
class GlobalAdminSayingCog(CustomGroupCog, group_name='saying'):
    def __init__(self, client: BotClient, saying: GlobalAdminSayingInterface, logger: GlobalLogger) -> None:
        super().__init__(client)
        self.saying = saying
        self.logger = logger

    @app_commands.command(name='create', description='Create a new saying')
    @app_commands.describe(saying='PISS-compatible saying.', ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def saying_create(self, interaction: Interaction, saying: str, ephemeral: bool = False) -> None:
        if not input_test(self.client, interaction, saying, ephemeral):
            return

        self.saying.create_saying(saying)
        await self.logger.create_saying(interaction, saying)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success', desc='Saying created successfully')

    @app_commands.command(name='edit', description='Edit an existing saying.')
    @app_commands.describe(index='The index of the saying you\'re editing.',
                           saying='The replacement saying.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def saying_edit(self, interaction: Interaction, index: int, saying: str, ephemeral: bool = False) -> None:
        if not input_test(self.client, interaction, saying, ephemeral):
            return

        try:
            old: SimpleSayingEditorData = self.saying.edit_saying(index, saying)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.edit_saying(interaction, old, saying)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success',
                                        desc=f'Fact edited successfully.')

    @app_commands.command(name='delete', description='Delete an existing saying.')
    @app_commands.describe(index='The index of the saying you\'re deleting.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def saying_delete(self, interaction: Interaction, index: int, ephemeral: bool = False) -> None:
        try:
            old: SimpleSayingEditorData = self.saying.delete_saying(index)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.delete_saying(interaction, old)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success', desc=f'Saying deleted successfully.')

    @app_commands.command(name='index', description='Display all of the stored Sayings.')
    @app_commands.describe(json='Output to a json file', ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def index(self, interaction: Interaction, json: bool = False, ephemeral: bool = True) -> None:
        sayings: list[SayingEditorData] = self.saying.get_sayings()
        file: discord.File
        if json:
            sayings: list[dict] = [i.as_json() for i in sayings]
            with io.StringIO(_json.dumps(sayings, indent=4)) as text_stream:
                file = discord.File(fp=text_stream, filename=f"sayings.json")
        else:
            sayings: list[str] = [f'{i + 1} [{j.author_id} at {j.modified_at}]: {j.text}' for i, j in enumerate(sayings)]
            sayings: str = '\n'.join(sayings)
            with io.StringIO(sayings) as text_stream:
                file = discord.File(fp=text_stream, filename=f"sayings.txt")
        await interaction.response.send_message(file=file, ephemeral=ephemeral, embed=Embed(title='Sayings', description='See attached file for Sayings data.', colour=Colour.blue())) # noqa this exists

    # region autocomplete
    async def _index_autocomplete_callback_impl(self, _: Interaction, current: str) -> list[Choice[str]]:
        if not current:
            current = 0
        sayings: list[SimpleSayingEditorData] = self.saying.get_sayings()
        lower, upper = selection_window(len(sayings), current, 4, favour='higher')
        return [
            Choice(name=f'{offset}: {saying[:80]}', value=offset)
            for offset, saying in enumerate(sayings[lower:upper])
        ]

    @saying_edit.autocomplete('index')
    @saying_delete.autocomplete('index')
    async def _index_autocomplete_callback_guard(self, _: Interaction, current: str) -> list[Choice[str]]:
        return await self.autocomplete_guard(_, current, self._index_autocomplete_callback_impl, 'index')
    # endregion