import random as _r

import discord
from discord.ext import commands

from configuration.global_config import CFG
from data.interfaces.pref import PreferencesInterface
from data.interfaces.saying import SayingInterface
from discorduser.user.abstract import BotClient
from piss import Instruction, parse_variables
from piss.instructionexecutor import InstructionExecutor


class RandomAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, say: SayingInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.say = say
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def random_saying_replies(self, message: discord.Message): # todo: rename 'saying', like what the fuck is this dude.
        if message.author.bot:
            return

        if _r.randint(1, CFG.SAYING_PROBABILIY) != 1:
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return

        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'saying'):
            return
        
        line_raw: str = self.say.get_saying()
        line: list[Instruction] = parse_variables(line_raw)
        executor: InstructionExecutor = InstructionExecutor(self.client)
        await executor.run(line, interaction=message)