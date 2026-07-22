import io as _io
import json as _json
from enum import Enum

import discord
from discord import app_commands, Interaction
from discord.ext import commands

from Rewrite.data.interfaces.pref import GuildChannelPreferenceData, PreferencesInterface
from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.discorduser.logger import Logger
from Rewrite.discorduser.logger.local_logger import LocalLogger
from Rewrite.data.interfaces.data import LocalAdminDataInterface, FactEditorData
from Rewrite.utilities.exceptions import CustomDiscordException, ErrorTooltip
from Rewrite.piss import parse_variables, Instruction
from Rewrite.piss.instructionexecutor import DebugInstructionExecutor
from Rewrite.piss.testing import test_raw_input as input_test

DEBUGGER_OUTPUT_WIKI_URL = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'
FACT_COUNT_MAXIMUM: int = 50
FACT_CHAR_LIMIT: int = 256

PREVIEW_COOLDOWN_SECONDS: float = 5.0
EDIT_COOLDOWN_SECONDS: float = 5.0
ADD_COOLDOWN_SECONDS: float = 5.0

class UseRestriction(Enum):
    NONE = 0,
    GUILD = 1,
    USER = 2,

    FACT_LIMIT = 4
    CHAR_LIMIT = 5

reasons: dict[UseRestriction, str] = {
        UseRestriction.NONE: 'An unlisted external reason has prevented you from performing this action. Seeing this usually means you\'re an outlier or something went wrong on our side.',
        UseRestriction.GUILD: 'This guild has been restricted from using this feature.',
        UseRestriction.USER: 'You cannot use this feature.',

        UseRestriction.FACT_LIMIT: 'This guild has hit the maximum number of Facts. Remove some to make space.',
        UseRestriction.CHAR_LIMIT: 'Your input was too long.'
    }

class RestrictedUseException(CustomDiscordException):
    def __init__(self, restriction: UseRestriction):
        super().__init__(f'Your action has been interrupted; ' + reasons[restriction], tooltip=ErrorTooltip.NONE) # todo: write on the wiki what's going on when you see this


# Unfortunately has to be 1 Cog class
# todo: move functions and import those
@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class LocalAdminCog(commands.Cog, name='admin'):
    def __init__(self, client: BotClient, db: LocalAdminDataInterface, pref: PreferencesInterface, logger: Logger) -> None:
        self.client = client
        self.db = db
        self.pref = pref
        self.logger = logger
        self.local_logger = LocalLogger(self.client, db)

    def restricted(self, guild_id: int, user_id: int) -> UseRestriction:
        """
        Returns the highest level restriction block on the given user/guild.
        """
        userban: bool = self.db.is_banned_user(user_id)
        if userban:
            return UseRestriction.USER
        guildban: bool = self.db.is_banned_guild(guild_id)
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
        if self.db.is_super_server(guild_id):
            return

        if len(text) > FACT_CHAR_LIMIT:
            raise RestrictedUseException(UseRestriction.CHAR_LIMIT)

        if not edit:
            if self.db.get_fact_count(guild_id) >= FACT_COUNT_MAXIMUM:
                raise RestrictedUseException(UseRestriction.FACT_LIMIT)

    async def kill_switch_check(self, interaction: Interaction) -> bool:
        if self.db.is_killswitch():
            await self.client.user_feedback(interaction, title='This feature is currently disabled.', ephemeral=True)
            return False
        return True

    # region facts
    @app_commands.command(name='add', description='Add a new local fact. Will be test-compiled, but not in detail.')
    @app_commands.describe(text='The fact to add. Will be tested',
                           ephemeral='Hide this command for other users.')
    @app_commands.checks.cooldown(1, ADD_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def add(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER) # todo: check for duplicates!
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        self.fact_limit_check(interaction.guild.id, text)
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        self.db.create_fact(interaction.guild.id, interaction.user.id, text)
        await self.logger.fact_create(interaction, text)
        await self.local_logger.fact_create(interaction, text)
        await self.client.user_feedback(interaction, title='Success', desc=f'Fact added successfully.', ephemeral=ephemeral)

    @app_commands.command(name='edit', description='Edit or Remove a local fact. Leave the text empty to remove.')
    @app_commands.describe(index='The index of the fact you\'re editing/removing',
                           text='The replacement fact. Leave empty to remove the original.',
                           ephemeral='Hide this command for other users.')
    @app_commands.checks.cooldown(1, EDIT_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def edit(self, interaction: Interaction, index: int, text: str = None, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER)
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        delete: bool = text is None
        self.fact_limit_check(interaction.guild.id, text, edit=True) # todo: check for duplicates!
        if not delete:
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        old: FactEditorData = self.db.get_local_fact(interaction.guild.id, index)
        self.db.edit_fact(interaction.guild_id, old.author_id, old.text, interaction.user.id, text)
        await self.logger.fact_edit(interaction, text, old)
        await self.local_logger.fact_edit(interaction, old, index, text)
        await self.client.user_feedback(interaction, ephemeral=ephemeral,
                                        title='Success', desc=f'Fact {'deleted' if delete else 'edited'} successfully.'
                                                                f'\n# Old:\n`{old.text}`\n\n# New:\n`{text}`')

    @app_commands.command(name='preview', description='Allows you to test and preview fact input (runs on PISS!)')
    @app_commands.describe(text='The Sequence you\'d like to test.', ephemeral='Hide this command for other users.')
    @app_commands.checks.cooldown(1, PREVIEW_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def preview(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if ephemeral:
            await interaction.response.send_message(ephemeral=ephemeral, embed=discord.Embed(description='Performing PISS test.'))
        exception: CustomDiscordException | None = None
        description: str = 'If you see this, something went so wrong it executed neither the test nor the exception handler.'
        try:
            compiled: list[Instruction] = parse_variables(text)
            executor: DebugInstructionExecutor = DebugInstructionExecutor(self.client)
            await executor.run(compiled, interaction)
            description = (f'# Taken input:\n'
                           f'`{text}`\n'
                           f'\n'
                           f'# Chat output:\n'
                           f'`{executor.output}`\n'
                           f'\n'
                           f'# Compiled and executed Instructions:\n'
                           f'{'\n'.join(f'`{i}`'.replace('InstructionType.', '') for i in compiled)}')
        except CustomDiscordException as e:
            exception = e
        except Exception as e:
            exception = CustomDiscordException(cause=e, tooltip=ErrorTooltip.WIKI)
        if exception is not None:
            description = f'See the attached Embed for additional information on the compilation error.'

        # Create output embed
        embed: discord.Embed = discord.Embed(
            title=f'PISS input {'compiled sucessfully' if exception is None else 'failed to compile'}',
            description=description + f'\n\nMore information on Debugger output and functionality can be found [here]({DEBUGGER_OUTPUT_WIKI_URL})'
        )
        embeds = [embed] + ([exception.as_embed()] if exception else [])
        await interaction.edit_original_response(embeds=embeds)

    @app_commands.command(name='help', description='A small introduction on how to use PISS to construct facts.')
    @app_commands.describe(ephemeral='Hide this command for other users.')
    async def help(self, interaction: Interaction, ephemeral: bool = True) -> None:
        with open("data/admin_help.md", "r", encoding="utf-8") as f:
            markdown_content = f.read()
        nli: int = markdown_content.index('\n') # find first newline to separate first line as embed title.
        title, other = markdown_content[:nli], markdown_content[nli:]
        title = title.replace('#', '').strip()
        if not title:
            title = 'invalid title formatting'
        if not other:
            other = 'no body content'

        await interaction.response.send_message(ephemeral=ephemeral, embed=discord.Embed(title=title, description=other))

    @app_commands.command(name='index', description='Exports an overview of Local facts. Can be exported to JSON for easier automated use.')
    @app_commands.describe(ephemeral='Hide this command for other users.', json='Export the facts to an attached JSON file instead.')
    async def index(self, interaction: Interaction, ephemeral: bool = True, json: bool = False) -> None:
        if interaction.user.bot:
            raise RestrictedUseException(UseRestriction.USER)
        local_facts: list[FactEditorData] = self.db.get_local_facts(interaction.guild.id)
        if not local_facts:
            await self.client.user_feedback(interaction, ephemeral=ephemeral, title='Local Facts', desc='There are no local facts. Go add some!')
            return

        if json:
            out: list[dict[str, str | int]] = [{'text': v.text, 'author_id': v.author_id} for v in local_facts]
            with _io.StringIO(_json.dumps(out, indent=4)) as text_stream:
                file = discord.File(fp=text_stream, filename=f"local_fact_data_{interaction.guild.id}.json")

                await interaction.response.send_message(embed=discord.Embed(title='Local fact data', description='JSON data attached.'), ephemeral=True, file=file)
                return

        out: list[str] = []
        for i, fact in enumerate(local_facts):
            author = interaction.guild.get_member(fact.author_id)
            if author:
                author = author.name
            else:
                author = fact.author_id
            out.append(f'{i+1} ({author}): {fact.text}')
        out: str = '\n'.join(out)
        with _io.StringIO(out) as text_stream:
            file = discord.File(fp=text_stream, filename=f"local_fact_data_{interaction.guild.id}.txt")
            await interaction.response.send_message(ephemeral=ephemeral, file=file, embed=discord.Embed(title='Local fact data', description='See attached file for fact data.'))

    @app_commands.command(name='log', description='Logs administrative usage of the bot to a given channel.')
    @app_commands.describe(ephemeral='Hide this command for other users.', channel='Channel ID to log in. Requires writing permission. Leave empty to disable.')
    async def log(self, interaction: Interaction, channel: int = None, ephemeral: bool = True) -> None:
        # todo: autocomplete with current channel, having the text display which channel it is set to ('click to set to this channel')
        # todo: parse <#id> input, so change input to string.
        if not channel:
            self.db.set_log_output(interaction.guild.id, None)
            await self.client.user_feedback(interaction, ephemeral=ephemeral, desc='Logging output removed')
            return

        logchannel = interaction.guild.get_channel(channel)
        if not logchannel:
            await self.client.user_feedback(interaction, ephemeral=ephemeral, desc=f'Input channel ID **{channel}** is invalid or not found.')

        self.db.set_log_output(interaction.guild.id, logchannel.id)
        await self.client.user_feedback(interaction, ephemeral=ephemeral, desc=f'Log output channel set to <#{logchannel.id}>')
        # todo: Choice to display current value.
    # endregion
    # region preferences
    @app_commands.command(name="autoreply_preferences",
                          description="Toggle automatic features for this, or all, channels. Set to True to toggle.")
    @app_commands.describe(here="If false, edits general server-wide override instead.",
                           numbers="Incremental number replies.", letters='Letter-only replies.',
                           text='Text content replies.')
    async def guild_toggle_preference(self, interaction: discord.Interaction, here: bool, numbers: bool = False,
                                      letters: bool = False, text: bool = False, saying: bool = False, ephemeral: bool = True) -> None:
        await interaction.response.defer(ephemeral=ephemeral, thinking=True)
        guild_id: int = interaction.guild_id
        channel_id: int | None = interaction.channel_id if here else None
        pref: GuildChannelPreferenceData = self.pref.guild_channel_autoreplies_enabled(guild_id, channel_id)
        desc: str = 'Preferences for ' + (f'<#{channel_id}>' if channel_id else '**Server-wide override**') + '\n'
        if not (numbers or letters or text or saying):
            await self.client.user_feedback(interaction, title=desc.removesuffix('\n'), desc=f'**Number:** {'Off' if not pref.number else 'On'}\n'
                                                                                     f'**Letter:** {'Off' if not pref.letter else 'On'}\n'
                                                                                     f'**Text:** {'Off' if not pref.text else 'On'}\n'
                                                                                     f'**Saying:** {'Off' if not pref.saying else 'On'}\n')
            return

        feat: set[_supp_autr_features] = set()  # noqa because empty set
        if numbers:
            feat.add('number')
            desc += f'**Number:** {not pref.number}\n'
        if letters:
            feat.add('letter')
            desc += f'**Letter:** {not pref.letter}\n'
        if text:
            feat.add('text')
            desc += f'**Text:** {not pref.text}\n'
        if saying:
            feat.add('saying')
            desc += f'**Saying:** {not pref.saying}\n'

        assert feat.__sizeof__() > 0, 'Set of selected features is 0 even though some feature was selected.'

        self.pref.toggle_autoreply_feature(guild_id, channel_id, feat)

        desc = desc.removesuffix('\n')
        await self.client.user_feedback(interaction,
            title='Guild autoreply preferences updated',
            desc=desc,
        )
    # endregion