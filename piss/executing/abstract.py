from abc import ABC, abstractmethod
from typing import Any as _Any
import random as _r
import asyncio as _asyncio

from discord import Message as _Message, Interaction as _Interaction, Member as _Member, Guild as _Guild, User as _User, ClientUser as _ClientUser, TextChannel as _TextChannel, Thread as _Thread, StageChannel as _StageChannel, VoiceChannel as _VoiceChannel
from discord.abc import Messageable, User as _abcUser

from discorduser.user.abstract import BotClient
from piss.instructions.abstract import Instruction as _Instruction
from piss.instructions.build import BuildInstruction
from piss.instructions.choice import ChoiceInstruction
from piss.instructions.memory import MemoryInstruction
from piss.instructions.push import PushInstruction
from piss.instructions.randnum import RandomNumberInstruction
from piss.instructions.randuser import RandomUserInstruction
from piss.instructions.sleep import SleepInstruction
from piss.instructions.writing import WritingInstruction
from piss._utils.mem_tools import fetch as _fetch
from piss.exceptions import InstructionExecutionError as _InstructionExecutionError, InstructionExecutionError
from piss.old import INITIAL_MEMORY_TYPES
from utilities.exceptions import CustomDiscordException as _CustomDiscordException, ErrorTooltip as _ErrorTooltip, IncompatibleTargetChannel as _IncompatibleTargetChannel

MAX_EXECUTION_RECURSION_DEPTH = 5  # todo: into config file you go.


class AbstractInstructionExecutor(ABC):
    def __init__(self):
        self._first_reply: bool = True

    async def _exec(self, instructions: list[_Instruction], interaction: _Message | _Interaction,
                    recursion_depth: int, memory: dict[str, _Any],
                    push_final_build: bool,
                    build: str) -> str:
        recursion_depth += 1
        if recursion_depth > MAX_EXECUTION_RECURSION_DEPTH:
            # todo: Make better
            raise _CustomDiscordException(
                message=f'Maximum recursion depth of {recursion_depth} exceeded maximal value when executing Instructions.\n'
                        f'{"\n".join(str(i) for i in instructions)}', error_type='ParsedExecutionDepthLimit',
                tooltip=_ErrorTooltip.WIKI)

        i: int = 0
        n: int = len(instructions)

        while i < n:
            instruction: _Instruction = instructions[i]

            try:
                # faster with a 'switch' case but is that even available.
                # todo: make better this SMELLS it STINKS it's DOOKIE
                if isinstance(instruction, BuildInstruction):
                    build += await self._build(instruction)
                elif isinstance(instruction, PushInstruction):
                    await self._push(instruction, build, interaction)
                    build = ''
                elif isinstance(instruction, ChoiceInstruction):
                    build = await self._choice(instruction, interaction, recursion_depth, memory, build)
                elif isinstance(instruction, MemoryInstruction):
                    build += str(await self._memory(instruction, memory))
                elif isinstance(instruction, RandomNumberInstruction):
                    build += str(await self._rnd_num(instruction))
                elif isinstance(instruction, RandomUserInstruction):
                    build += await self._rnd_usr(instruction, interaction)
                elif isinstance(instruction, SleepInstruction):
                    await self._sleep(instruction)
                elif isinstance(instruction, WritingInstruction):
                    build = await self._writing(instruction, interaction, recursion_depth, memory, build)
                else:
                    raise NotImplementedError(f'Instruction of type {type(instruction)} is not supported.')

            except _CustomDiscordException as e:
                raise e
            except Exception as e:
                raise InstructionExecutionError(instruction, cause=e)

        if push_final_build:
            await self._push(PushInstruction(), build, interaction)
            build = ''

        return build

    # noinspection method-may-be-static
    async def __memory_integrity(self, memory: dict[str, _Any]):
        """
        Raises Exception if the initial memory is not up to code.
        """
        missing_keys: set[str] = set()
        bad_types: set[tuple[str, type, type]] = set()
        for k, v in INITIAL_MEMORY_TYPES.items():
            if k not in memory:
                missing_keys.add(k)
                continue
            if type(memory[k]) != v:
                bad_types.add((k, v, type(memory[k])))
        if missing_keys or bad_types:
            raise TypeError(
                f'Initial memory has not been constructed correctly; Missing: {missing_keys}. Incorrect types: {','.join(f'{i[0]}: {i[1]} (wanted {i[2]})' for i in bad_types)}')

    @abstractmethod
    async def _build(self, instruction: BuildInstruction) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def _push(self, instruction: PushInstruction, build: str, interaction: _Interaction | _Message) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def _choice(self, instruction: ChoiceInstruction, interaction: _Message | _Interaction,
                      recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def _rnd_usr(self, instruction: RandomUserInstruction, interaction: _Interaction | _Message) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def _sleep(self, instruction: SleepInstruction) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def _writing(self, instruction: WritingInstruction, interaction: _Interaction | _Message,
                       recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def _create_init_memory(self, client: BotClient, interaction: _Interaction | _Message) -> dict[str, _Any]:
        raise NotImplementedError()

    async def _memory(self, instruction: MemoryInstruction, memory: dict[str, _Any]) -> _Any:
        val: _Any | None = _fetch(memory, instruction.key)
        if val is None:
            raise ValueError(
                f'Seemingly, the key {instruction.key} is not available. This is only possible using a malformed Instruction list.')
        return val

    async def _rnd_num(self, instruction: RandomNumberInstruction) -> int:
        """
        Returns random number from instruction parameters. Requires string-conversion to be usable for building.
        """
        return _r.randint(instruction.a, instruction.b)

