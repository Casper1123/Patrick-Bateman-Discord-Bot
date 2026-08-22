from piss.instructions.abstract import Instruction
from piss.instructions.choice import ChoiceInstruction
from piss.instructions.push import PushInstruction
from piss.instructions.randnum import RandomNumberInstruction
from piss.instructions.randuser import RandomUserInstruction
from piss.instructions.sleep import SleepInstruction
from piss.instructions.writing import WritingInstruction

parse_order: tuple[type[Instruction], ...] = (
    PushInstruction,
    RandomNumberInstruction,
    RandomUserInstruction,
    SleepInstruction,
    WritingInstruction,
    ChoiceInstruction,
)