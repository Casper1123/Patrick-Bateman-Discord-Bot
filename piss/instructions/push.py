from re import Match as _Match

from discord import AllowedMentions as _AllowedMentions

from piss.exceptions import InstructionParseError as _InstructionParseError
from piss.instructions.abstract import Instruction as _Instruction


class PushInstruction(_Instruction):
    def __str__(self) -> str:
        # noinspection string-conversion-without-dunder-method
        # so be it for some random list moment
        return super().__str__() + f'[ev={self.pingable.everyone}; usr={self.pingable.users}; role={self.pingable.roles}; reply={self.pingable.replied_user}]'

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^push\((?P<pingable>(\d?))\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory: dict[str, type], recursion_depth: int,
                   writing: bool) -> PushInstruction:
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

        # todo: could make each one of these an individual option, binary encode it into 4 bits (or let 0000 be an input)
        if pingable_val == 2:
            return PushInstruction(everyone=True, users=True, roles=True, replied_user=True)
        elif pingable_val == 1:
            return PushInstruction(replied_user=True)
        
        return PushInstruction()

    def __init__(self, everyone: bool = False, users: bool = False, roles: bool = False, replied_user: bool = False) -> None:
        """
        :param everyone: @everyone & @here
        :param users: Can ping other users
        :param roles: Can ping roles
        :param replied_user: If to ping the author if replying.
        """
        self.pingable = _AllowedMentions(everyone=everyone, users=users, roles=roles, replied_user=replied_user)