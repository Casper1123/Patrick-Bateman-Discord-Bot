from re import Match as _Match

from piss.exceptions import InstructionParseError as _InstructionParseError
from piss.instructions.abstract import Instruction as _Instruction

SLEEP_TIMER_UPPER_BOUND: float = 3600  # in seconds
SLEEP_TIMER_LOWER_BOUND: float = 0.5


class SleepInstruction(_Instruction):
    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Sleep')

        time = match.group('time')
        if not time:
            return SleepInstruction()

        try:
            time = float(time)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'Could not convert **{time}** into a number.')

        if time < SLEEP_TIMER_LOWER_BOUND:
            raise _InstructionParseError(match.group(0), 'SLEEP Instruction time is below lower bound.\n'
                                                         f'Received: **{time}**. Minimal: **{SLEEP_TIMER_LOWER_BOUND}**')
        elif time > SLEEP_TIMER_UPPER_BOUND:
            raise _InstructionParseError(match.group(0), f'SLEEP Instruction time exceeds upper bound.\n'
                                                         f'Received: **{time}**. Maximum: **{SLEEP_TIMER_UPPER_BOUND}**.')
        return SleepInstruction(time)

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^sleep\((?P<time>(\d{1,4}(\.\d{1,2})?)?)\)$', 0),

    def __init__(self, time: float | int = 1):
        self.time = time