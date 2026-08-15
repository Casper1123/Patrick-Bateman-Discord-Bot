from piss.instructions import Instruction, InstructionType


# todo: figure out when this is usable
class BuildInstruction(Instruction):
    @staticmethod
    def signatures() -> tuple[str, ...]:
        return '',

    def __init__(self, text: str):
        self.text = text

        super().__init__(InstructionType.BUILD)