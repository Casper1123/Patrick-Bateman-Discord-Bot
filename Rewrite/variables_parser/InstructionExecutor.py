import asyncio as _asyncio

import discord
from discord.ext import commands

from Rewrite.utilities.exceptions import CustomDiscordException
from Rewrite.discorduser import BotClient
from . import Instruction, InstructionType


class ParsedExecutionFailure(CustomDiscordException):
    def __init__(self, instruction: Instruction, index: int, cause: Exception | None = None) -> None:
        super().__init__(f'Failed to execute Instruction of type **{instruction.type}** (index {index}) given options \'{instruction.options}\'', cause)

class ParsedExecutionRecursionDepthLimit(CustomDiscordException):
    def __init__(self, instructions: list[Instruction], depth: int) -> None:
        super().__init__(f'Maximum recursion depth of {depth} exceeded maximal value when executing Instructions.\n'
                         f'{"\n".join(str(i) for i in instructions)}')

MAX_EXECUTION_RECUSION_DEPTH = 5 # todo: into config file you go.

class InstructionExecutor:
    """
    One call per instance, in part to be compatible with the debugger.
    todo: pass around the constructor as a method to call from a global scope or nah?
    """
    def __init__(self, client: BotClient):
        self.client = client

    async def run(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple(str | None, bool):
        if not interaction.guild.id:
            raise PermissionError('Cannot execute instructions outside of Guild context.')
        depth: int = depth + 1 if depth else 0
        if depth > MAX_EXECUTION_RECUSION_DEPTH:
            raise ParsedExecutionRecursionDepthLimit(instructions, depth)
        first_reply = fresh
        i: int = 0
        build: str = build if build else "" # expanded until finished or message sends, then reset. Highest scope is first.
        mem: dict[str, ...] = {}
        memstack = memstack if memstack else [] # outer scope memory. Initialize here for now.
        while i < len(instructions):
            instruction = instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    # todo: settings for message. Assuming it's sent right now.
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
                else:
                    raise NotImplementedError()
            except NotImplementedError:
                build += '{ Skip exec of type ' + str(instruction.type) + '; NotImplemented }'
            except Exception as e:
                raise ParsedExecutionFailure(instruction, i, cause=e)
            i += 1

        if build and push_final_build:
            await self.send_output(build, interaction, fresh=first_reply)
            return None, first_reply
        else:
            return build, first_reply

    async def send_output(self, out: str, interaction: discord.Interaction | discord.Message, fresh: bool = True) -> None:
        ...  # todo: implement sending data.
        if isinstance(interaction, discord.Message):
            ... # case Message
            # reply
            interaction.reply(out, mention_author=..., allowed_mentions=...)
            # not reply
            interaction.channel.send(out, mention_author=..., allowed_mentions=...)
            # Allowed mentions notes, see constructor:
            discord.AllowedMentions(everyone= False, users = False, roles = False, replied_user=False) # users & roles can be collections as well.
            discord.AllowedMentions.all() # also an option
        else:
            ... # case Interaction
            interaction.edit_original_response(out, allowed_mentions=...) # delete after...?
            interaction.followup.send(content=out, allowed_mentions=...)



    async def sleep(self, time: int | float):
        await _asyncio.sleep(time)

    def basic_replace(self, interaction: discord.Interaction | discord.Message, key: str) -> str:
        raise NotImplementedError()

    async def is_writing(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        async with interaction.channel.typing():
            return await self.run(instructions, interaction, depth, build, False, fresh, memstack)

class DebugInstructionExecutor(InstructionExecutor):
    def __init__(self, client: BotClient):
        self.output: str = ''
        super().__init__(client)

    def _instruction_log(self, itype: str, extra: str = None):
        self.output += '{ ' + itype + '; ' + extra if extra else '' + ' }'

    async def run(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True, memstack: list[dict[str, ...]] = None) -> tuple[str | None, bool]:
        # fixme: determine if any initialization needs to be done here for memory evaluation.
        out = await super().run(instructions, interaction, depth, build, push_final_build, fresh, memstack)
        return out

    async def send_output(self, out: str, interaction: discord.Interaction | discord.Message, fresh: bool = True):
        self._instruction_log('PUSH', f'fr={fresh}')

    async def sleep(self, time: int | float):
        self._instruction_log('SLEEP', f'time={time}')

    async def basic_replace(self, interaction: discord.Interaction | discord.Message, key: str) -> str:
        return '{ BASIC_REPLACE; ' + key + ' }'

    async def is_writing(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int, build: str, fresh: bool, memstack: list[dict[str, ...]]) -> tuple[str | None, bool]:
        build += '{ WRITING; Start {'
        build_out, first_reply = await self.run(instructions, interaction, depth, build, False, fresh, memstack)
        build += build_out if build_out else ''
        build += '} WRITING; End }'
        return build, first_reply