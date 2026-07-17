# NOTE: COMMANDS ARE NOT GLOBALLY USABLE, THEY ARE GLOBAL ADMIN
import io as _io
import json as _json

import discord
from discord import app_commands, Interaction, Embed, Guild
from discord.ext import commands

from Rewrite.discorduser import BotClient
from Rewrite.data.interfaces.data import GlobalAdminDataInterface, FactEditorData
from Rewrite.utilities.exceptions import CustomDiscordException, ErrorTooltip
from Rewrite.piss.testing import test_raw_input as input_test

GLOBAL_ADMIN_SERVER_ID: int = 0 # todo: config input

@app_commands.default_permissions(administrator=True)
@app_commands.guilds(discord.Object(id=GLOBAL_ADMIN_SERVER_ID))
class GlobalAutoreplyAdminCog(commands.Cog, name='autoreply'):
    def __init__(self, client: BotClient,  db: GlobalAdminDataInterface, logger) -> None:
        self.client = client
        self.db = db
        self.logger = logger

    # region autoreply
    # Create Alias
    # Edit / Delete Alias
    # 
    # endregion autoreply