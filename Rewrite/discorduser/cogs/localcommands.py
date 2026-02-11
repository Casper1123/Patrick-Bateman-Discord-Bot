import io as _io
import json as _json
import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from enum import Enum

from .. import BotClient
from ..logger.logger import Logger
from ..logger.local_logger import LocalLogger
from ...data.data_interface_abstracts import LocalAdminDataInterface, FactEditorData
from ...utilities.exceptions import CustomDiscordException, ErrorTooltip
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import DebugInstructionExecutor
from ...variables_parser.testing import test_raw_input as input_test

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


class RestrictedUseException(CustomDiscordException):
    def __init__(self, restriction: UseRestriction):
        reasons: dict[UseRestriction, str] = {
            UseRestriction.NONE: 'An unlisted external reason has prevented you from performing this action. Seeing this usually means you\'re an outlier or something went wrong on our side.',
            UseRestriction.GUILD: 'This guild has been restricted from using this feature.',
            UseRestriction.USER: 'You cannot use this feature.',

            UseRestriction.FACT_LIMIT: 'This guild has hit the maximum number of Facts. Remove some to make space.',
            UseRestriction.CHAR_LIMIT: 'Your input was too long.'
        }
        super().__init__(f'Your action has been interrupted; ' + reasons[restriction], tooltip=ErrorTooltip.NONE) # todo: write on the wiki what's going on when you see this


@app_commands.default_permissions(administrator=True)
class LocalAdminCog(commands.Cog, name='admin'):
    def __init__(self, client: BotClient,  db: LocalAdminDataInterface, logger: Logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger
        self.local_logger = LocalLogger(self.client)

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
        if self.client.local_fact_kill_switch:
            await interaction.response.send_message(ephemeral=True, content='This feature is currently disabled.')
            return False
        return True

    # region facts
    @app_commands.command(name='add', description='Add a new local fact. Will be test-compiled, but not in detail.')
    @app_commands.describe(text='The fact to add. Will be tested',
                           ephemeral='Hide the message from other users.')
    @app_commands.checks.cooldown(1, ADD_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def add(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        self.fact_limit_check(interaction.guild.id, text)
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        success: bool = self.db.create_fact(interaction.guild.id, interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title='Success' if success else 'Failure', description=f'Fact added successfully.' if success else 'Fact creation failed.'))
        await self.logger.fact_create(interaction, text)
        await self.local_logger.fact_create(interaction, text)

    @app_commands.command(name='edit', description='Edit or Remove a local fact. Leave the text empty to remove.')
    @app_commands.describe(index='The index of the fact you\'re editing/removing',
                           text='The replacement fact. Leave empty to remove the original.',
                           ephemeral='Hide the message from other users.')
    @app_commands.checks.cooldown(1, EDIT_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def edit(self, interaction: Interaction, index: int, text: str = None, ephemeral: bool = True) -> None:
        if not await self.kill_switch_check(interaction):
            return
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        delete: bool = text is None
        self.fact_limit_check(interaction.guild.id, text, edit=True)
        if not delete:
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        old: FactEditorData = self.db.get_local_fact(interaction.guild.id, index)
        success: bool = self.db.edit_fact(interaction.guild_id, old.author_id, old.text, interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title='Success' if success else 'Failure',
                                                                        description=f'Fact {'deleted' if delete else 'edited'} successfully.' if success else f'Fact {'deletion' if delete else 'edit'} failed.'))
        await self.logger.fact_edit(interaction, text, old)
        await self.local_logger.fact_edit(interaction, old, index, text)

    @app_commands.command(name='preview', description='Allows you to test and preview fact input (runs on PISS!)')
    @app_commands.describe(text='The Sequence you\'d like to test.', ephemeral='Hide the message from other users.')
    @app_commands.checks.cooldown(1, PREVIEW_COOLDOWN_SECONDS, key=lambda i: (i.guild_id, i.user.id))
    async def preview(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if ephemeral:
            await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(description='Performing PISS test.'))
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
    @app_commands.describe(ephemeral='Hide the message from other users.')
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

        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title=title, description=other))

    @app_commands.command(name='index', description='Exports an overview of Local facts. Can be exported to JSON for easier automated use.')
    @app_commands.describe(ephemeral='Hide the message from other users.', json='Export the facts to an attached JSON file instead.')
    async def index(self, interaction: Interaction, ephemeral: bool = True, json: bool = False) -> None:
        local_facts: list[FactEditorData] = self.db.get_local_facts(interaction.guild.id)
        if not local_facts:
            await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title='Local Facts', description='There are no local facts. Go add some!'))
            return

        if json:
            out: list[dict[str, str | int]] = [{'text': v.text, 'author_id': v.author_id} for v in local_facts]
            with _io.StringIO(_json.dumps(out, indent=4)) as text_stream:
                file = discord.File(fp=text_stream, filename=f"local_fact_data_{interaction.guild.id}.json")

                await interaction.response.send_message(embed=Embed(title='Local fact data', description='JSON data attached.'), ephemeral=True, file=file)
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
            await interaction.response.send_message(ephemeral=ephemeral, file=file, embed=Embed(title='Local fact data', description='See attached file for fact data.'))

    @app_commands.command(name='log', description='Logs administrative usage of the bot to a given channel.')
    @app_commands.describe(ephemeral='Hide the message from other users.', channel='Channel ID to log in. Requires writing permission. Leave empty to disable.')
    async def log(self, interaction: Interaction, channel: int = None, ephemeral: bool = True) -> None:
        if not channel:
            self.db.set_log_output(interaction.guild.id, None)
            await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(description='Logging output removed.'))
            return

        logchannel = interaction.guild.get_channel(channel)
        if not logchannel:
            await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(description=f'Input channel ID **{channel}** is invalid or not found.\n'))

        self.db.set_log_output(interaction.guild.id, logchannel.id)
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(description=f'Log output channel set to <#{logchannel.id}>'))
        # todo: Choice to display current value.
    # endregion