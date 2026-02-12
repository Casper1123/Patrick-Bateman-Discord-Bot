from discord import Interaction, Message, Embed

from Rewrite.discorduser import BotClient
from Rewrite.variables_parser import Instruction, parse_variables, InstructionParseError
from Rewrite.variables_parser.instructionexecutor import DebugInstructionExecutor, ParsedExecutionFailure


async def test_raw_input(client: BotClient, interaction: Interaction | Message, text: str, ephemeral: bool) -> bool:
    """
    Compiles and test executes given PISS input.
    If unsuccessful, automatically sends information Embed message, assuming it hasn't had any messages sent yet.
    :return: Success.
    """
    try:
        compiled: list[Instruction] = parse_variables(text)
        executor: DebugInstructionExecutor = DebugInstructionExecutor(client)
        await executor.run(compiled, interaction)
    except InstructionParseError or ParsedExecutionFailure as e:
        await interaction.response.send_message(ephemeral=ephemeral, embed=Embed(
            title=f'Input failed {'to compile' if isinstance(e, InstructionParseError) else 'somewhere in test execution'}.',
            description=f'Aborting operation. Consider testing using `/admin preview` for more detailed information.\n\nInput given:\n`{text}`'))
        return False
    return True