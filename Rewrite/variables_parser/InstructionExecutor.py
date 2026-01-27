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
    def __init__(self, client: BotClient):
        self.client = client

    async def run(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int = None, build: str = None, push_final_build: bool = True, fresh: bool = True) -> tuple(str | None, bool):
        # TODO: make fail if not ran in guild context. Do not let DM context make things more complicated. Get this to work first.
        depth: int = depth + 1 if depth else 0
        if depth > MAX_EXECUTION_RECUSION_DEPTH:
            raise ParsedExecutionRecursionDepthLimit(instructions, depth)
        first_reply = fresh
        i: int = 0
        build: str = build if build else "" # expanded until finished or message sends, then reset.
        mem: dict[str, ...] = {}
        while i < len(instructions):
            instruction = instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    # todo: settings for message. Assuming it's sent right now.
                    if build == "": raise ValueError('Instruction of type PUSH did not receive content to push.')
                    await self.send_output(build, interaction, first_reply=first_reply)
                    build = ""
                    first_reply = False
                elif instruction.type == InstructionType.DEFINE:
                    mem[str(instruction.options['name'])] = instruction.options['value']
                elif instruction.type == InstructionType.SLEEP:
                    await self.sleep(instruction.options['time'])
                elif instruction.type == InstructionType.BASIC_REPLACE:
                    build += self.basic_replace(interaction, instruction.options['key'])
                elif instruction.type == InstructionType.WRITING:
                    build, first_reply = await self.is_writing(instruction.options['instructions'], interaction, depth, build)
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
            await self.send_output(build, interaction, first_reply=first_reply)
            return None, first_reply
        else:
            return build, first_reply

    async def send_output(self, out: str, interaction: discord.Interaction | discord.Message, first_reply: bool = True) -> None:
        ...  # todo: implement sending data.
        if isinstance(interaction, discord.Message):
            ... # case Message
            # reply
            interaction.reply(out, delete_after=..., mention_author=..., allowed_mentions=...)
            # not reply
            interaction.channel.send(out, delete_after=..., mention_author=..., allowed_mentions=...)
            # Allowed mentions notes, see contructor:
            discord.AllowedMentions(everyone= False, users = False, roles = False, replied_user=False) # users & roles can be collections as well.
            discord.AllowedMentions.all() # also an option
        else:
            ... # case Interaction
            interaction.edit_original_response(out, allowed_mentions=...)



    async def sleep(self, time: int | float):
        await _asyncio.sleep(time)

    def basic_replace(self, interaction: discord.Interaction | discord.Message, key: str) -> str:
        raise NotImplementedError()

    async def is_writing(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int, build: str) -> tuple[str | None, bool]:
        async with interaction.channel.typing():
            return await self.run(instructions, interaction, depth, build, False)

class DebugInstructionExecutor(InstructionExecutor):
    def __init__(self, client: BotClient):
        super().__init__(client)

    async def send_output(self, out: str, interaction: discord.Interaction | discord.Message, first_reply: bool = True):
        raise NotImplementedError()

    async def sleep(self, time: int | float):
        raise NotImplementedError()

    async def basic_replace(self, interaction: discord.Interaction | discord.Message, key: str) -> str:
        raise NotImplementedError()

    async def is_writing(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message, depth: int, build: str) -> tuple[str | None, bool]:
        build += '{ As writing; Start }'
        build_out, first_reply = await self.run(instructions, interaction, depth, build, False)
        build += build_out if build_out else ''
        build += '{ As writing; End }'
        return build, first_reply