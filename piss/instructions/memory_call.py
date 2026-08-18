from re import Match as _Match

from piss.instructions.abstract import Instruction


class MemoryInstruction(Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        raise RuntimeError('BuildInstruction incompatible with Signatures and from_match.')

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> Instruction:
        raise RuntimeError('BuildInstruction incompatible with Signatures and from_match.')

    def __init__(self, key: str):
        self.key = key