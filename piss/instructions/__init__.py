from abc import ABC, abstractmethod
from enum import Enum

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

    def __init__(self, itype: InstructionType):
        self.type = itype
    # todo: execute method?

