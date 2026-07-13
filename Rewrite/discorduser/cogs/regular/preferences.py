import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface


class UserPreferenceCog(commands.Cog):
    def __init__(self, client: commands.Bot, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # User preference toggle.
    @app_commands.command(name="preferences", description="Toggle automatic features for yourself.")
    @app_commands.describe(numbers="Incremental number replies.", letters='Letter-only replies.', text='Text content replies.')
    async def user_toggle_preference(self, interaction: discord.Interaction, numbers: bool = False, letters: bool = False, text: bool = False):
        if not (numbers or letters or text):
            await interaction.response.