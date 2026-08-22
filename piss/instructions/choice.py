from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError
from utilities.exceptions import ErrorTooltip
from piss.instructions import _doubles, _bounds, _escapes, _be_map


option_bounds: list[str] = ['\'', '"']

class ChoiceInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^choice\(\s*(?P<options>.*)\s*\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> ChoiceInstruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Choice')

        # todo: remake entirely.
        raise NotImplementedError()