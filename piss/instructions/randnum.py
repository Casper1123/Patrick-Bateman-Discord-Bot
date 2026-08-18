from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError


class RandomNumberInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^rand(om)?\((?P<a>-?\d+),\s?(?P<b>-?\d+)\)$', 0), # todo: make b optional s.t. it is 0-a (inclusive)

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type RandomNumber')

        a = match.group('a')
        b = match.group('b')
        try:
            a = int(a)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'**{a}** is not a Python-recognized integer.')
        try:
            b = int(b)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'**{b}** is not a Python-recognized integer.')
        if a > b:
            raise _InstructionParseError(match.group(0),
                                        f'**left ({a})** should not be greater than **right ({b})**.')
        return RandomNumberInstruction(a, b)

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b