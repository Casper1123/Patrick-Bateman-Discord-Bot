from abc import ABC as _ABC, abstractmethod as _abstractmethod
from re import Match as _Match


class Instruction(_ABC):
    @staticmethod
    @_abstractmethod
    def signatures() -> tuple[str, ...]:
        """
        RegEx signatures to match on for this Instruction type.
        """
        raise NotImplementedError()

    @staticmethod
    @_abstractmethod
    def from_match(match: _Match) -> Instruction:
        """
        Take one of the class' RegEx signature matches to create an Instruction.
        """
        raise NotImplementedError()

