from piss.instructions.abstract import Instruction as _Instruction
from piss.instructions.choice import ChoiceInstruction as _ChoiceInstruction
from piss.instructions.push import PushInstruction as _PushInstruction
from piss.instructions.randnum import RandomNumberInstruction as _RandomNumberInstruction
from piss.instructions.randuser import RandomUserInstruction as _RandomUserInstruction
from piss.instructions.sleep import SleepInstruction as _SleepInstruction
from piss.instructions.writing import WritingInstruction as _WritingInstruction

parse_order: tuple[type[_Instruction], ...] = (
    _PushInstruction,
    _RandomNumberInstruction,
    _RandomUserInstruction,
    _SleepInstruction,
    _WritingInstruction,
    _ChoiceInstruction,
)