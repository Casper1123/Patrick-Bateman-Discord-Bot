from discord import Interaction, Message, Embed

from discorduser.user.abstract import BotClient
from piss.old import Instruction, parse_variables, InstructionParseError
from piss.old.instructionexecutor import DebugInstructionExecutor, ParsedExecutionFailure


async def test_raw_input(client: BotClient, interaction: Interaction | Message, text: str, ephemeral: bool) -> bool:
    """
    Compiles and test executes given PISS input.
    If unsuccessful, automatically sends information Embed message, assuming it hasn't had any messages sent yet.
    :return: Success.
    """
    # todo: explore complete state space because this is nonsense.
    try:
        compiled: list[Instruction] = parse_variables(text)
        executor: DebugInstructionExecutor = DebugInstructionExecutor(client)
        await executor.run(compiled, interaction)
    except InstructionParseError or ParsedExecutionFailure as e:
        # noinspection unresolved-references
        await interaction.response.send_message(
            ephemeral=ephemeral,
            embed=Embed(
                title=f'Input failed {'to compile' if isinstance(e, InstructionParseError) else 'somewhere in test execution'}.',
                description=f'Aborting operation. Consider testing using `/admin preview` for more detailed information.\n\n**Input given:**\n{text}'
            )
        )
        return False
    return True
