import discord
from discord import Embed, Colour
from discord.ext import commands

from discorduser.logger import GlobalLogger
from discorduser.user.abstract import BotClient


class ListenerCog(commands.Cog):
    def __init__(self, bot: BotClient, logger: GlobalLogger) -> None:
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener("on_ready")
    async def on_ready_gaming(self):
        await self.bot.change_presence(activity=discord.Game(name="you like a fiddle"), status=discord.Status.idle)
        out: str = f"Bot ready in {len(self.bot.guilds)} servers"
        for guild in self.bot.guilds:
            out += f'\n\t{guild.name} ({guild.id}) : {len(guild.members)}'
        await self.logger.log_general(
            console=out,
            channel=Embed(
                title='Bot online',
                description='Bot online and ready.',
                colour=Colour.green()
            )
        )
