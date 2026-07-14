import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface, _supp_autr_features


class UserPreferenceCog(commands.Cog):
    def __init__(self, client: commands.Bot, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # User preference toggle.
    @app_commands.command(name="preferences", description="Toggle automatic features for yourself.")
    @app_commands.describe(numbers="Incremental number replies.", letters='Letter-only replies.', text='Text content replies.')
    async def user_toggle_preference(self, interaction: discord.Interaction, numbers: bool = False, letters: bool = False, text: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not (numbers or letters or text):
            await interaction.edit_original_response(content='Please select an option.')
            return
        desc: str = ''
        feat: set[_supp_autr_features] = set() # noqa because empty set
        if numbers:
            feat.add('number')
            val: bool = self.pref.is_user_autoreply_enabled(interaction.user.id, 'number') # todo: optimize with one pref call -> take set of feat and open 1 connection.
            desc += f'**Number:** {not val}\n'
        if letters:
            feat.add('letter')
            val: bool = self.pref.is_user_autoreply_enabled(interaction.user.id, 'letter')
            desc += f'**Letter:** {not val}\n'
        if text:
            feat.add('text')
            val: bool = self.pref.is_user_autoreply_enabled(interaction.user.id, 'text')
            desc += f'**Text:** {not val}\n'

        assert feat.__sizeof__() > 0, 'Set of selected features is 0 even though some feature was selected.'

        self.pref.toggle_user_autoreply_feature(interaction.user.id, feat)
        desc = desc.removesuffix('\n')
        await interaction.edit_original_response(embed=discord.Embed(
            title='User preferences updated',
            description=desc,
        ))
