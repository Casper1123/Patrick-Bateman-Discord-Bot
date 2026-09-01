import discord
from discord import app_commands
from discord.ext import commands

from data.interfaces.pref import PreferencesInterface
from discorduser.user.abstract import BotClient


@app_commands.guild_only()
class NumberAutoreplyCog(commands.Cog):
    def __init__(self, client: BotClient, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    @commands.Cog.listener("on_message")
    async def number_only_replies(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if self.pref.is_paused_channel(message.guild.id, message.channel.id):
            return
        if not self.pref.is_user_autoreply_enabled(message.author.id, 'number'):
            return
        if not self.pref.is_autoreply_enabled(message.guild.id, message.channel.id, 'number'):
            return

        # Todo: optimizable / improvable
        # Example: something with text after the first space is clearly more than just a number

        # todo: fixme;; 1231087891741,100009908 -> 1231087891742.1
        # Solution: cast to int, lose floating point, remove that as the prefix, keep the remainder, append that at the end.
        txt: str = message.content
        try:
            num: float = float(txt)
        except ValueError:
            txt = txt.replace(',', '.')
            try:
                num: float = float(txt)
            except ValueError:
                return  # More expressive matching
        if num == int(num) and not '.' in txt:
            num = int(num)

        num += 1

        txt = str(num)
        await message.reply(txt, mention_author=False)
