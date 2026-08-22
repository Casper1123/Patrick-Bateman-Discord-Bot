import datetime as _datetime
import re as _re
from re import Match as _Match

from piss.instructions.memory import MemoryInstruction
from piss.parsing.parse_order import parse_order
from piss.exceptions import InstructionParseError
from piss.instructions.abstract import Instruction
from piss.instructions.build import BuildInstruction
# noinspection protected-member
from piss._utils.mem_tools import fetch
from piss.instructions import _be_map, _bounds, _doubles, _escapes, _terminator
from utilities.exceptions import CustomDiscordException

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


# todo: improve feedback information

def _parse_top_level(parse_string: str, recursion_depth: int, memory_stack: list[dict[str, type]], writing: bool) -> list[Instruction]:
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

    i: int = 0 # Position in str
    n: int = len(parse_string)

    build: str = '' # currently building string output / input (for block)
    opened: int = 0  # { Count scope; Decrease when } found

    while i < n:
        # Is this character escaped?
        escaped: bool = i > 0 and build[i - 1] == '\\'

        char: str = parse_string[i]

        if char == '\\':
            # Opened clause to preserve escape symbols until their required layer.
            if escaped or opened > 0:
                build += char
        elif escaped:
            build += char
        elif char == '{':
            if opened == 0 and build:
                instructions.append(BuildInstruction(text=build))
                build = ''
            opened += 1
        elif char == '}':
            if opened > 0:
                opened -= 1
                if opened == 0:
                    # Insert build into parser
                    instructions += _parse_instruction_block(build, memory_stack, recursion_depth, writing)
                    build = ''
            else:
                raise InstructionParseError(parse_string, reason=f'Found block-closing symbol at pos {i} before a block-opening symbol.')
        else:
            build += char

        i += 1 # Mandatory, next char
    if opened != 0: raise InstructionParseError(parse_string, reason=f'Input left with {opened} unclosed scopes.')
    if build: instructions.append(BuildInstruction(text=build))

    return instructions


def _parse_instruction_block(parse_string: str, memory_stack: list[dict[str, type]], recursion_depth: int, writing: bool) -> list[Instruction]:
    """
    Determines instruction type(s) and creates instructions using their parameters.
    :param parse_string: Input string
    :param recursion_depth: The current recursion depth, in case a sub-instruction requires recursion.
    :param memory_stack: The memory stack, layered on scope, of the current scope. Defines variable types for type checking.
    :param writing: The given build string would be parsed as if it is inside a writing(*i) operand.
    :return: Instructions from Build
    """
    if recursion_depth > MAX_RECURSION_DEPTH:
        raise InstructionParseError(parse_string, 'Maximum recursion depth exceeded. Lower the complexity of your input.')

    # region Step 1: separate into instruction subsections.
    subsections: list[str] = [] # Top-level instructions separated by ;
    build: str = '' # Current subsection.

    layer_stack: list[str] = [] # Stack of opened layers for the current subsection.
    # Populated with expected characters, not the bounds that placed them.

    i: int = 0
    n: int = len(parse_string)

    while i < n:
        escaped: bool = i > 0 and parse_string[i - 1] == '\\'
        top_stack: str = '' if not layer_stack else layer_stack[-1]

        char: str = parse_string[i]

        if char == '\\':
            if escaped and not layer_stack:
                build += char

        elif escaped:
            build += char

        elif char == _terminator:
            if layer_stack:
                build += char
            else:
                subsections.append(build)
                build = ''

        elif char in _doubles:
            if char == top_stack:
                layer_stack.pop()
            else:
                layer_stack.append(char)

            build += char

        elif char in _bounds:
            build += char
            layer_stack.append(_be_map[char])

        elif char in _escapes:
            if char == top_stack:
                layer_stack.pop()
                build += char
            else:
                raise InstructionParseError(build, f'Unexpected escape symbol found. Found {char}, expected {top_stack}')

        else:
            build += char

        i += 1

    if layer_stack: raise InstructionParseError(build, f'Unescaped layers. Expected **{' '.join(reversed(layer_stack))}**.')
    if build: subsections.append(build)

    # Minor postprocessing
    subsections = [i.strip() for i in subsections]

    # Memory cleanup to not fudge references
    del build, layer_stack, char, escaped, i, n
    # endregion

    # todo: how the FUCK is the memory stack going to work.
    local_scope: dict[str, type] = {} if memory_stack else INITIAL_MEMORY_TYPES.copy()
    memory_stack.append(local_scope)

    # region Step 2: Instruction recognition
    instructions: list[Instruction] = []

    n: int = len(subsections) # To keep track of if stuff is still required to be done.

    # Go over each subsection and determine containing Instruction based on Signature.
    for i, subsection in enumerate(subsections):
        found: bool = False # Keep track of if an Instruction was found.
        for inst_type in parse_order:
            for sig, ident in inst_type.signatures():
                match: _Match | None = _re.match(sig, subsection)
                if match:
                    try:
                        instructions.append(inst_type.from_match(match, ident, memory_stack, recursion_depth, writing))
                    except CustomDiscordException as e:
                        raise e
                    except Exception as e:
                        err: InstructionParseError = InstructionParseError(subsection, f'Error occurred when trying to parse input for input ({inst_type.__name__} signature ID {ident})')
                        err.cause = e
                        raise err

                    found = True
                    break
            if found: break

        if not found:
            # Perform memory call;
            # 1. If not at the end, cannot perform a memory call for an instruction block
            # 2. See if the key exists
            # 3. See if resulting type is compatible for output.
            if i < n:
                raise InstructionParseError(parse_string, reason=f'Found memory print instruction **{subsection}** at section {i} before end of input.')
            res_type: type | None = fetch(memory_stack, subsection)
            if res_type is None:
                raise InstructionParseError(subsection, f'Key {subsection} not found.')
            # todo: supported output memory type?
            instructions.append(MemoryInstruction(key=subsection))

    return instructions
    # endregion


def parse_instructions_from_string(txt: str, ) -> list[Instruction]:
    # Parse input string with default values.
    # todo: post-check?
    return _parse_top_level(
        parse_string=txt,
        recursion_depth=0,
        memory_stack=[],
        writing=False,
    )