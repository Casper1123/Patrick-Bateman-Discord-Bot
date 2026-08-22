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
from piss.exceptions import InstructionExecutionError as _InstructionExecutionError
from piss.old import INITIAL_MEMORY_TYPES
from utilities.exceptions import CustomDiscordException as _CustomDiscordException, ErrorTooltip as _ErrorTooltip, IncompatibleTargetChannel as _IncompatibleTargetChannel

MAX_EXECUTION_RECURSION_DEPTH = 5  # todo: into config file you go.

class InstructionExecutor:
    def __init__(self, client: BotClient) -> None:
        self.client: BotClient = client
        self._first_reply: bool = True

        self._shuffled_member_list: list[_Member] = []


    async def run(self, instructions: list[_Instruction], interaction: _Message | _Interaction):
        """
        Run the given Instructions in the context of the given interaction.
        Has less safety features as the Compiler is supposed to handle that.
        """
        if not instructions:
            raise AttributeError('No instructions given.')

        if not interaction.guild:
            raise ValueError('Cannot be performed outside of a Guild.')

        if not isinstance(interaction.channel, Messageable):
            raise _IncompatibleTargetChannel(interaction.channel, Messageable.__name__)

        await self._exec(
            instructions=instructions,
            interaction=interaction,
            recursion_depth=-1, # Incremented by _exec to 0
            memory=await self._create_init_memory(interaction), # todo: init memory
            push_final_build=True,
            build=''
        )

    async def _exec(self, instructions: list[_Instruction], interaction: _Message | _Interaction,
                    recursion_depth: int, memory: dict[str, _Any],
                    push_final_build: bool,
                    build: str) -> str:
        recursion_depth += 1
        if recursion_depth > MAX_EXECUTION_RECURSION_DEPTH:
            raise _CustomDiscordException(
                message=f'Maximum recursion depth of {recursion_depth} exceeded maximal value when executing Instructions.\n'
                        f'{"\n".join(str(i) for i in instructions)}', error_type='ParsedExecutionRecursionDepthLimit',
                tooltip=_ErrorTooltip.WIKI)
        
        i: int = 0
        n: int = len(instructions)
        
        
        while i < n:
            instruction: _Instruction = instructions[i]
            
            # faster with a 'switch' case but is that even available.
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
                raise _CustomDiscordException() # todo: proper execution raise required.

        if push_final_build:
            await self._push(PushInstruction(), build, interaction)
            build = ''

        return build

    # region instructions
    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _build(self, instruction: BuildInstruction) -> str:
        """
        Returns build extension based on instruction.
        """
        return instruction.text

    async def _push(self, instruction: PushInstruction, build: str, interaction: _Interaction | _Message) -> None:
        """
        Push given build into target channel.
        Note that if no `build` is passed in, `interaction` may be a malformed object as it is never checked.
        Do make sure to clean out `build`.
        """
        if not build:
            self._first_reply = False
            return

        if isinstance(interaction, _Message) and self._first_reply:
            await interaction.reply(content=build, allowed_mentions=instruction.pingable)
        elif isinstance(interaction, _Interaction) and self._first_reply:
            await interaction.response.send_message(content=build, allowed_mentions=instruction.pingable)
        else:
            await interaction.channel.send(content=build, allowed_mentions=instruction.pingable)

        self._first_reply = False

    async def _choice(self, instruction: ChoiceInstruction, interaction: _Message | _Interaction, recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        """
        Branches Choice instruction and returns leftover build.
        """
        branch: list[_Instruction] = _r.choice(instruction.options)
        build = await self._exec(
            instructions=branch,
            interaction=interaction,
            recursion_depth=recursion_depth,
            memory=memory,
            push_final_build=False,
            build=build
        )

        return build

    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _memory(self, instruction: MemoryInstruction, memory: dict[str, _Any]) -> _Any:
        val: _Any | None = _fetch(memory, instruction.key)
        if val is None:
            raise ValueError(f'Seemingly, the key {instruction.key} is not available. This is only possible')

    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _rnd_num(self, instruction: RandomNumberInstruction) -> int:
        """
        Returns random number from instruction parameters. Requires string-conversion to be usable for building.
        """
        return _r.randint(instruction.a, instruction.b)

    async def _rnd_usr(self, instruction: RandomUserInstruction, interaction: _Interaction | _Message) -> str:
        """
        Returns direct conversion user attribute from instruction parameters.
        """
        if not self._shuffled_member_list:
            self._shuffled_member_list = list(interaction.guild.members)
            _r.shuffle(self._shuffled_member_list)

        index: int = instruction.index % len(self._shuffled_member_list)
        member: _Member = self._shuffled_member_list[index]

        if instruction.attribute == 'id':
            return str(member.id)
        elif instruction.attribute == 'name':
            return member.display_name
        elif instruction.attribute == 'account':
            return member.name
        elif instruction.attribute == 'created_at':
            return member.created_at.isoformat(timespec='minutes')
        elif instruction.attribute == 'roles':
            return str(len(member.roles))
        elif instruction.attribute == 'mutual_guilds':
            return str(len(member.mutual_guilds))
        else:
            raise _InstructionExecutionError(instruction, reason=f'Unsupported random user attribute {instruction.attribute}')

    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _sleep(self, instruction: SleepInstruction) -> None:
        """
        Asynchronously sleeps for given time interval.
        """
        await _asyncio.sleep(instruction.time)

    async def _writing(self, instruction: WritingInstruction, interaction: _Interaction | _Message, recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        """
        Executes embedded instructions while showing the typing indicator in the channel.
        Returns leftover build.
        """
        async with interaction.channel.typing():
            return await self._exec(
                instructions=instruction.instructions,
                recursion_depth=recursion_depth,
                memory=memory,
                build=build,
                push_final_build=False,
                interaction=interaction
            )
    # endregion
    # region memory
    async def _create_init_memory(self, interaction: _Interaction | _Message) -> dict[str, _Any]:
        # noinspection bad-assignment
        guild: _Guild = interaction.guild
        if not guild:
            raise PermissionError('Cannot execute instructions outside of Guild context.')

        # todo : pretty sure this don't work on messages.
        if isinstance(interaction, _Interaction):
            user: _User | _Member = interaction.user
            member: _Member | None = guild.get_member(interaction.user.id)
        else:
            user: _User | _Member = interaction.author
            member: _Member | None = guild.get_member(interaction.author.id)

        me: _ClientUser | None = self.client.user
        if not me:
            raise ValueError('Cannot prepare memory data, missing required data to construct initial memory.')

        me_member: _Member | None = guild.get_member(me.id)
        if not isinstance(interaction.channel, (_TextChannel, _VoiceChannel, _StageChannel, _Thread)):
            raise _IncompatibleTargetChannel(interaction.channel, Messageable.__name__)
        channel: _TextChannel | _VoiceChannel | _StageChannel | _Thread = interaction.channel
        # noinspection bad-assignment
        # always exists.
        owner: _Member = guild.owner  # guild owner

        local_facts: int = self.client.fact.get_fact_count(guild.id)
        global_facts: int = self.client.fact.get_fact_count(None)
        total_facts: int = local_facts + global_facts

        if None in [member, me, me_member] or not isinstance(me, _abcUser):
            raise ValueError('Cannot prepare memory data, missing required data to construct initial memory.')
        try:
            # noinspection unresolved-references
            # Any Nones should be excluded by the statements above.
            out = {
                '\\n': '\n',

                # interaction target
                'user.id': user.id,
                'user': user.display_name,
                'user.name': user.display_name,
                'user.created_at': user.created_at,
                'user.account': user.name,
                'user.mutual_guilds': len(member.mutual_guilds),
                'user.roles': len(member.roles),

                'self.id': me.id,
                'self': me.display_name,
                'self.name': me.display_name,
                'self.created_at': me.created_at,
                'self.account': me.name,
                'self.roles': len(me_member.roles) if me_member else 0,

                'channel': channel.name,
                'channel.id': channel.id,
                'channel.name': channel.name,
                'channel.created_at': channel.created_at,
                'channel.jump_url': channel.jump_url,

                'guild': guild.name,
                'guild.id': guild.id,
                'guild.name': guild.name,
                'guild.created_at': guild.created_at,
                'guild.members': guild.member_count,
                'guild.roles': len(guild.roles),

                # guild owner
                'owner.id': owner.id,
                'owner': owner.display_name,
                'owner.name': owner.display_name,
                'owner.created_at': owner.created_at,
                'owner.account': owner.name,
                'owner.roles': len(owner.roles) if owner else 0,
                'owner.mutual_guilds': len(owner.mutual_guilds),

                # external
                'local_facts': local_facts,
                'global_facts': global_facts,
                'total_facts': total_facts,
            }
            # check for safety if all keys from parser specification are present.
            await self.__memory_integrity(out)
            return out
        except _CustomDiscordException as e:
            raise e  # Pass pre-constructed Exceptions up to user layer.
        except Exception as e:
            raise _CustomDiscordException(message='Initial Instruction Memory failed to build.', cause=e,
                                         error_type='InstructionMemoryError')

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
            raise TypeError(f'Initial memory has not been constructed correctly; Missing: {missing_keys}. Incorrect types: {','.join(f'{i[0]}: {i[1]} (wanted {i[2]})' for i in bad_types)}')
    # endregion
