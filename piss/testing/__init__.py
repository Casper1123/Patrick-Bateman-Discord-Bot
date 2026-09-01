from discord import Interaction as _Interaction, Message as _Message, Embed as _Embed

from discorduser.user.abstract import BotClient as _BotClient

from piss.parsing import parse_instructions_from_string as _parse_text
from piss.instructions.abstract import Instruction as _Instruction
from piss.executing.test import TestInstructionExecutor as _TestInstructionExecutor
from piss.exceptions import InstructionParseError as _InstructionParseError, InstructionExecutionError as _InstructionExecutionError


async def test_raw_input(client: _BotClient, interaction: _Interaction | _Message, text: str, ephemeral: bool) -> bool:
    """
    Compiles and test executes given PISS input.
    If unsuccessful, automatically sends information Embed message, assuming it hasn't had any messages sent yet.
    :return: Success.
    """
    # todo: explore complete state space because this is nonsense.
    try:
        compiled: list[_Instruction] = _parse_text(text)
        executor: _TestInstructionExecutor = _TestInstructionExecutor()
        await executor.run(compiled)
    except _InstructionParseError or _InstructionExecutionError as e:
        await client.user_feedback(
            interaction,
            title=f'Input failed {'to compile' if isinstance(e, _InstructionParseError) else 'somewhere in test execution'}.',
            desc=f'Aborting operation. Consider testing using `/admin preview` for more detailed information.\n\n**Input given:**\n{text}',
            ephemeral=ephemeral,
        )
        return False
    return True
