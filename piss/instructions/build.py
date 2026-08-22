from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError
from utilities.exceptions import ErrorTooltip as _ErrorTooltip


class BuildInstruction(_Instruction):
    def __str__(self) -> str:
        return super().__str__() + f'[text={self.text}]'

    @staticmethod
    def from_match(match: _Match, ident: int, memory: dict[str, type], recursion_depth: int,
                   writing: bool) -> BuildInstruction:
        raise _InstructionParseError(
            'BuildInstruction incompatible with Signatures and from_match.',
            tooltip=_ErrorTooltip.ISSUE
        )

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        raise _InstructionParseError(
            'BuildInstruction incompatible with Signatures and from_match.',
            tooltip=_ErrorTooltip.ISSUE
        )

    def __init__(self, text: str):
        self.text = text
