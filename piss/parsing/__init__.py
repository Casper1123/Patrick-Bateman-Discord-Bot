# todo: two components, string parser with blocks, and one parser that parses vars only.
from typing import Any

from piss.exceptions import InstructionParseError
from piss.instructions import Instruction
from piss.instructions.build import BuildInstruction

MAX_RECURSION_DEPTH: int = 5

def parse_variables(parse_string: str, depth: int = 0, memstack: list[dict[str, Any]] | None = None, writing: bool = False) -> list[Instruction]:
    """
    Decomposes input string into text and command blocks by turning them into Instructions.
    :param parse_string: Input string containing variable blocks.
    :param depth: Recursion depth.
    :param memstack: Current given memory stack.
    :param writing: If the current `parse_string` would be executed inside of a writing(*i) environment.
    :return: `parse_string` converted into its composing Instructions.
    """
    recursion_depth = depth
    if recursion_depth > MAX_RECURSION_DEPTH:
        raise InstructionParseError(parse_string,
                                    'Maximum recursion depth exceeded. Lower the complexity of your input.')

    # mem: dict[str, type] = INITIAL_MEMORY_TYPES.copy() if not memstack else {}  # local memory todo: move to var parser
    # memstack = [mem] if not memstack else memstack + [mem]
    instructions: list[Instruction] = []
    i: int = 0
    build: str = ""
    depth: int = 0  # count opened brackets. We consider the var closed when back to 0.
    while i < len(parse_string):
        char: str = parse_string[i]

        if char == "{":
            if parse_string[i - 1] == '\\' and i > 0:  # ensure doesn't check end of string but char in front
                build += char
            elif i == 0 or parse_string[
                i - 1] != '\\' and build and depth == 0:  # In a variable now. Previous build needs to be exited.
                if build != '':
                    instructions.append(BuildInstruction(text=build))
                    build = ""
                depth += 1
            else:
                build += char
                depth += 1
        elif char == "}":
            if parse_string[i - 1] == '\\':
                build += char
            else:
                if depth > 1:
                    build += char
                depth -= 1

            if depth == 0:
                instructions += Instruction.from_string(build, depth=recursion_depth, memstack=memstack,
                                                        writing=writing)
                build = ""
        else:
            build += char
        i += 1
    if build: instructions.append(Instruction(InstructionType.BUILD, content=build))

    return instructions



def parse_instructions_from_string(txt: str, ) -> list[Instruction]:
    raise NotImplementedError()