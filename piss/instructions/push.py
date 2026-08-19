from enum import Enum as _Enum
from re import Match as _Match

from discord import AllowedMentions as _AllowedMentions

from piss.instructions.abstract import Instruction as _Instruction
from piss.exceptions import InstructionParseError as _InstructionParseError


class PushInstruction(_Instruction):
    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^push\((?P<pingable>(\d?))\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int = 0,
                   writing: bool = False) -> _Instruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Push')

        pingable_val: str = match.group('pingable')
        if not pingable_val:
            return PushInstruction()

        try:
            pingable_val: int = int(pingable_val)
        except ValueError:
            raise _InstructionParseError(match.group(0), f'Could not parse {pingable_val} into an Integer.')

        if not pingable_val in {0, 1, 2}:
            raise _InstructionParseError(match.group(0), f'Pingable option **{pingable_val}** not in **[0, 1, 2]**.')

        if pingable_val == 2:
            pingable = MentionOptions.ALL
        elif pingable_val == 1:
            pingable = MentionOptions.AUTHOR
        else:
            pingable = MentionOptions.NONE

        return PushInstruction(pingable)

    def __init__(self, pingable: _AllowedMentions | None = None) -> None:
        if not pingable:
            # Everyone: @everyone & @here
            # Users: Can ping other users
            # Roles: Can ping roles
            # Replied_user: If to ping the author if replying.
            pingable = _AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)
        self.pingable = pingable