from __future__ import annotations

import datetime as _datetime
import random as _r
from typing import Any as _Any

from discord import Message as _Message, Interaction as _Interaction

from discorduser.user.abstract import BotClient as _BotClient
from piss._utils.mem_tools import reshape as _reshape
from piss.exceptions import InstructionExecutionError as _InstructionExecutionError, InstructionExecutionError as _InstructionExecutionError
from piss.executing.abstract import AbstractInstructionExecutor as _AbstractInstructionExecutor
from piss.instructions.abstract import Instruction as _Instruction
from piss.instructions.build import BuildInstruction as _BuildInstruction
from piss.instructions.choice import ChoiceInstruction as _ChoiceInstruction
from piss.instructions.memory import MemoryInstruction as _MemoryInstruction
from piss.instructions.push import PushInstruction as _PushInstruction
from piss.instructions.randnum import RandomNumberInstruction as _RandomNumberInstruction
from piss.instructions.randuser import RandomUserInstruction as _RandomUserInstruction
from piss.instructions.sleep import SleepInstruction as _SleepInstruction
from piss.instructions.writing import WritingInstruction as _WritingInstruction
from utilities.exceptions import CustomDiscordException as _CustomDiscordException


class TestInstructionExecutor(_AbstractInstructionExecutor):
    """
    Used for running test input. Discard after use.
    """

    async def _build(self, instruction: _BuildInstruction) -> str:
        return instruction.text

    async def _rnd_usr(self, instruction: _RandomUserInstruction, interaction: _Interaction | _Message) -> str:
        if instruction.attribute == 'id':
            return f'member[{instruction.index}].id'
        elif instruction.attribute == 'name':
            return f'member[{instruction.index}].display_name'
        elif instruction.attribute == 'account':
            return f'member[{instruction.index}].name'
        elif instruction.attribute == 'created_at':
            return f'member[{instruction.index}].created_at'
        elif instruction.attribute == 'roles':
            return f'member[{instruction.index}].roles'
        elif instruction.attribute == 'mutual_guilds':
            return f'member[{instruction.index}].mutual_guilds'
        else:
            raise _InstructionExecutionError(instruction, reason=f'Unsupported random user attribute {instruction.attribute}')

    async def _sleep(self, instruction: _SleepInstruction) -> None:
        self.out += '{SLEEP; ' + f'{instruction.time}' + '}'

    async def _writing(self, instruction: _WritingInstruction, interaction: _Interaction | _Message,
                       recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        self.out += '{WRITING[OPEN]; '
        build = await self._exec(instruction.instructions, interaction, recursion_depth, memory, False, build)
        self.out += '[CLOSE]}'
        return build

    def __init__(self):
        super().__init__()
        self.out: str = '' # Used for output returning.
        self.pure_out: str = '' # Printed text into discord channel

    async def run(self, instructions: list[_Instruction]) -> str:
        if not instructions:
            raise AttributeError('No instructions given.')

        await super()._exec(
            instructions=instructions,
            interaction=None,
            recursion_depth=-1,
            memory=await self._create_init_memory(None, None),
            push_final_build=True,
            build=''
        )
        return self.out

    async def _exec(self, instructions: list[_Instruction], interaction: _Message | _Interaction,
                    recursion_depth: int, memory: dict[str, _Any],
                    push_final_build: bool,
                    build: str) -> str:
        build = await super()._exec(instructions, interaction, recursion_depth, memory, push_final_build, build)
        return build

    async def _create_init_memory(self, client: _BotClient, interaction: _Message | _Interaction) -> dict[str, _Any]:
        now = _datetime.datetime.now()
        try:
            # noinspection unresolved-references
            # Any Nones should be excluded by the statements above.
            out = {
                '\\n': '\n',

                # interaction target
                'user.id': 0,
                'user': 'user.display_name',
                'user.name': 'user.display_name',
                'user.created_at': now,
                'user.account': 'user.name',
                'user.mutual_guilds': 0,
                'user.roles': 0,

                'self.id': 1,
                'self': 'me.display_name',
                'self.name': 'me.display_name',
                'self.created_at': now,
                'self.account': 'me.name',
                'self.roles': 1,

                'channel': 'channel.name',
                'channel.id': 2,
                'channel.name': 'channel.name',
                'channel.created_at': now,
                'channel.jump_url': 'channel.jump_url',

                'guild': 'guild.name',
                'guild.id': 3,
                'guild.name': 'guild.name',
                'guild.created_at': now,
                'guild.members': 3,
                'guild.roles': 3,

                # guild owner
                'owner.id': 4,
                'owner': 'owner.display_name',
                'owner.name': 'owner.display_name',
                'owner.created_at': now,
                'owner.account': 'owner.name',
                'owner.roles': 4,
                'owner.mutual_guilds': 4,

                # external
                'local_facts': 0,
                'global_facts': 0,
                'total_facts': 0,
            }
            # check for safety if all keys from parser specification are present.
            await self.__memory_integrity(out)
            return out
        except _CustomDiscordException as e:
            raise e  # Pass pre-constructed Exceptions up to user layer.
        except Exception as e:
            raise _CustomDiscordException(message='Initial Instruction Memory failed to build.', cause=e,
                                         error_type='InstructionMemoryError')

    # region instructions
    async def _push(self, instruction: _PushInstruction, build: str, interaction: _Interaction | _Message) -> None:

        self.pure_out += '{PUSH}' + build

        self.out += ('{PUSH;' +

                     f'eura='
                     f'{int(instruction.pingable.everyone)}'
                     f'{int(instruction.pingable.users)}'
                     f'{int(instruction.pingable.roles)}'
                     f'{int(instruction.pingable.replied_user)}'

                     + ';' + build + '}')

        self._first_reply = False

    async def _choice(self, instruction: _ChoiceInstruction, interaction: _Message | _Interaction,
                      recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        """
        Branches Choice instruction and returns leftover build.
        """
        # Store output for now.

        # 1. Copy current state.
        # 2. Run a copy for each branch on given input
        branch_results: list[tuple[TestInstructionExecutor, str, dict[str, _Any]]] = []
        for i, branch in enumerate(instruction.options):
            ex = TestInstructionExecutor()
            mem = memory.copy()
            try:
                branch_build = await ex._exec(branch, interaction, recursion_depth, mem, False, build)
            except _InstructionExecutionError as e:
                raise e
            except Exception as e:
                raise _InstructionExecutionError(instruction, reason=f'The error was raised in option {i + 1}.', cause=e)

            branch_results.append(
                (ex, branch_build, mem)
            )
        # 3. Check memory integrity after each; are all objects in each memory and of the same type?
        # new: dict[str, type] = {}
        # todo: push memory integrity to compiler not to executor.


        # 4. Pick a random one for visualization feedback for users.
        index: int = 1 + _r.randint(0, len(branch_results) - 1)
        ex, branch_build, mem = branch_results[index]
        _reshape(memory, mem) # Mutate memory into mem

        # Take corresponding data and shape around it.
        self.pure_out += ex.pure_out
        self.out += '{CHOICE[' + str(index) + ']; ' + ex.out + '}'

        return branch_build

    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _memory(self, instruction: _MemoryInstruction, memory: dict[str, _Any]) -> _Any:
        val = super()._memory(instruction, memory)

        self.out += '{MEM; ' + instruction.key + '}' # todo: is this even useful / good? test it a little.

        return val

    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _rnd_num(self, instruction: _RandomNumberInstruction) -> int:
        """
        Returns random number from instruction parameters. Requires string-conversion to be usable for building.
        """
        return await super()._rnd_num(instruction)

    # endregion
