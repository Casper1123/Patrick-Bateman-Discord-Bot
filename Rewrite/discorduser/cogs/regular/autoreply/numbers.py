import discord
from discord.ext import commands

from Rewrite.data.interfaces.fact import FactInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.user.abstract import BotClient


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

        # todo: pattern matching and conversion.
        # Notes for later:
        # numbers [,] numbers [.]  [numbers [,] numbers] and mirrored
        # ?