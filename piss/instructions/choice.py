from re import Match as _Match
import ast as _ast

from piss.instructions.abstract import Instruction as _Instruction
# noinspection PyProtectedMember
from piss.parsing import _parse_top_level
# todo fixme: circular import! parser -> parse order -> ChoiceInstruction -> parser

class ChoiceInstruction(_Instruction):
    def __init__(self, options: list[list[_Instruction]]):
        self.options: list[list[_Instruction]] = options

    def __str__(self) -> str:
        return super().__str__() + f'[opt={self.options}]'

    @staticmethod
    def signatures() -> tuple[tuple[str, int], ...]:
        return (r'^choice\(\s*(?P<options>.*)\s*\)$', 0),

    @staticmethod
    def from_match(match: _Match, ident: int, memory_stack: list[dict[str, type]], recursion_depth: int,
                   writing: bool) -> ChoiceInstruction:
        if not ident == 0:
            raise ValueError('Unsupported match identifier for Instruction of type Choice')

        # todo: remake entirely.
        # Tldr; choice(str, str*, str) where str* is any number >= 0 str input, each bounded with either ' or "
        # Need to individually parse the choices given the parsing function _parse_top_level
        # _ast.literal_eval should perform this function, but double check if that is true through testing.
        opt_raw = _ast.literal_eval(f'({match.group('options')})')

        if not isinstance(opt_raw, tuple):
            raise ValueError('Match not parsed as tuple. Probably a non-user error.')

        for x in opt_raw:
            if not isinstance(x, str):
                raise TypeError(f'Options entry of type {type(x).__name__}, not string for option {x}')

        opt_raw: tuple[str, ...]

        # Turn into Instructions
        options: list[list[_Instruction]] = []
        for x in opt_raw:
            instr: list[_Instruction] = _parse_top_level(x, recursion_depth + 1, memory_stack, writing)
            options.append(instr)

        return ChoiceInstruction(options)