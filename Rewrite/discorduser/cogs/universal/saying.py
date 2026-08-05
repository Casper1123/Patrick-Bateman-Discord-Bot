import discord
from discord import app_commands, Interaction
from discord.app_commands import Choice
from discord.ext import commands

from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface, SimpleSayingEditorData
from Rewrite.discorduser.logger import GlobalLogger
from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.piss.testing import test_raw_input as input_test
from Rewrite.utilities.selection_window import selection_window

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class GlobalAdminSayingCog(commands.Cog, name='saying'):
    def __init__(self, client: BotClient, saying: GlobalAdminSayingInterface, logger: GlobalLogger) -> None:
        self.client = client
        self.saying = saying
        self.logger = logger

    @app_commands.command(name='create', description='Create a new saying')
    @app_commands.describe(saying='PISS-compatible saying.', ephemeral='Hide this command for other users.')
    async def saying_create(self, interaction: Interaction, saying: str, ephemeral: bool = False) -> None:
        if not input_test(self.client, interaction, saying, ephemeral):
            return

        self.saying.create_saying(saying)
        await self.logger.create_saying(interaction, saying)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success', desc='Saying created successfully')

    @app_commands.command(name='edit', description='Edit an existing saying.')
    @app_commands.describe(index='The index of the saying you\'re editing.',
                           saying='The replacement saying.',
                           ephemeral='Hide this command for other users.')
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
                           ephemeral='Hide this command for other users.')
    async def saying_delete(self, interaction: Interaction, index: int, ephemeral: bool = False) -> None:
        try:
            old: SimpleSayingEditorData = self.saying.delete_saying(index)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.delete_saying(interaction, old)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success', desc=f'Saying deleted successfully.')

    @saying_edit.autocomplete('index')
    @saying_delete.autocomplete('index')
    async def _index_autocomplete_callback(self, _: Interaction, current: str) -> list[Choice[str]]:
        if not current:
            current = 0
        sayings: list[SimpleSayingEditorData] = self.saying.get_sayings()
        lower, upper = selection_window(len(sayings), current, 4, favour='higher')
        return [
            Choice(name=f'{offset}: {saying[:80]}', value=offset)
            for offset, saying in enumerate(sayings[lower:upper])
        ]
