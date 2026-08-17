from re import Match

from piss.instructions import Instruction, InstructionType


# todo: figure out when this is usable
class BuildInstruction(Instruction):
    @staticmethod
    def from_match(match: Match) -> Instruction:
        raise RuntimeError('BuildInstruction incompatible with Signatures and from_match.')

    @staticmethod
    def signatures() -> tuple[str, ...]:
        raise RuntimeError('BuildInstruction incompatible with Signatures and from_match.')

    def __init__(self, text: str):
        self.text = text