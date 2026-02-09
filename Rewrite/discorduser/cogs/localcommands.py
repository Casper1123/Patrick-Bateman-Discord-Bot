import discord
from discord import app_commands, Interaction
from discord.ext import commands
from enum import Enum

from ...data.data_interface_abstracts import LocalAdminDataInterface
from ...utilities.exceptions import CustomDiscordException
from ...variables_parser import parse_variables, Instruction
from ...variables_parser.instructionexecutor import InstructionExecutor, DebugInstructionExecutor

DEBUGGER_OUTPUT_WIKI_URL = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'

class UserRestriction(Enum):
    NONE = 0,
    GUILD = 1,
    USER = 2,

class RestrictedAccessException(CustomDiscordException):
    def __init__(self, restriction: UserRestriction):
        super().__init__(f'Your action has been interrupted; ' + (
            'This guild has been restricted from using this feature.' if restriction == UserRestriction.GUILD
            else 'You cannot use this command.'), refer_wiki=True) # todo: write on the wiki what's going on when you see this


@app_commands.default_permissions(administrator=True)
class LocalAdminCog(commands.Cog, name='admin'):
    def __init__(self, client: commands.bot,  db: LocalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    def restricted(self, guild_id: int, user_id: int) -> UserRestriction:
        userban: bool = self.db.is_banned_user(user_id)
        if userban:
            return UserRestriction.USER
        guildban: bool = self.db.is_banned_guild(guild_id)
        if guildban:
            return UserRestriction.GUILD
        return UserRestriction.NONE

    def user_authorize_check(self, guild_id: int, user_id: int) -> None:
        restrictions: UserRestriction = self.restricted(guild_id, user_id)
        if restrictions != UserRestriction.NONE:
            raise RestrictedAccessException(restrictions)

    # region facts
    # fact add
    # fact edit -> empty input removes
    # fact help
    # fact preview
    # endregion

    async def add(self, interaction: Interaction, text: str) -> None:
        self.user_authorize_check(interaction.guild.id, interaction.user.id)
        # todo: is super server, otherwise check for bounds restriction? -> char limit / fact count.
        # todo: duplicate check?
        # todo: compilation check
        self.db.create_fact(interaction.guild.id, interaction.user.id, text)

    async def edit(self, interaction: Interaction, index: int, text: str = None) -> None:
        ...

    async def help(self, interaction: Interaction) -> None:
        ... # todo: implement sending basic MD data over.

    async def preview(self, interaction: Interaction, text: str, ephemeral: bool = True) -> None:
        if ephemeral:
            await interaction.response.defer(ephemeral=ephemeral, thinking=False)
        compiled: list[Instruction] = parse_variables(text)
        executor: DebugInstructionExecutor = DebugInstructionExecutor(self.client)
        exception: CustomDiscordException | None = None
        try:
            await executor.run(compiled, interaction)
        except CustomDiscordException as e:
            exception = e

        # Create output embed
        embed: discord.Embed = discord.Embed(
            title='PISS test results:',
            description=f'Your input {'compiled sucessfully' if exception is None else 'failed to compile'}.'
                        f'\n{f'It outputs as follows:\n```\n{executor.output}\n```' if exception is None else 'See the attached Embed for additional information on the compilation error.'}' +
                        f'\n\nMore information on Debugger output and functionality can be found [here]({DEBUGGER_OUTPUT_WIKI_URL})'
        )
        embeds = [embed] + ([exception.as_embed()] if exception else [])
        await interaction.edit_original_response(embeds=embeds)