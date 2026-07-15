import random as _r

import discord
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.piss import Instruction, parse_variables
from Rewrite.piss.instructionexecutor import InstructionExecutor


class RandomAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot, db: DataInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.db = db
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def random_saying_replies(self, message: discord.Message): # todo: rename 'saying', like what the fuck is this dude.
        if message.author.bot:
            return

        if _r.randint(1, 300) != 1: # todo: config probability
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return

        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'saying'):
            return
        
        line_raw: str = self.db.get_saying()
        line: list[Instruction] = parse_variables(line_raw)
        executor: InstructionExecutor = InstructionExecutor(self.client, self.db)
        await executor.run(line, interaction=message)