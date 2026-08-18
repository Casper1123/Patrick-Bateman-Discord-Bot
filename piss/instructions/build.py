from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError
from utilities.exceptions import ErrorTooltip as _ErrorTooltip


class BuildInstruction(_Instruction):
    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        raise _InstructionParseError('BuildInstruction incompatible with Signatures and from_match.', tooltip=_ErrorTooltip.ISSUE)

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        raise _InstructionParseError('BuildInstruction incompatible with Signatures and from_match.', tooltip=_ErrorTooltip.ISSUE)

    def __init__(self, text: str):
        self.text = text
