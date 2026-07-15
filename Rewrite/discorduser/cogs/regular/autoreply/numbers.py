import discord
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface


class NumberAutoreplyCog(commands.Cog):
    def __init__(self, client: commands.Bot, db: DataInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.db = db
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

        # todo: pattern matching and conversion.
        # Notes for later:
        # numbers [,] numbers [.]  [numbers [,] numbers] and mirrored
        # ?