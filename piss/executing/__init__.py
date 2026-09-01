import asyncio as _asyncio
import random as _r
from typing import Any as _Any

from discord import Message as _Message, Interaction as _Interaction, Member as _Member, Guild as _Guild, User as _User, \
    ClientUser as _ClientUser, TextChannel as _TextChannel, Thread as _Thread, StageChannel as _StageChannel, \
    VoiceChannel as _VoiceChannel
from discord.abc import Messageable, User as _abcUser

from discorduser.user.abstract import BotClient as _BotClient
from piss.exceptions import InstructionExecutionError as _InstructionExecutionError
from piss.executing.abstract import AbstractInstructionExecutor as _AbstractInstructionExecutor
from piss.instructions.abstract import Instruction as _Instruction
from piss.instructions.build import BuildInstruction as _BuildInstruction
from piss.instructions.choice import ChoiceInstruction as _ChoiceInstruction
from piss.instructions.push import PushInstruction as _PushInstruction
from piss.instructions.randuser import RandomUserInstruction as _RandomUserInstruction
from piss.instructions.sleep import SleepInstruction as _SleepInstruction
from piss.instructions.writing import WritingInstruction as _WritingInstruction
from utilities.exceptions import CustomDiscordException as _CustomDiscordException, \
    IncompatibleTargetChannel as _IncompatibleTargetChannel

MAX_EXECUTION_RECURSION_DEPTH = 5  # todo: into config file you go.

class InstructionExecutor(_AbstractInstructionExecutor):
    def __init__(self) -> None:
        super().__init__()

        self._shuffled_member_list: list[_Member] = []


    async def run(self, client: _BotClient, instructions: list[_Instruction], interaction: _Message | _Interaction):
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
            memory=await self._create_init_memory(client, interaction), # todo: init memory
            push_final_build=True,
            build=''
        )

    # region instructions
    # noinspection PyMethodMayBeStatic
    # this way to make testing framework easier to implement.
    async def _build(self, instruction: _BuildInstruction) -> str:
        """
        Returns build extension based on instruction.
        """
        return instruction.text

    async def _push(self, instruction: _PushInstruction, build: str, interaction: _Interaction | _Message) -> None:
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

    async def _choice(self, instruction: _ChoiceInstruction, interaction: _Message | _Interaction, recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
        """
        Branches Choice instruction and returns leftover build.
        """
        branch: list[_Instruction] = _r.choice(instruction.options)

        return await self._exec(
            instructions=branch,
            interaction=interaction,
            recursion_depth=recursion_depth,
            memory=memory,
            push_final_build=False,
            build=build
        )

    async def _rnd_usr(self, instruction: _RandomUserInstruction, interaction: _Interaction | _Message) -> str:
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
    async def _sleep(self, instruction: _SleepInstruction) -> None:
        """
        Asynchronously sleeps for given time interval.
        """
        await _asyncio.sleep(instruction.time)

    async def _writing(self, instruction: _WritingInstruction, interaction: _Interaction | _Message, recursion_depth: int, memory: dict[str, _Any], build: str) -> str:
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
    async def _create_init_memory(self, client: _BotClient, interaction: _Interaction | _Message) -> dict[str, _Any]:
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

        me: _ClientUser | None = client.user
        if not me:
            raise ValueError('Cannot prepare memory data, missing required data to construct initial memory.')

        me_member: _Member | None = guild.get_member(me.id)
        if not isinstance(interaction.channel, (_TextChannel, _VoiceChannel, _StageChannel, _Thread)):
            raise _IncompatibleTargetChannel(interaction.channel, Messageable.__name__)
        channel: _TextChannel | _VoiceChannel | _StageChannel | _Thread = interaction.channel
        # noinspection bad-assignment
        # always exists.
        owner: _Member = guild.owner  # guild owner

        local_facts: int = client.fact.get_fact_count(guild.id)
        global_facts: int = client.fact.get_fact_count(None)
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
            # todo: this is dookie.
            raise _CustomDiscordException(message='Initial Instruction Memory failed to build.', cause=e,
                                         error_type='InstructionMemoryError')
    # endregion
