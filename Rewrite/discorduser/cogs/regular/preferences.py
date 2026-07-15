import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface, _supp_autr_features, UserPreferenceData


class UserPreferenceCog(commands.Cog):
    def __init__(self, client: commands.Bot, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # User preference toggle.
    @app_commands.command(name="channel_preferences", description="Toggle automatic features for yourself. Set to True to toggle.")
    @app_commands.describe(numbers="Incremental number replies.", letters='Letter-only replies.', text='Text content replies.')
    async def user_toggle_preference(self, interaction: discord.Interaction, numbers: bool = False, letters: bool = False, text: bool = False):
        # Not allowing to disable sayings is on purpose.
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not (numbers or letters or text):
            await interaction.edit_original_response(content='Please select at least one option.')
            return
        desc: str = ''
        feat: set[_supp_autr_features] = set() # noqa because empty set
        pref: UserPreferenceData = self.pref.user_autoreplies_enabled(interaction.user.id)
        if numbers:
            feat.add('number')
            desc += f'**Number:** {not pref.number}\n'
        if letters:
            feat.add('letter')
            desc += f'**Letter:** {not pref.letter}\n'
        if text:
            feat.add('text')
            desc += f'**Text:** {not pref.text}\n'

        assert feat.__sizeof__() > 0, 'Set of selected features is 0 even though some feature was selected.'

        self.pref.toggle_user_autoreply_feature(interaction.user.id, feat)

        desc = desc.removesuffix('\n')
        await interaction.edit_original_response(embed=discord.Embed(
            title='User preferences updated',
            description=desc,
        ))
