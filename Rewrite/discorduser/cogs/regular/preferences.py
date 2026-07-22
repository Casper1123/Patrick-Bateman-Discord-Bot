import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface, _supp_autr_features, UserPreferenceData
from Rewrite.discorduser.user.abstract import BotClient


@app_commands.guild_only()
class UserPreferenceCog(commands.Cog):
    def __init__(self, client: BotClient, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # User preference toggle.
    # Note: autocomplete not supported for Boolean types.
    @app_commands.command(name="preferences", description="Toggle automatic features for yourself. Set to True to toggle.")
    @app_commands.describe(numbers="Incremental number replies.", letters='Letter-only replies.', text='Text content replies.')
    async def user_toggle_preference(self, interaction: discord.Interaction, numbers: bool = False, letters: bool = False, text: bool = False):
        # Not allowing to disable sayings is on purpose.
        await interaction.response.defer(ephemeral=True, thinking=True)
        pref: UserPreferenceData = self.pref.user_autoreplies_enabled(interaction.user.id)
        if not (numbers or letters or text):
            await interaction.edit_original_response(embed=discord.Embed(title=f'User preference for {interaction.user.name}',
                                                                         description=f'**Number:** {'Off' if not pref.number else 'On'}\n'
                                                                                     f'**Letter:** {'Off' if not pref.letter else 'On'}\n'
                                                                                     f'**Text:** {'Off' if not pref.text else 'On'}\n'))
            return
        desc: str = ''
        feat: set[_supp_autr_features] = set() # noqa because empty set
        if numbers:
            feat.add('number')
            desc += f'**Number:** {'Off' if pref.number else 'On'}\n'
        if letters:
            feat.add('letter')
            desc += f'**Letter:** {'Off' if pref.letter else 'On'}\n'
        if text:
            feat.add('text')
            desc += f'**Text:** {'Off' if pref.text else 'On'}\n'

        assert feat.__sizeof__() > 0, 'Set of selected features is 0 even though some feature was selected.'

        self.pref.toggle_user_autoreply_feature(interaction.user.id, feat)

        desc = desc.removesuffix('\n')
        await interaction.edit_original_response(embed=discord.Embed(
            title='User preferences updated',
            description=desc,
        ))