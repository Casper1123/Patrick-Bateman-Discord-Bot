from abc import ABC, abstractmethod
from enum import Enum
from re import Match

class InstructionType(Enum):
    BUILD = 0

class Instruction(ABC):
    @staticmethod
    @abstractmethod
    def signatures() -> tuple[str, ...]:
        """
        RegEx signatures to match on for this Instruction type.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_match(match: Match) -> Instruction:
        """
        Take one of the class' RegEx signature matches to create an Instruction.
        """
        raise NotImplementedError()

