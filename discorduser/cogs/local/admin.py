import io as _io
import json as _json

import discord
from discord import app_commands, Interaction, Guild, TextChannel, VoiceChannel, StageChannel, Thread
from discord.abc import Messageable
from discord.app_commands import Choice, Transform

from configuration.global_config import CFG
from data.interfaces.fact import LocalAdminFactInterface, SimpleFactEditorData
from data.interfaces.moderation import LocalAdminModerationInterface
from data.interfaces.other import LocalAdminDataInterface
from data.interfaces.pref import GuildChannelPreferenceData, PreferencesInterface, supported_autoreply_features
from discorduser.logger import GlobalLogger
from discorduser.logger.local import LocalLogger
from discorduser.user.abstract import BotClient
from discorduser.user.custom_cog import CustomGroupCog
from discorduser.user.transformers.channel import ChannelIDTransformer
from piss.old import parse_variables, Instruction
from piss.old.instructionexecutor import DebugInstructionExecutor
from piss.old.testing import test_raw_input as input_test
from utilities.exceptions import CustomDiscordException, ErrorTooltip, UseRestriction, RestrictedUseException, \
    IncompatibleTargetChannel
from utilities.selection_window import selection_window


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class LocalAdminCog(CustomGroupCog, group_name='admin'):
    def __init__(self, client: BotClient, fact: LocalAdminFactInterface, mod: LocalAdminModerationInterface,
                 pref: PreferencesInterface, db: LocalAdminDataInterface, logger: GlobalLogger,
                 local_logger: LocalLogger) -> None:
        super().__init__(client)
        self.fact = fact
        self.mod = mod
        self.pref = pref
        self.db = db
        self.logger = logger
        self.local_logger = local_logger

    def restricted(self, guild_id: int, user_id: int) -> UseRestriction:
        """
        Returns the highest level restriction block on the given user/guild.
        """
        userban: bool = self.mod.is_banned_user(user_id)
        if userban:
            return UseRestriction.USER
        guildban: bool = self.mod.is_banned_guild(guild_id)
        if guildban:
            return UseRestriction.GUILD
        return UseRestriction.NONE

    def user_authorize_check(self, guild_id: int, user_id: int) -> None:
        """
        Raises Exception if lacking full access to this command suite.
        This is to be handled by the BotClient's Exception handler.
        Does nothing if the user has access.
        """
        restrictions: UseRestriction = self.restricted(guild_id, user_id)
        if restrictions != UseRestriction.NONE:
            raise RestrictedUseException(restrictions)

    def fact_limit_check(self, guild_id: int, text: str, edit: bool = False) -> None:
        """
        Checks given input and sees if it can be created as a fact.
        Will raise an Exception if the check fails.
        :param guild_id: Guild ID to check for
        :param text: Created/updated fact text; used for character limit checking
        :param edit: If true, ignores fact limit check (considers it as replacing the fact)
        :return: Permission.
        """
        if self.mod.is_super_server(guild_id):
            return

        if len(text) > CFG.FACT_CHAR_LIMIT:
            raise RestrictedUseException(UseRestriction.CHAR_LIMIT)

        if not edit:
            if self.fact.get_fact_count(guild_id) >= CFG.FACT_COUNT_MAXIMUM:
                raise RestrictedUseException(UseRestriction.FACT_LIMIT)

    async def kill_switch_check(self, interaction: Interaction) -> bool:
        if self.fact.is_killswitch():
            await self.client.user_feedback(interaction, title='This feature is currently disabled.', ephemeral=True)
            return False
        return True

    # region facts
    @app_commands.command(name='add', description='Add a new local fact. Will be test-compiled, but not in detail.')
    @app_commands.describe(text='The fact to add. Will be tested',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    @app_commands.checks.cooldown(1, CFG.ADD_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def add(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild
        if not await self.kill_switch_check(interaction):
            return
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER)

        self.user_authorize_check(guild.id, interaction.user.id)
        self.fact_limit_check(guild.id, text)

        if not await input_test(self.client, interaction, text, ephemeral):
            return
        self.fact.create_fact(guild.id, interaction.user.id, text)

        await self.logger.local_fact_create(guild, interaction, text)
        await self.local_logger.fact_create(interaction, text)
        await self.client.user_feedback(interaction, title='Success', desc=f'Fact created successfully.',
                                        ephemeral=ephemeral)

    @app_commands.command(name='edit', description='Edit or Remove a local fact.')
    @app_commands.describe(index='The index of the fact you\'re editing.',
                           text='The replacement fact.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    @app_commands.checks.cooldown(1, CFG.EDIT_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def edit(self, interaction: Interaction, index: int, text: str, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER)

        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild
        self.user_authorize_check(guild.id, interaction.user.id)
        self.fact_limit_check(guild.id, text, edit=True)

        if not await input_test(self.client, interaction, text, ephemeral):
            return
        try:
            old: SimpleFactEditorData = self.fact.edit_fact(guild.id, index, text, interaction.user.id)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.local_fact_edit(guild, interaction, old, text)
        await self.local_logger.fact_edit(interaction, guild, old, text)
        await self.client.user_feedback(interaction, ephemeral=ephemeral,
                                        title='Success', desc=f'Fact edited successfully.\n\n'
                                                              f'**Old:**\n{old.text}\n\n**New:**\n{text}')

    @app_commands.command(name='delete', description='Delete a local fact.')
    @app_commands.describe(index='The index of the fact you\'re deleting.',
                           ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    @app_commands.checks.cooldown(1, CFG.DELETE_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def delete(self, interaction: Interaction, index: int, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return

        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild
        try:
            old: SimpleFactEditorData = self.fact.delete_fact(guild.id, index)
        except IndexError:
            await self.client.user_feedback(interaction, title='Index is out of range.', ephemeral=ephemeral)
            return

        await self.logger.local_fact_remove(guild=guild, interaction=interaction, old=old)
        await self.local_logger.fact_remove(interaction, interaction.guild, old)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Success',
                                        desc=f'Fact deleted successfully.\n\n'
                                             f'**Old:**\n{old.text}')

    @app_commands.command(name='preview', description='Allows you to test and preview fact input (runs on P.I.S.S.!)')
    @app_commands.describe(text='The Sequence you\'d like to test.', ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    @app_commands.checks.cooldown(1, CFG.PREVIEW_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def preview(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        await interaction.response.defer(ephemeral=ephemeral, thinking=True)
        await interaction.edit_original_response(
            embed=discord.Embed(description='Performing PISS test.')
        )
        exception: CustomDiscordException | None = None
        description: str = 'If you see this, something went so wrong it executed neither the test nor the exception handler.'
        try:
            compiled: list[Instruction] = parse_variables(text)
            executor: DebugInstructionExecutor = DebugInstructionExecutor(self.client)
            await executor.run(compiled, interaction)
            description = (f'**Taken input:**\n'
                           f'{text}\n'
                           f'\n'
                           f'**Chat output:**\n'
                           f'{executor.output}\n'
                           f'\n'
                           f'**Compiled and executed Instructions:**\n'
                           f'{'\n'.join(f'`{i}`'.replace('InstructionType.', '') for i in compiled)}')
        except CustomDiscordException as e:
            exception = e
        except Exception as e:
            exception = CustomDiscordException(cause=e, tooltip=ErrorTooltip.WIKI)
        if exception is not None:
            description = f'See the attached Embed for additional information on the compilation error.'

        # Create output embed
        embed: discord.Embed = discord.Embed(
            title=f'PISS input {'compiled successfully' if exception is None else 'failed to compile'}',
            description=description + f'\n\nMore information on Debugger output and functionality can be found [here]({CFG.DEBUGGER_OUTPUT_WIKI_URL})'
        )
        embeds = [embed] + ([exception.as_embed()] if exception else [])
        await interaction.edit_original_response(embeds=embeds)

    @app_commands.command(name='help', description='A small introduction on how to use PISS to construct facts.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    async def help(self, interaction: Interaction, ephemeral: bool = True) -> None:
        with open("data/data/admin_help.md", "r", encoding="utf-8") as f:
            markdown_content = f.read()
        nli: int = markdown_content.index('\n')  # find first newline to separate first line as embed title.
        title, other = markdown_content[:nli], markdown_content[nli:]
        title = title.replace('#', '').strip()
        if not title:
            title = 'invalid title formatting'
        if not other:
            other = 'no body content'

        await interaction.response.send_message(
            ephemeral=ephemeral,
            embed=discord.Embed(title=title, description=other)
        )

    @app_commands.command(name='index', description='Exports an overview of Local facts.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION, json='Export data in JSON format.')
    async def index(self, interaction: Interaction, json: bool = False, ephemeral: bool = True, ) -> None:
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER)

        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild

        local_facts: list[SimpleFactEditorData] = self.fact.get_local_facts(guild.id)
        if not local_facts:
            await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Local Facts',
                                            desc='There are no local facts. Go add some!')
            return

        if json:
            out: list[dict] = [v.as_json() for v in local_facts]
            with _io.StringIO(_json.dumps(out, indent=4)) as text_stream:
                # noinspection bad-argument-type
                file = discord.File(
                    fp=text_stream,
                    filename=f"local_fact_data_{guild.id}.json"
                )

                await interaction.response.send_message(
                    embed=discord.Embed(title='Local fact data', description='JSON data attached.'),
                    ephemeral=ephemeral,
                    file=file)
                return

        out: list[str] = []
        for i, fact in enumerate(local_facts):
            author = guild.get_member(fact.author_id)
            if author:
                author = f'{author.name} ({author.id})'
            else:
                author = f'({fact.author_id})'
            out.append(f'{i + 1} {author}: {fact.text}')
        out: str = '\n'.join(out)
        with _io.StringIO(out) as text_stream:
            # noinspection bad-argument-type
            file = discord.File(
                fp=text_stream,
                filename=f"local_fact_data_{guild.id}.txt"
            )
            await interaction.response.send_message(
                ephemeral=ephemeral,
                file=file,
                embed=discord.Embed(title='Local fact data', description='See attached file for fact data.')
            )

    # endregion

    # region preferences
    @app_commands.command(name="autoreply_preferences",
                          description="Leave empty to see current settings.")
    @app_commands.describe(here="If false, edits general server-wide override instead.",
                           numbers="Incremental number replies.", letters='Letter-only replies.',
                           text='Text content replies.')
    async def guild_toggle_preference(self, interaction: Interaction, here: bool, numbers: bool = False,
                                      letters: bool = False, text: bool = False, saying: bool = False,
                                      ephemeral: bool = True) -> None:
        await interaction.response.defer(ephemeral=ephemeral, thinking=True)

        if not here:
            channel: None = None
        elif isinstance(interaction.channel, (TextChannel, VoiceChannel, StageChannel, Thread)):
            channel: TextChannel | VoiceChannel | StageChannel | Thread = interaction.channel
        else:
            raise IncompatibleTargetChannel(interaction.channel, Messageable.__name__)

        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild_id: int = interaction.guild_id

        channel_id: int | None = interaction.channel_id if here else None
        pref: GuildChannelPreferenceData = self.pref.guild_channel_autoreplies_enabled(guild_id, channel_id)
        desc: str = 'Preferences for ' + (f'<#{channel_id}>' if channel_id else '**Server-wide override**') + '\n'
        if not (numbers or letters or text or saying):
            await self.client.user_feedback(interaction, title=desc.removesuffix('\n'),
                                            desc=f'**Number:** {'Off' if not pref.number else 'On'}\n'
                                                 f'**Letter:** {'Off' if not pref.letter else 'On'}\n'
                                                 f'**Text:** {'Off' if not pref.text else 'On'}\n'
                                                 f'**Saying:** {'Off' if not pref.saying else 'On'}\n')
            return

        feat: set[supported_autoreply_features] = set()
        if numbers:
            feat.add('number')
            pref.number = not pref.number
            desc += f'**Number:** {pref.number}\n'
        if letters:
            feat.add('letter')
            pref.letter = not pref.letter
            desc += f'**Letter:** {pref.letter}\n'
        if text:
            feat.add('text')
            pref.text = not pref.text
            desc += f'**Text:** {pref.text}\n'
        if saying:
            feat.add('saying')
            pref.saying = not pref.saying
            desc += f'**Saying:** {pref.saying}\n'

        if not feat.__sizeof__() > 0:
            raise RuntimeError('Set of selected features is 0 even though some feature was selected.')

        # todo: return updated data and then use that to save a DB call.
        self.pref.toggle_autoreply_feature(guild_id, channel_id, feat)
        await self.local_logger.set_channel_preferences(interaction, channel, pref)

        desc = desc.removesuffix('\n')
        await self.client.user_feedback(
            interaction,
            title='Guild autoreply preferences updated',
            desc=desc,
        )

    # endregion

    # region other
    @app_commands.command(name='log', description='Logs administrative usage of the bot to a given channel.')
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION,
                           channel='Channel ID to log in. Leave empty to remove.')
    # todo: support for local logging!
    async def set_log_channel(self, interaction: Interaction,
                              channel: Transform[int, ChannelIDTransformer] | None = None,
                              ephemeral: bool = True) -> None:
        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild

        if not channel:
            self.db.set_log_output(guild.id, None)
            await self.client.user_feedback(interaction, ephemeral=ephemeral, desc='Logging output removed')
            return

        log_channel = guild.get_channel(channel)
        if not log_channel:
            await self.client.user_feedback(interaction, ephemeral=ephemeral,
                                            desc=f'Input channel ID **{channel}** is invalid or not found.')
        if not isinstance(log_channel, Messageable):
            raise IncompatibleTargetChannel(log_channel, Messageable.__name__)

        self.db.set_log_output(guild.id, log_channel.id)
        await self.logger.local_set_log_channel(guild, interaction, log_channel)
        await self.local_logger.set_log_channel(interaction, log_channel)
        await self.client.user_feedback(interaction, ephemeral=ephemeral,
                                        desc=f'Log output channel set to <#{log_channel.id}>')

    @app_commands.command(name="pause",
                          description=f'Pause all application interactions in this channel for {CFG.CHANNEL_PAUSE_DURATION} seconds. Refreshable.', )
    @app_commands.describe(ephemeral=CFG.EPHEMERAL_DESCRIPTION)
    # Hardcoded 75% duration done; so refreshable every 60s with default config.
    @app_commands.checks.cooldown(1, (CFG.CHANNEL_PAUSE_DURATION // 4) * 3, key=lambda i: (i.guild_id, i.channel_id))
    async def pause(self, interaction: Interaction, ephemeral: bool = False) -> None:
        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild

        self.pref.pause_all_in_channel(guild.id, interaction.channel_id, CFG.CHANNEL_PAUSE_DURATION)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Features paused',
                                        desc=f'Features put on pause for another {CFG.CHANNEL_PAUSE_DURATION} seconds.')

    # endregion

    # region autocomplete
    async def _local_fact_index_autocomplete_impl(self, interaction: Interaction, current: int) -> list[Choice[int]]:
        # Always instance available as this is a guild_only command.
        # noinspection bad-assignment
        guild: Guild = interaction.guild

        facts: list[SimpleFactEditorData] = self.fact.get_local_facts(guild.id)
        if not facts:
            return [Choice[int](name='No local facts', value=-1)]

        if not current:
            current = 0
        lower, upper = selection_window(len(facts), current, 11, favour='higher')
        return [
            Choice[int](name=f'{offset + 1}: {fact.text[:80]}', value=offset + 1)
            for offset, fact in enumerate(facts[lower:upper])
        ]

    @edit.autocomplete('index')
    @delete.autocomplete('index')
    async def _local_fact_index_autocomplete_guard(self, interaction: Interaction, current: int) -> list[Choice[int]]:
        return await self.autocomplete_guard(interaction, current, self._local_fact_index_autocomplete_impl, 'index')
    # endregion
