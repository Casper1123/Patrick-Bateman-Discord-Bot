from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError
from utilities.exceptions import ErrorTooltip


option_bounds: list[str] = ['\'', '"']

class ChoiceInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^choice\(\s*(?P<options>.*)\s*\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Choice')

        options = match.group('options').strip()
        if not options:
            raise _InstructionParseError(match.group(0),
                                        f'CHOICE Instruction did not receive anything to choose from.')
        if not options[0] in option_bounds:
            raise _InstructionParseError(match.group(0),
                                        f'CHOICE Instruction did not receive input starting with a valid option boundary.\n'
                                        f'Received: **{options[0]}**.\n'
                                        f'Expected: *One of* **{option_bounds}**.\n')

        build_option: str = ''
        chosen_bound: str = options[0]
        options_raw: list[str] = []
        # todo: needs to rely on a stack system where layering will working properly.
        # todo: remake entirely.
        # Solution: when opening, throw bound on top of the stack. Use known bounds variables and parsing.
        # If the stack is empty, the next character MUST be a ,
        # Once that was encountered, ignore any spaces until the known bound is found.
        # Any non-picked bound is tossed aside
        i: int = 1
        layer_stack: list[str] = [chosen_bound]
        jumping: int = 0  # 0: in string, 1: right after, 2: spaces optional
        while i < len(options):
            char = options[i]
            # We are outside a variable
            if jumping != 0:
                if jumping == 1 and char == ',':
                    jumping = 2
                elif jumping == 2 and char == ' ':
                    pass
                elif jumping == 2 and char == chosen_bound:
                    layer_stack.append(chosen_bound)
                    jumping = 0
                else:
                    raise _InstructionParseError(options,
                                                f'CHOICE Instruction ran into parsing error while jumping between options (stage **{jumping}**).\n'
                                                f'Received: **{options[i]}**.\n'
                                                f'Expected: **{',' if jumping == 1 else chosen_bound}**.')
            else:
                escaped: bool = i > 0 and options[i - 1] == '\\'
                if escaped:
                    build_option += char
                # We are in a var.
                # Exiting the var.
                elif len(layer_stack) == 1 and layer_stack[-1] == chosen_bound == char:
                    # empty option build after appending, then set jumping var.
                    options_raw.append(build_option)
                    layer_stack.pop()
                    build_option = ''
                    jumping = 1
                # Character is a doubles bound
                elif char in doubles:
                    # Check if it is a bound or escape
                    if len(layer_stack) > 0 and layer_stack[-1] == char:
                        # escape
                        layer_stack.pop()
                    else:  # todo: this does not cover all cases. Remake.
                        # bound
                        layer_stack.append(char)
                    build_option += char
                elif char in bounds:
                    layer_stack.append(char)
                    build_option += char
                elif char in escapes:
                    if not layer_stack:
                        raise InstructionParseError(options,
                                                    f'CHOICE Instruction parsing encountered unescaped escaping character before encountering any bounding characters.\n'
                                                    f'Received: **{char}**')
                    # escape has to be on top
                    top = layer_stack[-1]
                    top_escape = be_map[top]
                    if char == top_escape:
                        layer_stack.pop()
                        build_option += char
                    else:
                        raise InstructionParseError(build_option + char,
                                                    reason=f'Encountered unescaped {char} before encountering {top_escape}')
                else:
                    build_option += char
            i += 1