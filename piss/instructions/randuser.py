from re import Match as _Match
from typing import TypeAlias as _TypeAlias, Literal as _Literal, get_args

from piss.exceptions import InstructionParseError as _InstructionParseError
from piss.instructions.abstract import Instruction as _Instruction

UserAttributeOptions = _Literal['id', 'name', 'account', 'created_at', 'roles', 'mutual_guilds']
_checkable_options: set[str] = set(get_args(UserAttributeOptions))


class RandomUserInstruction(_Instruction):
    def __str__(self) -> str:
        return super().__str__() + f'[i={self.index}; attr={self.attribute}]'

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^tru\((?P<num>-?\d+)(?:,\s*(?P<attr>\w+))?\)$', 0),
        # todo: support suffixing with .attrib as opposed to just (id, attrib)

    @staticmethod
    def from_match(match: _Match, ident: int, memory: dict[str, type], recursion_depth: int,
                   writing: bool) -> RandomUserInstruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type RandomUser')

        num = match.group('num')
        attr = match.group('attr')

        try:
            num = int(num)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'**{num}** is not a Python recognized integer.')

        if not attr:
            attr = 'name'
        if attr not in _checkable_options:
            raise _InstructionParseError(match.group(0), f'Incompatible attribute.\n'
                                                    f'Received: **{attr}**.\n'
                                                    f'Expected: Element in **{UserAttributeOptions}**.')
        return RandomUserInstruction(index=num, attribute=attr)

    def __init__(self, index: int, attribute: UserAttributeOptions) -> None:
        self.index = index
        self.attribute = attribute