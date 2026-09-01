import re as _re
from re import Match as _Match

# noinspection protected-member
from piss._utils.mem_tools import fetch as _fetch, INITIAL_MEMORY_TYPES
# noinspection protected-member
from piss._utils.symbols import be_map, bounds, doubles, escapes, terminator
from piss.exceptions import InstructionParseError as _InstructionParseError
from piss.instructions.abstract import Instruction as _Instruction
from piss.instructions.build import BuildInstruction as _BuildInstruction
from piss.instructions.memory import MemoryInstruction as _MemoryInstruction
from piss.parsing.parse_order import parse_order as _parse_order
from utilities.exceptions import CustomDiscordException as _CustomDiscordException

MAX_RECURSION_DEPTH: int = 5 # todo: config

# todo: improve feedback information

def _parse_top_level(parse_string: str, recursion_depth: int, memory: dict[str, type], writing: bool) -> list[_Instruction]:
    """
    Decomposes input string into text and Instructions blocks by turning them into Instructions.
    :param parse_string: Input string containing variable blocks.
    :param recursion_depth: Recursion depth.
    :param memory Current given memory.
    :param writing: If the current `parse_string` would be executed inside a writing(*i) environment.
    :return: `parse_string` converted into its composing Instructions.
    """
    if recursion_depth > MAX_RECURSION_DEPTH: raise _InstructionParseError(parse_string, reason='Maximum recursion depth exceeded. Lower the complexity of your input.')

    # Trackers
    instructions: list[_Instruction] = [] # final output for this subsection

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
                instructions.append(_BuildInstruction(text=build))
                build = ''
            opened += 1
        elif char == '}':
            if opened > 0:
                opened -= 1
                if opened == 0:
                    # Insert build into parser
                    instructions += _parse_instruction_block(build, memory, recursion_depth, writing)
                    build = ''
            else:
                raise _InstructionParseError(parse_string, reason=f'Found block-closing symbol at pos {i} before a block-opening symbol.')
        else:
            build += char

        i += 1 # Mandatory, next char
    if opened != 0: raise _InstructionParseError(parse_string, reason=f'Input left with {opened} unclosed scopes.')
    if build: instructions.append(_BuildInstruction(text=build))

    return instructions


def _parse_instruction_block(parse_string: str, memory: dict[str, type], recursion_depth: int, writing: bool) -> list[_Instruction]:
    """
    Determines instruction type(s) and creates instructions using their parameters.
    :param parse_string: Input string
    :param recursion_depth: The current recursion depth, in case a sub-instruction requires recursion.
    :param memory: The memory. Defines variable types for type checking.
    :param writing: The given build string would be parsed as if it is inside a writing(*i) operand.
    :return: Instructions from Build
    """
    if recursion_depth > MAX_RECURSION_DEPTH:
        raise _InstructionParseError(parse_string, 'Maximum recursion depth exceeded. Lower the complexity of your input.')

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

        elif char == terminator:
            if layer_stack:
                build += char
            else:
                subsections.append(build)
                build = ''

        elif char in doubles:
            if char == top_stack:
                layer_stack.pop()
            else:
                layer_stack.append(char)

            build += char

        elif char in bounds:
            build += char
            layer_stack.append(be_map[char])

        elif char in escapes:
            if char == top_stack:
                layer_stack.pop()
                build += char
            else:
                raise _InstructionParseError(build, f'Unexpected escape symbol found. Found {char}, expected {top_stack}')

        else:
            build += char

        i += 1

    if layer_stack: raise _InstructionParseError(build, f'Unescaped layers. Expected **{' '.join(reversed(layer_stack))}**.')
    if build: subsections.append(build)

    # Minor postprocessing
    subsections = [i.strip() for i in subsections]

    # Memory cleanup to not fudge references
    del build, layer_stack, char, escaped, i, n
    # endregion

    # region Step 2: Instruction recognition
    instructions: list[_Instruction] = []

    n: int = len(subsections) # To keep track of if stuff is still required to be done.

    # Go over each subsection and determine containing Instruction based on Signature.
    for i, subsection in enumerate(subsections):
        found: bool = False # Keep track of if an Instruction was found.
        for inst_type in _parse_order:
            for sig, ident in inst_type.signatures():
                match: _Match | None = _re.match(sig, subsection)
                if match:
                    try:
                        instructions.append(inst_type.from_match(match, ident, memory, recursion_depth, writing))
                    except _CustomDiscordException as e:
                        raise e
                    except Exception as e:
                        err = _InstructionParseError(subsection, f'Error occurred when trying to parse input for input ({inst_type.__name__} signature ID {ident})')
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
                raise _InstructionParseError(parse_string, reason=f'Found memory print instruction **{subsection}** at section {i} before end of input.')
            res_type: type | None = _fetch(memory, subsection)
            if res_type is None:
                raise _InstructionParseError(subsection, f'Key {subsection} not found.')
            # todo: supported output memory type?
            instructions.append(_MemoryInstruction(key=subsection))

    return instructions
    # endregion


def parse_instructions_from_string(txt: str, ) -> list[_Instruction]:
    # Parse input string with default values.
    # todo: post-check?
    return _parse_top_level(
        parse_string=txt,
        recursion_depth=0,
        memory=INITIAL_MEMORY_TYPES.copy(),
        writing=False,
    )