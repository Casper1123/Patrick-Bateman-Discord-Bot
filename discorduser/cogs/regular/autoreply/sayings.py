import random as _r

import discord
from discord import app_commands
from discord.ext import commands

from configuration.global_config import CFG
from data.interfaces.pref import PreferencesInterface
from data.interfaces.saying import SayingInterface
from discorduser.user.abstract import BotClient
from piss.instructions.abstract import Instruction
from piss.parsing import parse_instructions_from_string
from piss.executing import InstructionExecutor


@app_commands.guild_only()
class RandomAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, say: SayingInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.say = say
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def random_saying_replies(self,
                                    message: discord.Message):  # todo: rename 'saying', like what the fuck is this dude.
        if not message.guild:
            return

        if message.author.bot:
            return

        if _r.randint(1, CFG.SAYING_PROBABILITY) != 1:
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return

        if not self.pref.guild_channel_autoreplies_enabled(message.guild.id, message.channel.id).saying:
            return

        line_raw: str = self.say.get_saying()
        line: list[Instruction] = parse_instructions_from_string(line_raw)
        executor: InstructionExecutor = InstructionExecutor()
        await executor.run(self.client, line, interaction=message)
