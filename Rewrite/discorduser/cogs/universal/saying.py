import discord
from discord import app_commands, Interaction, Embed, Guild, Colour
from discord.ext import commands

from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface
from Rewrite.discorduser.logger import GlobalLogger
from Rewrite.discorduser.user.abstract import BotClient

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class GlobalAdminSayingCog(commands.Cog, name='saying'):
    def __init__(self, client: BotClient, saying: GlobalAdminSayingInterface, logger: GlobalLogger) -> None:
        self.client = client
        self.saying = saying
        self.logger = logger

    # todo: create
    # create
    # edit
    # delete