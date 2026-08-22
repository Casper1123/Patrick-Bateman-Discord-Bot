from abc import ABC as ABC, abstractmethod as abstractmethod
from re import Match as _Match


class Instruction(ABC):
    @staticmethod
    @abstractmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        """
        RegEx signatures to match on for this Instruction type.
        Comes paired with an identifier for from_match staticmethod.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int, writing: bool) -> Instruction:
        """
        Take one of the class' RegEx signature matches to create an Instruction.
        Requires Match input identifier.
        If recursing further, this is where the incrementation happens.
        """
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        return type(self).__name__.removesuffix('Instruction') + ': '

    def __hash__(self) -> int:
        return hash(str(type(self).__name__))