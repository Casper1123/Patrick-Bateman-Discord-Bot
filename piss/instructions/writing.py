from re import Match as _Match

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError



class WritingInstruction(_Instruction):
    def __str__(self) -> str:
        return super().__str__() + f'[instr={self.instructions}]'

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^writing\((?P<instr>(.*))\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int,
                   writing: bool) -> WritingInstruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Writing')

        if writing:
            raise _InstructionParseError(match.group(0),
                                        f'Writing Instruction cannot be used inside of another Writing Instruction')
        content = match.group('instr')

        # noinspection protected-member
        from piss.parsing import _parse_instruction_block

        content_instr: list[_Instruction] = _parse_instruction_block(content, memory_stack, recursion_depth + 1, writing=True)
        if not content_instr:
            raise _InstructionParseError(match.group(0),
                                        f'Writing Instruction did not receive any Instructions (received **{content}**).')

        return WritingInstruction(content_instr)

    def __init__(self, instructions: list[_Instruction]):
        self.instructions = instructions