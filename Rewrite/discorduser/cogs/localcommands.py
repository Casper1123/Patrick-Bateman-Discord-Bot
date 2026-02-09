import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from enum import Enum

from .. import BotClient
from ...data.data_interface_abstracts import LocalAdminDataInterface
from ...utilities.exceptions import CustomDiscordException
from ...variables_parser import parse_variables, Instruction, InstructionParseError
from ...variables_parser.instructionexecutor import DebugInstructionExecutor, ParsedExecutionFailure
from ...variables_parser.testing import test_raw_input as input_test

DEBUGGER_OUTPUT_WIKI_URL = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'
FACT_COUNT_MAXIMUM: int = 50
FACT_CHAR_LIMIT: int = 256

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
        super().__init__(f'Your action has been interrupted; ' + reasons[restriction], refer_wiki=True) # todo: write on the wiki what's going on when you see this


@app_commands.default_permissions(administrator=True)
class LocalAdminCog(commands.Cog, name='admin'):
    def __init__(self, client: BotClient,  db: LocalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

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


    async def killswitch_check(self, interaction: Interaction) -> bool:
        if self.client.local_fact_killswitch:
            await interaction.response.send_message(ephemeral=True, content='This feature is currently disabled.')
            return False
        return True

    # region facts
    # fact add
    # fact edit -> empty input removes
    # fact help
    # fact preview
    # endregion

    async def add(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if not await self.killswitch_check(interaction):
            return
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        # todo: is super server, otherwise check for bounds restriction? -> char limit / fact count.
        # todo: duplicate check?
        if not await input_test(self.client, interaction, text, ephemeral):
            return
        success: bool = self.db.create_fact(interaction.guild.id, interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title='Success' if success else 'Failure', description=f'Fact added successfully.' if success else 'Fact creation failed.'))
        # todo: log this action

    async def edit(self, interaction: Interaction, index: int, text: str = None, ephemeral: bool = True) -> None:
        if not await self.killswitch_check(interaction):
            return
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        delete: bool = text is None
        # todo: is super server, otherwise check for bounds restriction? -> char limit / fact count.
        # todo: duplicate check?
        if not delete:
            if not await input_test(self.client, interaction, text, ephemeral):
                return
        success: bool = self.db.edit_fact(interaction.guild_id, 0, 'old', interaction.user.id, text)
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(title='Success' if success else 'Failure',
                                                                        description=f'Fact {'deleted' if delete else 'edited'} successfully.' if success else f'Fact {'deletion' if delete else 'edit'} failed.'))
        # todo: log this action.


    async def help(self, interaction: Interaction) -> None:
        ... # todo: implement sending basic MD data over.

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
            exception = CustomDiscordException(cause=e, refer_wiki=True)
        if exception is not None:
            description = f'See the attached Embed for additional information on the compilation error.'

        # Create output embed
        embed: discord.Embed = discord.Embed(
            title=f'PISS input {'compiled sucessfully' if exception is None else 'failed to compile'}',
            description=description + f'\n\nMore information on Debugger output and functionality can be found [here]({DEBUGGER_OUTPUT_WIKI_URL})'
        )
        embeds = [embed] + ([exception.as_embed()] if exception else [])
        await interaction.edit_original_response(embeds=embeds)