import asyncio
import random

import discord
from discord import app_commands, Interaction, Message
from discord.ext import commands

from data.interfaces.saying import SayingInterface
from discorduser.user.abstract import BotClient
from piss import Instruction, parse_variables
from piss.instructionexecutor import InstructionExecutor


@app_commands.guild_only()
class AskPatrick(commands.Cog):
    def __init__(self, client: BotClient, saying: SayingInterface) -> None:
        self.client = client
        self.saying = saying

    @commands.Cog.listener("on_message")
    async def ask_patrick_listener(self, message: Message):
        if not message.content.lower().startswith(f"ask <@{self.client.user.id}>"):
            return
        # todo: check if command is callable here by user. If not, back out.
        split_content = message.content.split()
        if len(split_content) < 3:
            return  # Ignore if no question asked.
        await self.ask_patrick(message, " ".join(split_content[3:]))

    @app_commands.command(name="ask", description="A command-type shortcut to 'ask @botname <question>'.")
    @app_commands.describe(question="The question to ask.")
    async def ask_patrick_command(self, interaction: Interaction, question: str):
        await self.ask_patrick(interaction, question)

    async def ask_patrick(self, message: Message | Interaction, question: str):
        async def ask_reply(replyable: Message | Interaction, content: str,
                            send_in_channel: bool = False) -> None:
            if send_in_channel:
                await replyable.channel.send(content=content)
                return

            if isinstance(replyable, Interaction):
                await replyable.response.send_message(content=content)  # noqa
            else:
                await replyable.reply(mention_author=False, content=content)

        # todo: overhaul entirely. This is terrible.

        number = random.randint(1, 1000)
        # funny supersecret 1%%
        if number == 1:
            await ask_reply(message, "Ahem.")
            async with message.channel.typing():
                await asyncio.sleep(3)
                await ask_reply(message,  # todo: can be compacted into Instructions
                                "# **One day you will have to answer for your actions. And god.. may not be so merciful..**",
                                send_in_channel=True)
        # Yes 450%%
        elif number <= 451:
            await ask_reply(message, "Yes")
        # No 450%%
        elif number <= 901:
            await ask_reply(message, "No")
        elif number <= 951:
            saying: str = self.saying.get_saying()
            parsed: list[Instruction] = parse_variables(saying)
            executor: InstructionExecutor = InstructionExecutor(self.client)
            executor.fresh = False if isinstance(message, Message) else True # So we can reply to it if it is a message.
            await executor.run(parsed, message)
        else:
            await ask_reply(message, 'Haha I am immune to this question because I am queer')
