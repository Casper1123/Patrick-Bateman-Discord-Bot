from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction


class MemoryInstruction(_Instruction):
    def __str__(self) -> str:
        return super().__str__() + f'[key={self.key}]'

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        raise RuntimeError('MemoryInstruction incompatible with Signatures and from_match.')

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int,
                   writing: bool) -> MemoryInstruction:
        raise RuntimeError('MemoryInstruction incompatible with Signatures and from_match.')

    # todo: move mem getter function here?
    
    def __init__(self, key: str):
        self.key = key