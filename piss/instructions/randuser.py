from re import Match as _Match
from typing import TypeAlias as _TypeAlias, Literal as _Literal

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError


UserAttributeOptions: _TypeAlias = _Literal['id', 'name', 'account', 'created_at', 'roles', 'mutual_guilds']


class RandomUserInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^tru\((?P<num>-?\d+)(?:,\s*(?P<attr>\w+))?\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type RandomUser')

        num = match.group('num')
        attr = match.group('attr')

        try:
            num = int(num)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'**{num}** is not a Python recognized integer.')

        if not attr:
            attr = 'account'
        if attr not in UserAttributeOptions:
            raise _InstructionParseError(match.group(0), f'Incompatible attribute.\n'
                                                    f'Received: **{attr}**.\n'
                                                    f'Expected: Element in **{UserAttributeOptions}**.')
        RandomUserInstruction(index=num, attribute=attr)

    def __init__(self, index: int, attribute: UserAttributeOptions) -> None:
        self.index = index
        self.attribute = attribute