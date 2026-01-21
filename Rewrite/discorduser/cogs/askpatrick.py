import asyncio as _asyncio
import random as _r

import discord
from discord import app_commands
from discord.ext import commands


class AskPatrick(commands.Cog):
    def __init__(self, client: commands.bot) -> None:
        self.client = client

    @commands.Cog.listener("on_message")
    async def ask_patrick_listener(self, message: discord.Message):
        if not message.content.lower().startswith(f"ask <@{self.client.user.id}>"):
            return
        if len(message.content.split()) < 3:
            return # Ignore if no question asked.

        await self.ask_patrick(message, " ".join(message.content.split()[3:]))

    @app_commands.command(name="ask", description="A command-type shortcut to 'ask @botname <question>'.")
    @app_commands.describe(question="The question to ask.")
    async def ask_patrick_command(self, interaction: discord.Interaction, question: str):
        await self.ask_patrick(interaction, question)

    async def ask_patrick(self, message: discord.Message | discord.Interaction, question: str):
        async def ask_reply(replyable: discord.Message | discord.Interaction, content: str,
                            send_in_channel: bool = False) -> None:
            if send_in_channel:
                await replyable.channel.send(content=content)
                return

            if isinstance(replyable, discord.Interaction):
                await replyable.response.send_message(content=content)
            else:
                await replyable.reply(mention_author=False, content=content)
        # todo: system with weighted replies. Replies are defined as instructions.
        raise NotImplementedError()
        """
        # funny supersecret 1%%
        if number == 1:
            await ask_reply(message, "Ahem.")
            async with message.channel.typing():
                await _asyncio.sleep(3)
                await ask_reply(message,  # todo: can be compacted into Instructions
                                "# **One day you will have to answer for your actions. And god.. may not be so merciful..**",
                                send_in_channel=True)
        # Yes 450%%
        elif number <= 451:
            await ask_reply(message, "Yes")
        # No 450%%
        elif number <= 901:
            await ask_reply(message, "No")
        # Random bouncerline 50%%
        elif number <= 951:
            await ask_reply(message,
                            process_variables(self.cm.sayings.get_line(None), self.cm.facts_manager, message, self.bot))
        # Drunk too much, random bouncerwords 49%%
        elif number <= 1000:
            await ask_reply(message, "*He's drank too many beers.*")
            await ask_reply(message, " ".join(
                [_r.choice(self.cm.sayings.get_sayings_words()) for _ in range(_r.randint(1, 20))]),
                            send_in_channel=True)
        # krabklub only: I dunno lemme ask the bouncer 50%%
        elif number <= 1050:
            await ask_reply(message, "I don't know, let me ask the Bouncer")
            await ask_reply(message, f"ask <@756190206591369437> {question}", send_in_channel=True)
        """
