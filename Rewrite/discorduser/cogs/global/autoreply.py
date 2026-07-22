# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import io as _io
import json as _json

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, AliasData
from Rewrite.data.interfaces.data import GlobalAdminDataInterface, FactEditorData
from Rewrite.utilities.exceptions import CustomDiscordException, ErrorTooltip
from Rewrite.piss.testing import test_raw_input as input_test

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input
DELETE_ALIAS_INPUT: str = '<DELETE>'

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _AliasGlobalAdminCog(commands.Cog, name='alias'):
    def __init__(self, client: commands.Bot,  db: GlobalAdminDataInterface, repl: GlobalTextAutorepliesInterface, logger) -> None:
        self.client = client
        self.db = db
        self.repl = repl
        self.logger = logger

    @app_commands.command(name='create', description='Create a new Alias')
    @app_commands.describe(name='The name of the new alias. Cannot be duplicate.',
                           rate='The standard activation rate of this alias, ranging in between 1-256. Default: 256 (100%)')
    async def create_alias(self, interaction: discord.Interaction, name: str, rate: int = None):
        if name == DELETE_ALIAS_INPUT:
            await interaction.response.send_message(embed=discord.Embed(title='Alias creation failed',
                                                                        description='You cannot use this as an Alias name.'))
        try:
            self.repl.create_alias(name, rate if rate is not None else 256)
        except ValueError as e:
            await interaction.response.send_message(embed=discord.Embed(title='Alias creation failed',
                                                                        description='This alias already exists.'))
            return
        await interaction.response.send_message(embed=discord.Embed(title='Alias created successfully', ))

    @app_commands.command(name='edit', description='Edit or delete an existing Alias')
    @app_commands.describe(alias='The Alias you wish to edit.',
                          new_name='The new name of the Alias. If you select the deletion option, this will remove the Alias.',
                          rate='The standard activation rate of this alias, ranging in between 1-256.')
    async def edit_alias(self, interaction: discord.Interaction, alias: str, new_name: str | None = None, rate: int | None = None):
        if rate is None and new_name is None:
            await interaction.response.send_message(embed=discord.Embed(title='Alias edit failed',
                                                                        description='Please select an option. '
                                                                                    'If you intend to delete this alias, select the pre-given option to do so.'))
        # mode: edit
        if new_name != DELETE_ALIAS_INPUT:
            if rate is not None and not (1 <= rate <= 256):
                # Rate not in domain and passed in.
                await interaction.response.send_message(embed=discord.Embed(
                    title='Alias edit failed',
                    description=f'The given rate **{rate}** is not within the domain **[1..256]**.'))
                return
            try:
                self.repl.edit_alias(alias, new_name if (new_name and new_name != alias) else None, rate)
            except ValueError as e:
                await interaction.response.send_message(embed=discord.Embed(title='Alias edit failed',
                                                                            description='The given alias does not exist.'))
                return
            await interaction.response.send_message(embed=discord.Embed(title='Alias edited successfully'))
        # mode: delete
        else:
            try:
                self.repl.delete_alias(alias)
            except ValueError as e:
                await interaction.response.send_message(embed=discord.Embed(title='Alias edit failed',
                                                                            description='Cannot delete a nonexistent Alias.'))
                return
            await interaction.response.send_message(embed=discord.Embed(title='Alias deleted successfully'))

    @edit_alias.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str):
        target = current.lower() # Prevent repeat transformation
        aliases: list[AliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]

    @edit_alias.autocomplete('new_name')
    async def _delete_alias_option_autocomplete(self, _: discord.Interaction, __: str) -> list[Choice]:
        return [
            Choice(name='Delete this Alias.', value=DELETE_ALIAS_INPUT)
        ]


async def attach_cogs(client: commands.Bot, db: GlobalAdminDataInterface, repl: GlobalTextAutorepliesInterface, logger):
    await client.add_cog(_AliasGlobalAdminCog(client, db, repl, logger))