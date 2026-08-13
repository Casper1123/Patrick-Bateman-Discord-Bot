# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import io as _io
import json as _json

import discord
from discord import app_commands, Interaction, Embed, Guild, Colour
from discord.abc import Messageable
from discord.app_commands import Choice, Transform

from configuration.global_config import CFG
from configuration.logger import loggable
from data.interfaces.fact import GlobalAdminFactInterface, SimpleFactEditorData
from data.interfaces.moderation import GlobalAdminModerationInterface
from data.interfaces.other import LocalAdminDataInterface
from discorduser.logger import GlobalLogger
from discorduser.logger.local import LocalLogger
from discorduser.user.abstract import BotClient
from discorduser.user.custom_cog import CustomGroupCog
from discorduser.user.transformers.channel import ChannelIDTransformer
from piss.testing import test_raw_input as input_test
from utilities.exceptions import CustomDiscordException, ErrorTooltip
from utilities.selection_window import selection_window


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=CFG.GLOBAL_ADMIN_SERVER_ID))
class GlobalFactAdminCog(CustomGroupCog, group_name='gfact'):
    def __init__(self, client: BotClient, fact: GlobalAdminFactInterface, logger: GlobalLogger, local_logger: LocalLogger) -> None:
        super().__init__(client)
        self.fact = fact
        self.logger = logger
        self.local_logger = local_logger

    # region facts
    @app_commands.command(name='add', description='Add a new global fact. Will be test-compiled, but not in detail.')
    @app_commands.describe(text='The fact to add. Will be tested',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def add(self, interaction: Interaction, text: str, ephemeral: bool = False) -> None:
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        self.fact.create_global_fact(interaction.user.id, text)
        await self.logger.fact_create(interaction, text)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success',
                                        desc=f'Fact created successfully.')

    @app_commands.command(name='edit', description='Edit or Remove a global fact.')
    @app_commands.describe(index='The index of the fact you\'re editing.',
                           text='The replacement fact.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def edit(self, interaction: Interaction, index: int, text: str, ephemeral: bool = False) -> None:
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        try:
            old: SimpleFactEditorData = self.fact.edit_global_fact(index, interaction.user.id, text)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.fact_edit(interaction, old, text)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success',
                                        desc=f'Fact edited successfully.')

    @app_commands.command(name='delete', description='Delete a global fact.')
    @app_commands.describe(index='The index of the fact to delete', ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def delete(self, interaction: Interaction, index: int, ephemeral: bool = False) -> None:
        try:
            old: SimpleFactEditorData = self.fact.delete_global_fact(index)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.fact_remove(interaction, old)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success',
                                        desc=f'Fact deleted successfully.')

    @app_commands.command(name='index',
                          description='Exports an overview of Global (and Local) facts.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION,
                           json='Export data in JSON format.', local='Also export local facts, indexed by guild ID')
    async def index(self, interaction: Interaction, json: bool = False, local: bool = False,
                    ephemeral: bool = True, ) -> None:
        global_facts: list[SimpleFactEditorData] = self.fact.get_global_facts()
        local_facts: dict[int, list[SimpleFactEditorData]] = {} if not local else self.fact.get_all_local_facts()

        files: list[discord.File] = []
        if json:
            out: list[dict] = [v.as_json() for v in global_facts]
            with _io.StringIO(_json.dumps(out, indent=4)) as text_stream:
                # noinspection bad-argument-type
                files.append(
                    discord.File(
                        fp=text_stream,
                        filename=f"global_fact_data.json"
                    )
                )
        else:
            out: list[str] = []
            for i, fact in enumerate(global_facts):
                author = interaction.guild.get_member(fact.author_id)
                if author:
                    author = f'{author.name} ({author.id})'
                else:
                    author = f'({fact.author_id})'
                out.append(f'{i + 1} {author}: {fact.text}')
            out: str = '\n'.join(out)
            with _io.StringIO(out) as text_stream:
                # noinspection bad-argument-type
                files.append(
                    discord.File(
                        fp=text_stream,
                        filename=f"global_fact_data_{interaction.guild.id}.txt"
                    )
                )

        if local_facts and json:
            out: dict[int, list[dict[str, int | float | None | str | bool | dict | list]]] = {}
            for k, v in local_facts.items():
                out[k] = [f.as_json() for f in v]
            with _io.StringIO(_json.dumps(out, indent=4, sort_keys=True)) as text_stream:
                # noinspection bad-argument-type
                files.append(
                    discord.File(
                        fp=text_stream,
                        filename=f"local_fact_data.json"
                    )
                )
        elif local_facts and not json:
            out: str = ''
            membercache: dict[int, str] = {}
            for k, v in local_facts.items():
                guild: Guild | None = self.client.get_guild(k)
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
                guild_facts += '\n\n\n'  # factnl, nl, #guild, space of 2 between last fact and new guild.
                out += guild_facts
            with _io.StringIO(out) as text_stream:
                # noinspection bad-argument-type
                files.append(
                    discord.File(
                        fp=text_stream,
                        filename='local_fact_data.txt'
                    )
                )

        await interaction.response.send_message(ephemeral=ephemeral, files=files, embed=Embed(
            title=f'{'Global' if not local else 'Total'} fact data',
            description='JSON data attached' if json else f'See attached file{'s' if len(files) > 0 else ''} for fact data.'
        ))
    # endregion

    # region factmod
    @app_commands.command(name='modify', description='Modify local facts from any server directly.')
    @app_commands.describe(guild_id='The ID of the guild you wish to index from.',
                           index='Local fact index.',
                           text='Replacement text. Leave empty to remove entirely.',
                           local_log='Log to the given server\'s local log channel. Author will be denoted as the bot.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def modify(self, interaction: Interaction, guild_id: int, index: int, text: str | None = None,
                     local_log: bool = True, ephemeral: bool = False) -> None:
        delete: bool = text is None
        if not delete:
            text: str
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        try:
            if not delete:
                text: str
                old: SimpleFactEditorData = self.fact.edit_fact(guild_id, index, text, interaction.user.id)
            else:
                old: SimpleFactEditorData = self.fact.delete_fact(guild_id, index)
        except IndexError:
            await self.client.user_feedback(interaction, title='Fact modification failed',
                                            desc=f'Index {index} out of range.', ephemeral=ephemeral)
            return

        await self.logger.fact_modify(interaction, guild_id, old, text)
        guild: Guild | None = self.client.get_guild(guild_id) # used for getting the appropriate log channel.
        # If it is None it's fine
        if local_log and not delete:
            text: str
            await self.local_logger.fact_edit(interaction, guild, old, text, externally_modified=True)
        elif local_log and delete:
            await self.local_logger.fact_remove(interaction, guild, old, externally_modified=True)

        await interaction.response.send_message(
            ephemeral=ephemeral,
            # todo: update to also display guild information
            embed=Embed(title='Success',
                        description=f'Fact {'deleted' if delete else 'edited'} {'successfully.'}'
                                    f'\n# Old:\n'
                                    f'`{old.text}`\n'
                                    f'\n'
                                    f'# New:\n'
                                    f'`{text}`')
        )

    @app_commands.command(name='list', description='List the local facts of the given guild.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION,
                           json='Export the facts to an attached JSON file instead.',
                           guild_id='The ID of the guild you wish to index from.', )
    async def index_local(self, interaction: Interaction, guild_id: int, ephemeral: bool = False,
                          json: bool = False) -> None:
        local_facts: list[SimpleFactEditorData] = self.fact.get_local_facts(guild_id)
        if not local_facts:
            await interaction.response.send_message(
                ephemeral=ephemeral,
                embed=Embed(title='No local facts found.')
            )
            return
        if json:
            out: list[dict[str, int | float | None | str | bool | dict | list]]= [f.as_json() for f in local_facts]

            with _io.StringIO(_json.dumps(out, indent=4, sort_keys=True)) as text_stream:
                # noinspection bad-argument-type
                file = discord.File(
                    fp=text_stream,
                    filename=f"local_fact_data_{guild_id}.json"
                )
        else:
            membercache: dict[int, str] = {}
            guild: Guild | None = self.client.get_guild(guild_id)
            guild_facts: str = f'# - {guild_id} {f': {guild.name}' if guild else ''}'
            for i, f in enumerate(local_facts):
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
            with _io.StringIO(guild_facts) as text_stream:
                # noinspection bad-argument-type
                file = discord.File(
                    fp=text_stream,
                    filename=f'local_fact_data_{guild_id}.txt'
                )
        await interaction.response.send_message(ephemeral=ephemeral, file=file, embed=Embed(
            title=f'Local fact data',
            description='JSON data attached.' if json else f'See attached file for fact data.'
        ))

    # region autocomplete
    async def _gfact_index_autocomplete_impl(self, _: Interaction, current: int) -> list[Choice[int]]:
        if not current:
            current = 0
        facts: list[SimpleFactEditorData] = self.fact.get_global_facts()
        lower, upper = selection_window(len(facts), current, 11, favour='higher')

        return [
            Choice[int](name=f'{offset + 1}: {fact.text[:80]}', value=offset + 1)
            for offset, fact in enumerate(facts[lower:upper])
        ]

    @edit.autocomplete('index')
    @delete.autocomplete('index')
    async def _gfact_index_autocomplete_guard(self, _: Interaction, current: int) -> list[Choice[int]]:
        return await self.autocomplete_guard(_, current, self._gfact_index_autocomplete_impl, 'index')

    async def _gfactmod_index_autocomplete_impl(self, interaction: Interaction, current: int) -> list[Choice[int]]:
        guild_id: int = interaction.namespace.guild_id
        if not guild_id:
            return [Choice[int](name='Bad guild ID', value=-1)]
        facts: list[SimpleFactEditorData] = self.fact.get_local_facts(guild_id)
        if not facts:
            return [Choice[int](name='No local facts', value=-1)]

        if not current:
            current = 0
        lower, upper = selection_window(len(facts), current, 11, favour='higher')
        return [
            Choice[int](name=f'{offset + 1}: {fact.text[:80]}', value=offset + 1)
            for offset, fact in enumerate(facts[lower:upper])
        ]

    @modify.autocomplete('index')
    async def _gfactmod_index_autocomplete_guard(self, interaction: Interaction, current: int) -> list[Choice[int]]:
        return await self.autocomplete_guard(interaction, current, self._gfactmod_index_autocomplete_impl, 'index')
    # endregion
    # endregion


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=CFG.GLOBAL_ADMIN_SERVER_ID))
class GlobalAdminCog(CustomGroupCog, group_name='global'):
    def __init__(self, client: BotClient, fact: GlobalAdminFactInterface, mod: GlobalAdminModerationInterface,
                 db: LocalAdminDataInterface, logger: GlobalLogger) -> None:
        super().__init__(client)
        self.fact = fact
        self.mod = mod
        self.db = db
        self.logger = logger

    @app_commands.command(name='userban',
                          description='Ban a user from using Local Fact administrative features. If already banned, unbans them.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION, user_id='The ID of the user you aim to (un)ban.',
                           reason='A reason, for logging purposes.')
    async def ban_user(self, interaction: Interaction, user_id: int, reason: str | None = None,
                       ephemeral: bool = False) -> None:
        state: bool = self.mod.toggle_ban('user', user_id)
        user = self.client.get_user(user_id)

        await self.logger.ban_user(interaction, user_id, user, state, reason)

        embed = Embed(title=f'User {'un' if not state else ''}banned')

        if user:
            embed.set_author(name=user.name, icon_url=user.avatar.url)
        else:
            embed.set_author(name=f'{user_id}')
        await interaction.response.send_message(ephemeral=ephemeral, embed=embed)

    @app_commands.command(name='guildban',
                          description='Ban a guild from using Local Fact administrative features. If already banned, unbans it.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION,
                           guild_id='The ID of the guild you aim to (un)ban.',
                           reason='A reason, for logging purposes.')
    async def ban_guild(self, interaction: Interaction, guild_id: int, reason: str | None = None,
                        ephemeral: bool = False) -> None:
        state: bool = self.mod.toggle_ban('guild', guild_id)
        guild = self.client.get_guild(guild_id)

        await self.logger.ban_guild(interaction, guild_id, guild, state, reason)

        embed = Embed(title=f'Guild {'un' if not state else ''}banned')

        if guild:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name=f'{guild}')
        await interaction.response.send_message(ephemeral=ephemeral, embed=embed)

    # region other
    @app_commands.command(name='db_killswitch',
                          description='Disables any interaction with, or addition to, the Local Fact database.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def killswitch(self, interaction: Interaction, ephemeral: bool = False):
        state: bool = self.fact.toggle_local_fact_killswitch()
        await self.client.user_feedback(interaction, desc=f'Killswitch state set to {state}', ephemeral=ephemeral)
        await self.logger.log_general(
            console=f'[[ KILLSWITCH TOGGLE ]] :: Set to {state} by {interaction.user.name} : {interaction.user.id}',
            channel=Embed(
                title='[[ KILLSWITCH TOGGLE ]]',
                description=f'Set to **{state}**',
                colour=Colour.red()
            ).set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        )

    @app_commands.command(name='set_log',
                          description='Sets a log channel in global config.')
    async def set_log_channel(self, interaction: Interaction, action: loggable, channel: Transform[int, ChannelIDTransformer], ephemeral: bool = False):
        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild

        channel = guild.get_channel(channel)
        if not isinstance(channel, Messageable):
            raise CustomDiscordException(
                f'Channel id {interaction.channel_id} with type {type(interaction.channel)} is not discord.abc.Messageable.')

        if channel:
            await self.logger.set_log_channel(interaction, action,
                                              channel)  # doing this first so it at least lands this type of information in the final channel :p
            self.logger.update_output_channel(action, channel)
            await self.client.user_feedback(interaction, title='Log output updated',
                                            desc=f'Set log output channel for {action} to <#{channel.id}>',
                                            ephemeral=ephemeral)
        else:
            await self.client.user_feedback(interaction, title='Log output update failed', desc='Channel not found',
                                            ephemeral=ephemeral)

    # todo: backup command, creating a host-side backup of the db. Keep up to 3 backups.
    # endregion
