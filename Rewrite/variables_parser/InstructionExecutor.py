import asyncio as _asyncio

import discord
from discord.ext import commands

from Rewrite.utilities.exceptions import CustomDiscordException
from Rewrite.discorduser import BotClient
from . import Instruction, InstructionType


class ParsedExecutionFailure(CustomDiscordException):
    def __init__(self, instruction: Instruction, cause: Exception | None = None) -> None:
        super().__init__(f'Failed to execute Instruction of type **{instruction.type}** given options \'{instruction.options}\'', cause)



class InstructionExecutor:
    def __init__(self, client: BotClient):
        self.client = client

    async def run(self, instructions: list[Instruction], interaction: discord.Interaction | discord.Message):
        # TODO: make fail if not ran in guild context. Do not let DM context make things more complicated. Get this to work first.
        i: int = 0
        build: str = "" # expanded until finished or message sends, then reset.
        mem: dict[str, ...] = {}
        while i < len(instructions):
            instruction = instructions[i]
            try:
                if instruction.type == InstructionType.BUILD:
                    build += instruction.options['content']
                elif instruction.type == InstructionType.PUSH:
                    # todo: settings for message. Assuming it's sent right now.
                    await self.send_output(build)
                    build = ""
                elif instruction.type == InstructionType.DEFINE:
                    mem[instruction.options['name']] = instruction.options['content']
                elif instruction.type == InstructionType.SLEEP:
                    await self.sleep(instruction.options['content'])
                else:
                    build += '{ Skip exec of type ' + instruction.type + '; NotImplemented }'
            except Exception as e:
                raise ParsedExecutionFailure(instruction, cause=e)
            i += 1
        if build:
            await self.send_output(build)

    async def send_output(self, out: str):
        ...  # todo: implement sending data.
        if out == "": out = "{ ? Empty output string ? }"  # cannot send empty data. Substituting to allow for debugging.

    async def sleep(self, time: int | float):
        await _asyncio.sleep(time)

class DebugInstructionExecutor(InstructionExecutor):
    def __init__(self, client: BotClient):
        super().__init__(client)

    async def send_output(self, out: str):
        raise NotImplementedError()

    async def sleep(self, time: int | float):
        raise NotImplementedError()