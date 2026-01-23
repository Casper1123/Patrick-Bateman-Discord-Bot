import discord
from discord.ext import commands


class LetterAutoreplyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def letter_only_replies(self, message: discord.Message):
        if message.author.bot:
            return

        if len(message.content) != 1:
            return

        letterdict = {"a": "b", "b": "c", "c": "d",
                      "d": "e", "e": "f", "f": "g",
                      "g": "h", "h": "i", "i": "j",
                      "j": "k", "k": "l", "l": "m",
                      "m": "n", "n": "o", "o": "p",
                      "p": "q", "q": "r", "r": "s",
                      "s": "t", "t": "u", "u": "v",
                      "v": "w", "w": "x", "x": "y",
                      "y": "z", "z": "a"}

        if message.content.lower() not in letterdict.keys():
            return

        if message.content.isupper():
            letter = letterdict[message.content.lower()].upper()
        else:
            letter = letterdict[message.content]
        await message.reply(mention_author=False, content=letter)