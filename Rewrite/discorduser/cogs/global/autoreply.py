# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import io as _io
import json as _json

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, AliasData, _reply_types, _trigger_types
from Rewrite.data.interfaces.data import GlobalAdminDataInterface, FactEditorData
from Rewrite.utilities.exceptions import CustomDiscordException, ErrorTooltip
from Rewrite.piss.testing import test_raw_input as input_test

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input
DELETE_ENTRY_INPUT: str = '<DELETE>'
WEIGHT_UPPER_BOUND: int = 1024

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
                           rate='The standard activation rate of this alias, ranging in between 1-256. Default: 256 (100%)',
                           ephemeral='Hide the command and messages from the chat.')
    async def create_alias(self, interaction: discord.Interaction, name: str, rate: int = None, ephemeral: bool = False) -> None:
        try:
            self.repl.create_alias(name, rate if rate is not None else 256)
        except ValueError as e:
            await interaction.response.send_message(ephemeral=ephemeral, embed=discord.Embed(title='Alias creation failed',
                                                                        description='This alias already exists.'))
            return
        await interaction.response.send_message(ephemeral=ephemeral, embed=discord.Embed(title='Alias created successfully', ))

    @app_commands.command(name='edit', description='Edit an existing Alias')
    @app_commands.describe(alias='The Alias you wish to edit.',
                          new_name='The new name of the Alias.',
                          rate='The standard activation rate of this alias, ranging in between 1-256. Leave empty for 256',
                           ephemeral='Hide the command and messages from the chat.')
    @app_commands.rename(new_name='name')
    async def edit_alias(self, interaction: discord.Interaction, alias: str, new_name: str | None = None, rate: int | None = None):
        if rate is None and new_name is None:
            await interaction.response.send_message(embed=discord.Embed(title='Alias edit failed',
                                                                        description='Please select an option. '
                                                                                    'If you intend to delete this alias, select the pre-given option to do so.'))
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
                                                                        description='The given alias does not exist, or the new alias name is already taken.'))
            return
        await interaction.response.send_message(embed=discord.Embed(title='Alias edited successfully'))

    @app_commands.command(name='delete', description='Delete an existing Alias')
    @app_commands.describe(alias='The Alias you wish to delete.')
    async def delete_alias(self, interaction: discord.Interaction, alias: str):
        try:
            self.repl.delete_alias(alias)
        except ValueError as e:
            await interaction.response.send_message(embed=discord.Embed(title='Alias edit failed',
                                                                        description='Cannot delete a nonexistent Alias.'))
            return
        await interaction.response.send_message(embed=discord.Embed(title='Alias deleted successfully'))

    # region autocomplete
    @edit_alias.autocomplete('alias')
    @delete_alias.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str):
        target = current.lower() # Prevent repeat transformation
        aliases: list[AliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]

    @edit_alias.autocomplete('new_name')
    async def _delete_alias_option_autocomplete(self, _: discord.Interaction, __: str) -> list[Choice]:
        return [
            Choice(name='Delete this Alias.', value=DELETE_ENTRY_INPUT)
        ]
    # endregion

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _TriggerGlobalAdminCog(commands.Cog, name='trigger'):
    def __init__(self, client: BotClient,  db: GlobalAdminDataInterface, repl: GlobalTextAutorepliesInterface, logger) -> None:
        self.client = client
        self.db = db
        self.repl = repl
        self.logger = logger

    @app_commands.command(name='create', description='Create a new Trigger')
    @app_commands.describe(alias='The Alias this Trigger belongs to.', text='Trigger ReGex to match to.',
                           weight='The relative weight this Trigger will proc to, overriding the Alias rate if given. Range 1-256')
    async def create_trigger(self, interaction: discord.Interaction, alias: str, text: str, weight: int = None):
        if weight is not None and not (1 <= weight <= 256):
            await interaction.response.send_message(embed=discord.Embed(title='Trigger creation failed',
                                                                        description='The given weight is not in range **[1..256]**.'))
            return
        try:
            self.repl.add_trigger(alias, trigger_type='regex', data=text, rate=weight) # todo: create and support other trigger types.
        except ValueError as e:
            await interaction.response.send_message(embed=discord.Embed(title='Trigger creation failed',
                                                                        description=f'The given Alias {alias} does not exist.'))
            return

        await interaction.response.send_message(embed=discord.Embed(title='Trigger created successfully',
                                                                    description=f'Alias: {alias}\n'
                                                                                f'*Type: Regex*\n'
                                                                                f'Content: **{text}**'))

    # @app_commands.command(name='edit', description='Edit a Trigger')
    # @app_commands.describe()
    async def edit_trigger(self, interaction: discord.Interaction, alias: str, index: ..., ): # todo: how to index into?
        ...

    async def delete_trigger(self, interaction: discord.Interaction, alias: str, ):
        ...
    # region autocomplete
    @create_trigger.autocomplete('alias')
    async def _alias_options_autocomplete(self, _: discord.Interaction, current: str):
        target = current.lower()  # Prevent repeat transformation
        aliases: list[AliasData] = [i for i in self.repl.get_aliases() if i.name.startswith(target)]
        aliases.sort(key=lambda x: x.name)
        return [Choice(name=f'{i.name} ({i.rate})', value=i.name) for i in aliases[:4]]
    # endregion

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class _ReplyGlobalAdminCog(commands.Cog, name='reply'):
    def __init__(self, client: BotClient, db: GlobalAdminDataInterface, repl: GlobalTextAutorepliesInterface, logger) -> None:
        self.client = client
        self.db = db
        self.repl = repl
        self.logger = logger

    # Create
    @app_commands.command(name='create', description='Create a new Reply')
    @app_commands.describe(reply_type='The type of Reply this has to be.',
                           text='Raw text data for the reply.',
                           weight='The relative weight this Reply will proc to. Defaults to 1.',)
    @app_commands.choices(reply_type=[
        Choice(name='text', value='text'),
    ])
    @app_commands.rename(reply_type='type')
    async def create_reply(self, interaction: discord.Interaction, alias: str, reply_type: _reply_types, text: str, weight: int = 1):
        # todo: check, if reply type is reaction, that it is a standard unicode emoji.
        if reply_type == 'reaction':
            await interaction.response.send_message(embed=discord.Embed(title='Unsupported',
                                                                        description='The given Reply type is not supported.\n'
                                                                                    'It will be in the future, but right now it is not. The setting is a placeholder.'))
            return
        if weight is not None and not 0 <= weight <= WEIGHT_UPPER_BOUND:
            await interaction.response.send_message(embed=discord.Embed(title='Reply creation failed',
                                                                        description=f'Weight not in range [1..{WEIGHT_UPPER_BOUND}].'))
        if reply_type == 'text':
            # test the reply before adding.
            if not await input_test(self.client, interaction, text, ephemeral=True):
        try:
            self.repl.add_reply(alias, reply_type, data=text, weight=weight)
        except ValueError as e:
            ...
    # Edit
    # Remove

async def attach_cogs(client: BotClient, db: GlobalAdminDataInterface, repl: GlobalTextAutorepliesInterface, logger):
    await client.add_cog(_AliasGlobalAdminCog(client, db, repl, logger))
    await client.add_cog(_TriggerGlobalAdminCog(client, db, repl, logger))
    await client.add_cog(_ReplyGlobalAdminCog(client, db, repl, logger))