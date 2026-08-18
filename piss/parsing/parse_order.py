from piss.instructions.abstract import Instruction
from piss.instructions.push import PushInstruction

parse_order: tuple[type[Instruction], ...] = (
    PushInstruction, # todo: populate
)