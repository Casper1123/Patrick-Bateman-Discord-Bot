import re as _re

import discord
from discord.ext import commands

from data.interfaces.pref import PreferencesInterface
from discorduser.user.abstract import BotClient

class NumberAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def number_only_replies(self, message: discord.Message):
        if message.author.bot:
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return
        if not self.pref.is_user_autoreply_enabled(message.author.id, 'number'):
            return
        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'number'):
            return
        txt: str = message.content
        try:
            num: float = float(txt)
        except ValueError:
            txt = txt.replace(',', '.')
            try:
                num: float = float(txt)
            except ValueError:
                return # More expressive matching
        if num == int(num) and not '.' in txt:
            num = int(num)

        num += 1

        txt = str(num)
        await message.reply(txt, mention_author=False)
