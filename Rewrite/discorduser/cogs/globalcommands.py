# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import io as _io
import json as _json
import discord
from discord import app_commands, Interaction, Embed, Guild, Member
from discord.ext import commands

from .. import BotClient
from ...data.data_interface_abstracts import GlobalAdminDataInterface, FactEditorData
from ...utilities.exceptions import CustomDiscordException, ErrorTooltip
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor, DebugInstructionExecutor
from ...variables_parser.testing import test_raw_input as input_test

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input

@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class GlobalFactAdminCog(commands.Cog, name='gfact'):
    def __init__(self, client: BotClient,  db: GlobalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    # region facts
    @app_commands.command(name='add', description='Add a new global fact. Will be test-compiled, but not in detail.')
    @app_commands.describe(text='The fact to add. Will be tested',
                           ephemeral='Hide the message from other users.')
    async def add(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        success: bool = self.db.create_global_fact(interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral,
                                                embed=Embed(title='Success' if success else 'Failure',
                                                            description=f'Fact added successfully.' if success else 'Fact creation failed.'))
        await self.logger.global_fact_create(interaction, text)

    @app_commands.command(name='edit', description='Edit or Remove a global fact. Leave the text empty to remove.')
    @app_commands.describe(index='The index of the fact you\'re editing/removing',
                           text='The replacement fact. Leave empty to remove the original.',
                           ephemeral='Hide the message from other users.')
    async def edit(self, interaction: Interaction, index: int, text: str = None, ephemeral: bool = True) -> None:
        delete: bool = text is None
        if not delete:
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        old: FactEditorData = self.db.get_global_fact(index)
        success: bool = self.db.edit_global_fact(old.author_id, old.text, interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral,
                                                embed=Embed(title='Success' if success else 'Failure',
                                                            description=f'Fact {'deleted' if delete else 'edited'} successfully.' if success else f'Fact {'deletion' if delete else 'edit'} failed.'))
        await self.logger.fact_edit(interaction, text, old)

    @app_commands.command(name='index',
                          description='Exports an overview of Global (and, optionally, Local) facts. Can be exported to JSON for easier automated use.')
    @app_commands.describe(ephemeral='Hide the message from other users.',
                           json='Export the facts to an attached JSON file instead.', local='Also export local facts, indexed by guild ID')
    async def index(self, interaction: Interaction, ephemeral: bool = True, json: bool = False, local: bool = False) -> None:
        global_facts: list[FactEditorData] = self.db.get_global_facts()
        local_facts: dict[int, list[FactEditorData]] = {} if not local else self.db.get_all_local_facts()

        files: list[discord.File] = []
        if json:
            out: list[dict[str, str | int]] = [{'text': v.text, 'author_id': v.author_id} for v in global_facts]
            with _io.StringIO(_json.dumps(out, indent=4)) as text_stream:
                files.append(discord.File(fp=text_stream, filename=f"global_fact_data.json"))
        else:
            out: list[str] = []
            for i, fact in enumerate(global_facts):
                author = interaction.guild.get_member(fact.author_id)
                if author:
                    author = author.name
                else:
                    author = fact.author_id
                out.append(f'{i + 1} ({author}): {fact.text}')
            out: str = '\n'.join(out)
            with _io.StringIO(out) as text_stream:
                files.append(discord.File(fp=text_stream, filename=f"global_fact_data_{interaction.guild.id}.txt"))

        if local_facts and json:
            out: dict[int, list[dict[str, str | int]]] = {}
            for k, v in local_facts.items():
                out[k] = [{'text': f.text, 'author_id': f.author_id} for f in v]
            with _io.StringIO(_json.dumps(out, indent=4, sort_keys=True)) as text_stream:
                files.append(discord.File(fp=text_stream, filename=f"local_fact_data.json"))
        elif local_facts and not json:
            out: str = ''
            membercache: dict[int, str] = {}
            for k, v in local_facts.items():
                guild: Guild = self.client.get_guild(k)
                guild_facts: str = f'# - {k} {f': {guild.name}' if guild else ''}'
                for i, f in enumerate(v):
                    # member -> either in cache or require guild.
                    # if guild is not available, then we have a problem
                    if f.author_id in membercache.keys():
                        member = membercache[f.author_id]
                    elif not guild:
                        member = None
                    else:
                        member = guild.get_member(f.author_id).name
                        membercache[f.author_id] = member
                    guild_facts += f'\n{i} ({f.author_id if not member else f'{member} ; {f.author_id}'}): {f.text}'
                guild_facts += '\n\n\n' # factnl, nl, #guild, space of 2 between last fact and new guild.
                out += guild_facts
            with _io.StringIO(out) as text_stream:
                files.append(discord.File(fp=text_stream, filename='local_fact_data.txt'))

        await interaction.response.send_message(ephemeral=ephemeral, files=files, embed=Embed(
            title=f'{'Global' if not local else 'Total'} fact data',
            description='JSON data attached' if json else f'See attached file{'s' if len(files) > 0 else ''} for fact data.'
        ))
    # endregion

    # region factmod
    # fact modify -> other server
    @app_commands.command(name='modify', description='Modify local facts from any server directly.')
    @app_commands.describe(guild_id='The ID of the guild you wish to index from.',
                           index='Local fact index.',
                           text='Replacement text. Leave empty to remove entirely.',
                           local_log='Log to the given server\'s local log channel. Author will be denoted as the bot.',
                           ephemeral='Hide the message from the channel. Default: False')
    async def modify(self, interaction: Interaction, guild_id: int, index: int, text: str = None, local_log: bool = True, ephemeral: bool = False) -> None:
        delete: bool = text is None
        if not delete:
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        local_facts: list[FactEditorData] = self.db.get_local_facts(guild_id)
        try:
            old: FactEditorData = local_facts[index]
        except IndexError as e:
            raise CustomDiscordException(tooltip=ErrorTooltip.NONE, cause=e,
                                         message=f'Index ({index}) not in 0 <= index < {len(local_facts)}.')
        success: bool = self.db.edit_fact(interaction.guild_id, old.author_id, old.text, interaction.user.id, text)

        await interaction.response.send_message(ephemeral=ephemeral, # todo: update to also display guild information
                                                embed=Embed(title='Success' if success else 'Failure',
                                                            description=f'Fact {'deleted' if delete else 'edited'} {'successfully.' if success else 'failed.'}'
                                                                                    f'{f'\n# Old:\n'
                                                                                       f'`{old.text}`\n'
                                                                                       f'\n'
                                                                                       f'# New:\n'
                                                                                       f'`{text}`' if success else ''}'))
        await self.logger.global_fact_edit(interaction, text, old)
        if local_log:
            # todo: log to server locally
            pass

    @app_commands.command(name='list', description='List the local facts of the given guild.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: False',
                           json='Export the facts to an attached JSON file instead.',
                           guild_id='The ID of the guild you wish to index from.',)
    async def index_local(self, interaction: Interaction, guild_id: int, ephemeral: bool = False, json: bool = False) -> None:
        raise NotImplementedError()
    # endregion

@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class GlobalAdminCog(commands.Cog, name='global'):
    def __init__(self, client: BotClient,  db: GlobalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    # region autoreply
    # todo: make command list, probably move to autoreply cog?
    # endregion autoreply

    @app_commands.command(name='userban', description='Ban a user from using Local Fact administrative features. If already banned, unbans them.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: False', user_id='The ID of the user you aim to (un)ban.')
    async def ban_user(self, interaction: Interaction, user_id: int, ephemeral: bool = False) -> None:
        state: bool = self.db.is_banned_user(user_id)
        self.db.unban_user(user_id) if state else self.db.ban_user(user_id)
        await self.logger.user_ban(interaction, user_id, not state)
        embed = Embed(title=f'User {'un' if state else ''}banned')
        user = self.client.get_user(user_id)
        if user:
            embed.set_author(name=user.name, icon_url=user.avatar.url)
        else:
            embed.set_author(name=f'{user_id}')
        await interaction.response.send_message(ephemeral=ephemeral, embed=embed)

    @app_commands.command(name='guildban',
                          description='Ban a guild from using Local Fact administrative features. If already banned, unbans it.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: False',
                           guild_id='The ID of the guild you aim to (un)ban.')
    async def ban_guild(self, interaction: Interaction, guild_id: int, ephemeral: bool = False) -> None:
        state: bool = self.db.is_banned_guild(guild_id)
        self.db.unban_guild(guild_id) if state else self.db.ban_guild(guild_id)
        await self.logger.guild_ban(interaction, guild_id, not state)
        embed = Embed(title=f'Guild {'un' if state else ''}banned')
        guild = self.client.get_guild(guild_id)
        if guild:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name=f'{guild}')
        await interaction.response.send_message(ephemeral=ephemeral, embed=embed)

    # region other
    @app_commands.command(name='refresh',
                          description='Refresh command tree. ONLY USE IF YOU KNOW WHAT YOU ARE DOING.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: True')
    async def refresh(self, interaction: Interaction, ephemeral: bool = True):
        await interaction.response.defer(ephemeral=ephemeral, thinking=False)
        await interaction.edit_original_response(content=f'Synchronizing Command Tree ...')
        await self.client.tree.sync()
        await interaction.edit_original_response(content=f'Starting Super Guild overwrites ...')
        for i, guild_id in enumerate(self.db.get_super_server_ids()):
            try:
                await self.client.tree.sync(guild=discord.Object(id=guild_id))
            except discord.HTTPException:
                pass
        await interaction.edit_original_response(content=f'Command Tree synchronization complete.')

    @app_commands.command(name='DB_KILLSWITCH',
                          description='Disables any interaction with, or addition to, the Local Fact database. Use only if the bot is being griefed.')
    @app_commands.describe(ephemeral='Hide the message from the channel. Default: True')
    async def killswitch(self, interaction: Interaction, ephemeral: bool = True):
        state: bool = self.client.toggle_local_fact_killswitch()
        await interaction.response.send_message(ephemeral=ephemeral, content=f'Killswitch state set to {state}')

    # todo: backup command, creating a host-side backup of the db. Keep up to 3 backups.
    # endregion
