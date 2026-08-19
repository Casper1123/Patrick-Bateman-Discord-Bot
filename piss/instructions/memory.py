from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction


class MemoryInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        raise RuntimeError('MemoryInstruction incompatible with Signatures and from_match.')

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        raise RuntimeError('MemoryInstruction incompatible with Signatures and from_match.')

    # todo: move mem getter function here?
    
    def __init__(self, key: str):
        self.key = key