from discord import app_commands, Interaction
from discord.ext import commands

from data.interfaces.pref import PreferencesInterface, supported_autoreply_features, UserPreferenceData
from discorduser.user.abstract import BotClient


@app_commands.guild_only()
class UserPreferenceCog(commands.Cog):
    def __init__(self, client: BotClient, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # User preference toggle.
    # Note: autocomplete not supported for Boolean types.
    @app_commands.command(name="preferences",
                          description="Change enabled automated reply features. Anything set to True is enabled.")
    @app_commands.describe(numbers="Incremental number replies.", letters='Letter-only replies.',
                           text='Text content replies.')
    async def user_toggle_preference(self, interaction: Interaction, numbers: bool, letters: bool,
                                     text: bool):
        await interaction.response.defer(ephemeral=True, thinking=True)

        desc: str = ''
        feat: set[supported_autoreply_features] = set()
        if numbers:
            feat.add('number')
            desc += f'**Number:** {'Off' if not numbers else 'On'}\n'
        if letters:
            feat.add('letter')
            desc += f'**Letter:** {'Off' if not letters else 'On'}\n'
        if text:
            feat.add('text')
            desc += f'**Text:** {'Off' if not text else 'On'}\n'

        feat.add('saying') # Always enabled for Users

        if not feat.__sizeof__() > 0:
            raise RuntimeError('Set of selected features is 0 even though some feature was selected.')

        self.pref.set_user_autoreply_features(interaction.user.id, feat)

        desc = desc.removesuffix('\n')
        await self.client.user_feedback(
            interaction,
            title='User preferences updated',
            desc=desc,
        )
