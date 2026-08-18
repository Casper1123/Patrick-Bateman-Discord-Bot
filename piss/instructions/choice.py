from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError
from utilities.exceptions import ErrorTooltip


class ChoiceInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^choice\(\s*(?P<options>.*)\s*\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        raise _InstructionParseError('Unsupported match identifier for Instruction of type RandomUser', tooltip=ErrorTooltip.WIKI)