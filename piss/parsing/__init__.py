# todo: two components, string parser with blocks, and one parser that parses vars only.
from typing import Any
import datetime as _datetime

from piss.exceptions import InstructionParseError
from piss.instructions import Instruction
from piss.instructions.build import BuildInstruction

MAX_RECURSION_DEPTH: int = 5
INITIAL_MEMORY_TYPES: dict[str, type] = {
    '\\n': str,

    # interaction target
    'user.id': int,
    'user': str,
    'user.name': str,
    'user.created_at': _datetime.datetime,
    'user.account': str,
    'user.mutual_guilds': int,
    'user.roles': int,  # role count, not the actual roles.

    'self.id': int,
    'self': str,
    'self.name': str,
    'self.created_at': _datetime.datetime,
    'self.account': str,
    'self.roles': int,

    'channel': str,
    'channel.id': int,
    'channel.name': str,
    'channel.created_at': _datetime.datetime,
    'channel.jump_url': str,

    'guild': str,
    'guild.id': int,
    'guild.name': str,
    'guild.created_at': _datetime.datetime,
    'guild.members': int,  # member count
    'guild.roles': int,  # still, role count.

    # guild owner
    'owner.id': int,
    'owner': str,
    'owner.name': str,
    'owner.created_at': _datetime.datetime,
    'owner.mutual_guilds': int,
    'owner.account': str,
    'owner.roles': int,

    # Not always available!
    # 'message': int,
    # 'message.jump_url': str,

    # external
    'local_facts': int,
    'global_facts': int,
    'total_facts': int,
}
SLEEP_TIMER_UPPER_BOUND: float = 3600  # in seconds
SLEEP_TIMER_LOWER_BOUND: float = 0.25


def _parse_top_level(parse_string: str, recursion_depth: int, memory_stack: list[dict[str, Any]], writing: bool) -> list[Instruction]:
    """
    Decomposes input string into text and Instructions blocks by turning them into Instructions.
    :param parse_string: Input string containing variable blocks.
    :param recursion_depth: Recursion depth.
    :param memory_stack: Current given memory stack.
    :param writing: If the current `parse_string` would be executed inside a writing(*i) environment.
    :return: `parse_string` converted into its composing Instructions.
    """
    if recursion_depth > MAX_RECURSION_DEPTH: raise InstructionParseError(parse_string, reason='Maximum recursion depth exceeded. Lower the complexity of your input.')

    # Trackers
    instructions: list[Instruction] = [] # final output for this subsection

    #
    i: int = 0 # Position in str
    n: int = len(parse_string)

    build: str = '' # currently building string output / input (for block)
    opened: int = 0  # { Count scope; Decrease when } found

    while i < n:
        # Is this character backslashed?
        if i == 0: escaped = False
        else: escaped = parse_string[i-1] == '\\'

        char: str = parse_string[i]

        if char == '{':
            if escaped:
                build += char
            else:
                if opened == 0 and build:
                    instructions.append(BuildInstruction(text=build))
                    build = ''
                opened += 1
        elif char == '}':
            if escaped:
                build += char
            else:
                if opened > 0:
                    opened -= 1
                    if opened == 0:
                        # Insert build into parser
                        instructions += _parse_instruction_block(build, memory_stack, recursion_depth, writing)
                        build = ''
                    else:
                        raise InstructionParseError(parse_string, reason=f'Found block-closing symbol at pos {i} before a block-opening symbol.')
        elif char == '\\':
            # Opened clause to preserve escape symbols until their required layer.
            if escaped or opened > 0:
                build += char
        else:
            build += char

        i += 1 # Next char

    if opened != 0: raise InstructionParseError(parse_string, reason=f'Input left with {opened} unclosed states')
    if build: instructions.append(BuildInstruction(text=build))

    return instructions


def _parse_instruction_block(build: str, memory_stack: list[dict[str, type]], depth: int = 0, writing=False) -> list[Instruction]:
    """
    Determines instruction type(s) and creates instructions using their parameters.
    :param build: Input string
    :param depth: The current recursion depth, in case a sub-instruction requires recursion.
    :param memory_stack: The memory stack, layered on scope, of the current scope. Defines variable types for type checking.
    :param writing: The given build string would be parsed as if it is inside a writing(*i) operand.
    :return: Instructions from Build
    """
    if depth > MAX_RECURSION_DEPTH:
        raise InstructionParseError(build, 'Maximum recursion depth exceeded. Lower the complexity of your input.')

def parse_instructions_from_string(txt: str, ) -> list[Instruction]:
    # Parse input string with default values.
    # todo: post-check?
    return _parse_top_level(
        parse_string=txt,
        recursion_depth=0,
        memory_stack=[INITIAL_MEMORY_TYPES.copy()],
        writing=False,
    )