import ast as _ast
from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction


class ClearInstruction(_Instruction):
    def __init__(self, ):
        ...

    def __str__(self) -> str:
        return super().__str__().removesuffix(': ')

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^clear\(\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory: dict[str, type], recursion_depth: int,
                   writing: bool) -> ClearInstruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Choice')

        return ClearInstruction()