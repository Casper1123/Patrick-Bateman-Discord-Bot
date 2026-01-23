import discord
from discord.ext import commands


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def on_ready_gaming(self):
        await self.bot.change_presence(activity=discord.Game(name="you like a fiddle"), status=discord.Status.idle) # TODO: configurable in config file bc why not.
        print(f"Bot ready in {len(self.bot.guilds)} servers")
        # todo: log