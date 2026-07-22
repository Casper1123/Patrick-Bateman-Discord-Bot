import discord
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.discorduser.user.abstract import BotClient

_letterdict = {"a": "b", "b": "c", "c": "d",
              "d": "e", "e": "f", "f": "g",
              "g": "h", "h": "i", "i": "j",
              "j": "k", "k": "l", "l": "m",
              "m": "n", "n": "o", "o": "p",
              "p": "q", "q": "r", "r": "s",
              "s": "t", "t": "u", "u": "v",
              "v": "w", "w": "x", "x": "y",
              "y": "z", "z": "a"}

class LetterAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, db: DataInterface, pref: PreferencesInterface) -> None:
        self.client = client
        self.db = db
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def letter_only_replies(self, message: discord.Message):
        if message.author.bot:
            return

        if len(message.content) != 1:
            return

        if message.content.lower() not in _letterdict.keys():
            return
        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return
        if not self.pref.is_user_autoreply_enabled(message.author.id, 'letter'):
            return
        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'letter'):
            return

        letter: str = _letterdict[message.content]
        if message.content.isupper():
            letter = letter.upper()

        await message.reply(mention_author=False, content=letter)