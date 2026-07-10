import random as _r

import discord
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.variables_parser import Instruction, parse_variables
from Rewrite.variables_parser.instructionexecutor import InstructionExecutor

class MessageContentAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot, db: DataInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.db = db
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def message_content_replies(self, message: discord.Message):
        if message.author.bot:
            return

        # todo: figure shit out. Needs proper structure.