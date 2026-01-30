import asyncio as _asyncio
import random as _r
import datetime as _datetime

import discord
from discord import AllowedMentions, Message, Interaction
from discord.ext import commands

from Rewrite.utilities.exceptions import CustomDiscordException
from Rewrite.discorduser import BotClient
from . import Instruction, InstructionType, MentionOptions


class ParsedExecutionFailure(CustomDiscordException):
    def __init__(self, instruction: Instruction, index: int, cause: Exception | None = None) -> None:
        super().__init__(f'Failed to execute Instruction of type **{instruction.type}** (index {index}) given options \'{instruction.options}\'', cause)

class ParsedExecutionRecursionDepthLimit(CustomDiscordException):
    def __init__(self, instructions: list[Instruction], depth: int) -> None:
        super().__init__(f'Maximum recursion depth of {depth} exceeded maximal value when executing Instructions.\n'
                         f'{"\n".join(str(i) for i in instructions)}')

MAX_EXECUTION_RECURSION_DEPTH = 5 # todo: into config file you go.

class InstructionExecutor:
    """
    One call per instance, in part to be compatible with the debugger.
    todo: pass around the constructor as a method to call from a global scope or nah?
    """
    def __init__(self, client: BotClient):
        self.client = client

    async def run(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple[str | None, bool]:
        if not interaction.guild.id:
            raise PermissionError('Cannot execute instructions outside of Guild context.')
        depth: int = depth + 1 if depth else 0
        if depth > MAX_EXECUTION_RECURSION_DEPTH:
            raise ParsedExecutionRecursionDepthLimit(instructions, depth)
        first_reply = fresh
        i: int = 0
        build: str = build if build else "" # expanded until finished or message sends, then reset. Highest scope is first.
        mem: dict[str, ...] = {} if memstack else self.init_memory(interaction)
        memstack = memstack if memstack else [] # outer scope memory. Initialize here for now.
        while i < len(instructions):
            instruction = instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    if build == "": raise ValueError('Instruction of type PUSH did not receive content to push.')
                    await self.send_output(build, interaction, fresh=first_reply)
                    build = ""
                    first_reply = False
                elif instruction.type == InstructionType.DEFINE:
                    # fixme: match with banlist for other things? Or handle this properly with the parser.
                    name: str = str(instruction.options['name'])
                    value: object = instruction.options['value']
                    assigned: bool = False
                    for scope in memstack:
                        if name in scope.keys():
                            assigned = True
                            scope[name] = value
                    if not assigned:
                        mem[name] = value

                elif instruction.type == InstructionType.SLEEP:
                    await self.sleep(instruction.options['time'])
                elif instruction.type == InstructionType.BASIC_REPLACE:
                    build += self.basic_replace(interaction, instruction.options['key'])
                elif instruction.type == InstructionType.WRITING:
                    build, first_reply = await self.is_writing(instruction.options['instructions'], interaction, depth, build, fresh, memstack)
                    if build is None:
                        raise TypeError('Instruction of type WRITING returned None value instead of String.')
                elif instruction.type == InstructionType.CHOICE:
                    build, first_reply = await self.choice(instruction.options['options'], interaction, depth, build, fresh, memstack)
                elif instruction.type == InstructionType.CALCULATE:
                    self.calculate(instruction.options, memstack)
                else:
                    raise NotImplementedError()
            except NotImplementedError:
                build += '{ Skip exec of type ' + str(instruction.type) + '; NotImplemented }'
            except Exception as e:
                raise ParsedExecutionFailure(instruction, i, cause=e)
            i += 1

        if build and push_final_build:
            await self.send_output(build, interaction, fresh=first_reply, mention=MentionOptions.NONE) # Defaults to not mentioning. Should have PUSHed beforehand.
            return None, first_reply
        else:
            return build, first_reply

    def init_memory_types(self) -> dict[str, type]:
        """
        Used for type checking in available variables in instruction parsing.
        Genuinely only in here because I wanted a way to get the types of objects that could never be declared and did not know another way to do things.
        Look, I'll think of something to replace this properly okay. I just wanted this information available now so I can work on the Parser
        :return: The types of variables declared by default by InstructionExecutor.init_memory
        """
        return {
                '\\n': str,

                # interaction target
                'user.id': int,
                'user': str,
                'user.name': str,
                'user.created_at': _datetime.datetime,
                'user.account': str,
                'user.status': str,
                'user.mutual_guilds': int,
                'user.roles': int,  # role count, not the actual roles.

                'self.id': int,
                'self': str,
                'self.name': str,
                'self.created_at': _datetime.datetime,
                'self.account': str,
                'self.roles': int,

                'channel': str,
                'channel.id': int,
                'channel.name': str,
                'channel.created_at': _datetime.datetime,
                'channel.jump_url': str,

                'guild': str,
                'guild.id': int,
                'guild.name': str,
                'guild.created_at': _datetime.datetime,
                'guild.members': int, # member count
                'guild.roles': int, # still, role count.

                # guild owner
                'owner.id': int,
                'owner': str,
                'owner.name': str,
                'owner.created_at': _datetime.datetime,
                'owner.account': str,
                'owner.roles': int,

                'message': int,
                'message.jump_url': str,
            }
    async def init_memory(self, interaction: Interaction | Message) -> dict[str, ...]:
        user: discord.User = interaction.user
        member: discord.Member = interaction.guild.get_member(interaction.user.id)
        me: discord.ClientUser = self.client.user
        me_member: discord.Member = interaction.guild.get_member(me.id)

        channel: discord.TextChannel = interaction.channel
        guild: discord.Guild = interaction.guild
        owner: discord.Member = guild.owner  # guild owner

        if None in [member, me, me_member] or not isinstance(me, discord.abc.User):
            raise ValueError('Cannot prepare memory data, missing required data to construct initial memory.')
        try:
            return {
                '\\n': '\n',

                # interaction target
                'user.id': user.id,
                'user': user.display_name,
                'user.name': user.display_name,
                'user.created_at': user.created_at,
                'user.account': user.name,
                'user.status': str(member.client_status) if member.client_status not in [discord.Status.dnd, discord.Status.do_not_disturb] else 'do not disturb',
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

                'message': interaction.message.id,
                'message.jump_url': interaction.message.jump_url,
            }
        except Exception as e:
            raise CustomDiscordException('Initial Instruction Memory failed to build.', e, 'InstructionMemoryError')

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
        # merge memdict into a single dict:
        mem: dict[str, ...] = {}
        for frame in reversed(memdict): # reversed so, if somehow duplicates exist, the top-framed one takes precedence
            for k, v in frame.items():
                mem[k] = v

        if key not in mem.keys():
            raise MemoryError(f'Cannot access memory entry \'{key}\'.')
        return str(mem[key])

    async def is_writing(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        async with interaction.channel.typing():
            return await self.run(instructions, interaction, depth, build, False, fresh, memstack)

    async def choice(self, options: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        chosen: Instruction = _r.choice(options)
        return await self.run([chosen], interaction, depth, build, False, fresh, memstack)

    def calculate(self, options: dict[str, ...], memstack: list[dict[str, ...]]) -> None:
        ... # todo how in the world should calculations be performed? 

class DebugInstructionExecutor(InstructionExecutor):
    def __init__(self, client: BotClient):
        self.output: str = ''
        super().__init__(client)

    def _instruction_log(self, itype: str, extra: str = None):
        self.output += '{ ' + itype + '; ' + extra if extra else '' + ' }'

    async def run(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple[str | None, bool]:
        # todo: determine if any initialization needs to be done here for memory evaluation.
        out = await super().run(instructions, interaction, depth, build, push_final_build, fresh, memstack)
        return out

    async def send_output(self, out: str, interaction: Interaction | Message, fresh: bool, mention: MentionOptions = MentionOptions.NONE):
        self.output += out
        self._instruction_log('PUSH', f'fr={fresh},mention={mention}')

    async def sleep(self, time: int | float):
        self._instruction_log('SLEEP', f'time={time}')

    async def basic_replace(self, interaction: Interaction | Message, key: str) -> str:
        return '{ BASIC_REPLACE; ' + key + ' }'

    async def is_writing(self, instructions: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        build += '{ WRITING; Start {'
        build_out, first_reply = await self.run(instructions, interaction, depth, build, False, fresh, memstack)
        build += build_out if build_out else ''
        build += '} WRITING; End }'
        return build, first_reply

    async def choice(self, options: list[Instruction], interaction: Interaction | Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        index: int = _r.randint(0, len(options) - 1)
        chosen: Instruction = options[index]
        build += '{ CHOICE ['+str(index)+'] START; {'
        out, first_message =  await self.run([chosen], interaction, depth, build, False, fresh, memstack)
        out += '} CHOICE ['+str(index)+'] END }'
        return out, first_message

    def init_memory(self, interaction: Interaction | Message) -> dict[str, ...]:
        now: _datetime.datetime = _datetime.datetime.now()
        return {
            '\\n': '\n',

            'user.id': 0,
            'user': 'user',
            'user.name': 'user',
            'user.created_at': now,
            'user.account': 'useraccount',
            'user.status': 'userstatus',
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

            'message': 0,
            'message.jump_url': 'messageurl',
        }