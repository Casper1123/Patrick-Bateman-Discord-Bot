import asyncio as _asyncio
import random as _r
import datetime as _datetime

import discord
from discord import AllowedMentions, Message, Interaction
from discord.ext import commands

from Rewrite.utilities.exceptions import CustomDiscordException
from Rewrite.discorduser import BotClient
from . import Instruction, InstructionType, MentionOptions, INITIAL_MEMORY_TYPES


MAX_EXECUTION_RECURSION_DEPTH = 5 # todo: into config file you go.


class ParsedExecutionFailure(CustomDiscordException):
    def __init__(self, instruction: Instruction, index: int, cause: Exception | None = None) -> None:
        super().__init__(f'Failed to execute Instruction of type **{instruction.type}** (index {index}) given options \'{instruction.options}\'', cause)

class ParsedExecutionRecursionDepthLimit(CustomDiscordException):
    def __init__(self, instructions: list[Instruction], depth: int) -> None:
        super().__init__(f'Maximum recursion depth of {depth} exceeded maximal value when executing Instructions.\n'
                         f'{"\n".join(str(i) for i in instructions)}')

class InstructionExecutor:
    """
    One call per instance, in part to be compatible with the debugger.
    """
    def __init__(self, client: BotClient):
        self.client = client

    async def run(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple[str | None, bool]:
        depth: int = depth + 1 if depth else 0
        if depth > MAX_EXECUTION_RECURSION_DEPTH:
            raise ParsedExecutionRecursionDepthLimit(instructions, depth)

        first_reply = fresh
        i: int = 0
        build: str = build if build else "" # expanded until finished or message sends, then reset. Highest scope is first.
        mem: dict[str, ...] = {} if memstack else self.init_memory(interaction)
        memstack = memstack if memstack else [] # outer scope memory. Initialize here for now.
        local_scope = memstack + [mem]
        while i < len(instructions):
            instruction = instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    if build == "": raise ValueError('Instruction of type PUSH did not receive content to push.')
                    await self.send_output(build, interaction, fresh=first_reply, mention=instruction.options['pingable'])
                    build = ""
                    first_reply = False
                elif instruction.type == InstructionType.SLEEP:
                    time = instruction.options['time']
                    if isinstance(time, str):
                        time = self.mem_fetch(local_scope, time)
                    await self.sleep(time=time)
                elif instruction.type == InstructionType.BASIC_REPLACE:
                    build += self.basic_replace(local_scope, instruction.options['key'])
                elif instruction.type == InstructionType.WRITING:
                    build, first_reply = await self.is_writing(instruction.options['instructions'], interaction, depth, build, fresh, memstack)
                    if build is None:
                        raise TypeError('Instruction of type WRITING returned None value instead of String.') # fixme: this can't be right
                elif instruction.type == InstructionType.CHOICE:
                    build, first_reply = await self.choice(instruction.options['options'], interaction, depth, build, fresh, memstack)
                elif instruction.type == InstructionType.CALCULATE:
                    self.calculate(instruction.options, memstack)
                elif instruction.type == InstructionType.RANDOM_REPL:
                    build += str(self.random(instruction.options['left'], instruction.options['right']))
                else:
                    raise NotImplementedError(f'InstructionType {instruction.type} not implemented.')
            except Exception as e:
                raise ParsedExecutionFailure(instruction, i, cause=e)
            i += 1

        if build and push_final_build:
            await self.send_output(build, interaction, fresh=first_reply, mention=MentionOptions.NONE) # Defaults to not mentioning. Should have PUSHed beforehand.
            return None, first_reply
        else:
            return build, first_reply

    async def init_memory(self, interaction: Interaction | Message) -> dict[str, ...]:
        guild: discord.Guild = interaction.guild
        if not guild:
            raise PermissionError('Cannot execute instructions outside of Guild context.')
        user: discord.User = interaction.user
        member: discord.Member = interaction.guild.get_member(interaction.user.id)
        me: discord.ClientUser = self.client.user
        me_member: discord.Member = interaction.guild.get_member(me.id)

        channel: discord.TextChannel = interaction.channel
        owner: discord.Member = guild.owner  # guild owner

        local_facts: int = self.client.db.get_fact_count(guild.id)
        global_facts: int = self.client.db.get_fact_count(None)
        total_facts: int = local_facts + global_facts

        if None in [member, me, me_member] or not isinstance(me, discord.abc.User):
            raise ValueError('Cannot prepare memory data, missing required data to construct initial memory.')
        try:
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

                'message': interaction.message.id,
                'message.jump_url': interaction.message.jump_url,

                # external
                'local_facts': local_facts,
                'global_facts': global_facts,
                'total_facts': total_facts,
            }
            # check for safety if all keys from parser specification are present.
            self.check_init_memory(out)
            return out
        except CustomDiscordException as e:
            raise e # Pass pre-constructed Exceptions up to user layer.
        except Exception as e:
            raise CustomDiscordException('Initial Instruction Memory failed to build.', e, 'InstructionMemoryError')

    def check_init_memory(self, mem: dict[str, ...]) -> None:
        """
        Throws an exception if the memory is not safely initialized.
        :param mem: Initial memory.
        """
        for key in INITIAL_MEMORY_TYPES.keys():
            if not key in mem.keys():
                raise CustomDiscordException(
                    message=f'Initial Instruction Memory has a missing entry as specified by the parser at **{key}**.\n'
                            'This is an implementation error and has to be fixed by developers manually.\n'
                            'Aborting execution to preserve memory safety.', error_type='InstructionMemoryError')
            val = mem[key]
            expected = INITIAL_MEMORY_TYPES[key]
            if type(val) != expected:
                raise CustomDiscordException(error_type='InstructionMemoryError',
                                             message=f'Initial Instruction Memory has a typing mismatch from parser specification at **{key}** (expected **{expected}**, given **{type(val)} ({val})**).\n'
                                                     f'This is *probably* an implementation error and probably has to be fixed by developers manually.\n'
                                                     f'Aborting execution to preserve memory safety.')
        for key in mem.keys():
            if key not in INITIAL_MEMORY_TYPES.keys():
                raise CustomDiscordException(error_type='InstructionMemoryError',
                                             message=f'Initial Instruction Memory contains a value not present in parser specification (**{key}**).\n'
                                                     f'This is an implementation error and has to be fixed by developers manually.\n'
                                                     f'Aborting execution to preserve memory safety.')
            if type(mem[key]) != INITIAL_MEMORY_TYPES[key]:
                val = mem[key]
                raise CustomDiscordException(error_type='InstructionMemoryError',
                                             message=f'Initial Instruction Memory has a typing mismatch from parser specification at **{key}:{val} ({type(val)}** *(expected {INITIAL_MEMORY_TYPES[key]})*.\n'
                                                     f'This is probably an implementation error. Please raise this issue to the developers **if not reported already**.\n'
                                                     f'Aborting execution to preserve memory safety.')

    def mem_fetch(self, memdict: list[dict[str, ...]], keys: list[str]) -> dict[str, ...]:
        """
        Gets the given variables from memory.
        :param memdict: The given variable stack.
        :param keys: The keys to look up.
        :return: A { key: value } dictionary for each key in keys. None if no value found.
        """
        # merge memdict into a single dict:
        mem: dict[str, ...] = {}
        for frame in reversed(memdict):  # reversed so, if somehow duplicates exist, the top-framed one takes precedence
            for k, v in frame.items():
                mem[k] = v # todo: do I set this up such that it's returned from a function, that way I can also make other merged-mem functions (like keys)

        memkeys = mem.keys()
        return { key: mem[key] if key in memkeys else None for key in keys }

    async def send_output(self, out: str, interaction: Interaction | Message, fresh: bool, mention: MentionOptions = MentionOptions.NONE) -> None:
        """
        Sends the given string into the interaction output channel.
        :param out: Message content string.
        :param interaction: The Interaction or Message.
        :param fresh: If fresh, will send a new message into the channel. This is not returned.
        :param mention: MentionOptions enum to specify what is pingable/pinged.
        """
        if not isinstance(out, str):
            raise TypeError(f'Instruction of type PUSH received an output object of type {type(out)}, which is not supported.')
        allowed_mentions = AllowedMentions.all() if mention.ALL else (AllowedMentions(everyone=False, roles=False, users=False, replied_user=True) if mention.AUTHOR else AllowedMentions.none())
        if isinstance(interaction, Message):
            if fresh:
                await interaction.channel.send(content=out, allowed_mentions=allowed_mentions)
            else:
                await interaction.reply(content=out, allowed_mentions=allowed_mentions)
        elif isinstance(interaction, Interaction):
            if fresh:
                await interaction.response.send_message(content=out, allowed_mentions=allowed_mentions)
            else:
                await interaction.followup.send(content=out, allowed_mentions=allowed_mentions)
        else:
            raise TypeError(f'PUSH instruction received an Interaction of type {type(interaction)}, which is not supported.')

    async def sleep(self, time: int | float):
        await _asyncio.sleep(time)

    def basic_replace(self, memdict: list[dict[str, ...]], key: str) -> str:
        result = self.mem_fetch(memdict, [key])[key]
        if not result:
            raise MemoryError(f'Cannot access memory entry \'{key}\'.')
        return str(result)

    async def is_writing(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        async with interaction.channel.typing():
            return await self.run(instructions, interaction, depth, build, False, fresh, memstack)

    async def choice(self, options: list[list[Instruction]], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        chosen: list[Instruction] = _r.choice(options)
        return await self.run(chosen, interaction, depth, build, False, fresh, memstack)

    def random(self, left: int, right: int) -> int:
        return _r.randint(left, right)

class DebugInstructionExecutor(InstructionExecutor):
    def __init__(self, client: BotClient = None):
        self.output: str = ''
        super().__init__(client)

    def _instruction_log(self, itype: str, extra: str = None):
        self.output += '{' + itype + ';' + (extra if extra else '') + '}'

    async def run(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple[str | None, bool]:
        # todo: determine if any initialization needs to be done here for memory evaluation.
        out = await super().run(instructions, interaction, depth, build, push_final_build, fresh, memstack)
        return out

    async def send_output(self, out: str, interaction: Interaction | Message, fresh: bool, mention: MentionOptions = MentionOptions.NONE):
        self.output += out
        self._instruction_log('PUSH', f'fr={fresh},mention={mention}')

    async def sleep(self, time: int | float):
        self._instruction_log('SLEEP', f'time={time}')

    def basic_replace(self, interaction: Interaction | Message, key: str) -> str:
        return '{BASIC_REPLACE;' + key + '}'

    async def is_writing(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        build += '{WRITING;Start {'
        build_out, first_reply = await self.run(instructions, interaction, depth, build, False, fresh, memstack)
        build += build_out if build_out else ''
        build += '} WRITING;End}'
        return build, first_reply

    async def choice(self, options: list[list[Instruction]], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        index: int = _r.randint(0, len(options) - 1)
        chosen: list[Instruction] = options[index]
        build += '{CHOICE['+str(index)+'] START; {'
        out, first_message =  await self.run(chosen, interaction, depth, build, False, fresh, memstack)
        out += '} CHOICE['+str(index)+'] END}'
        return out, first_message

    def init_memory(self, interaction: Interaction | Message) -> dict[str, ...]:
        now: _datetime.datetime = _datetime.datetime.now()
        out = {
            '\\n': '\n',

            'user.id': 0,
            'user': 'user',
            'user.name': 'user',
            'user.created_at': now,
            'user.account': 'useraccount',
            'user.mutual_guilds': 0,
            'user.roles': 0,

            'self.id': 0,
            'self': 'self',
            'self.name': 'self',
            'self.created_at': now,
            'self.account': 'selfaccount',
            'self.roles': 0,

            'channel': 'channel',
            'channel.id': 0,
            'channel.name': 'channel',
            'channel.created_at': now,
            'channel.jump_url': 'channelurl',

            'guild': 'guild',
            'guild.id': 0,
            'guild.name': 'guild',
            'guild.created_at': now,
            'guild.members': 0,
            'guild.roles': 0,

            # guild owner
            'owner.id': 0,
            'owner': 'owner',
            'owner.name': 'owner',
            'owner.created_at': now,
            'owner.account': 'owneraccount',
            'owner.roles': 0,
            'owner.mutual_guilds': 0,

            'message': 0,
            'message.jump_url': 'messageurl',

            # external
            'local_facts': 1,
            'global_facts': 1,
            'total_facts': 2,
        }
        self.check_init_memory(out)
        return out

    def random(self, left: int, right: int) -> int:
        self._instruction_log('RANDOM', f'left={left}, right={right}')
        return 0