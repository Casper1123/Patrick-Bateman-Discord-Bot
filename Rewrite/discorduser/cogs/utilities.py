import discord
from discord.ext import commands

from Rewrite.discorduser.user.abstract import BotClient


class ListenerCog(commands.Cog):
    def __init__(self, bot: BotClient) -> None:
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def on_ready_gaming(self):
        await self.bot.change_presence(activity=discord.Game(name="you like a fiddle"), status=discord.Status.idle)
        print(f"Bot ready in {len(self.bot.guilds)} servers")
        for guild in self.bot.guilds:
            print(f"\t{guild.name} : {len(guild.members)} members")
        # todo: log