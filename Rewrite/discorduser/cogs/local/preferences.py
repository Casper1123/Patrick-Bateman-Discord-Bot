import discord
from discord import app_commands
from discord.ext import commands

from Rewrite.data.interfaces.data import DataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface, _supp_autr_features, GuildChannelPreferenceData


@app_commands.default_permissions(administrator=True)
class GuildPreferenceCog(commands.Cog):
    def __init__(self, client: commands.Bot, pref: PreferencesInterface) -> None:
        self.client = client
        self.pref = pref

    # Guild channel preference toggle
    @app_commands.command(name="guild_preferences", description="Toggle automatic features for this, or all, channels. Set to True to toggle.")
    @app_commands.describe(here="If false, edits general server-wide override instead.", numbers="Incremental number replies.", letters='Letter-only replies.', text='Text content replies.')
    async def guild_toggle_preference(self, interaction: discord.Interaction, here: bool, numbers: bool = False, letters: bool = False, text: bool = False, saying: bool = False):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not (numbers or letters or text or saying):
            await interaction.edit_original_response(content='Please select at least one option.')
            return

        guild_id: int = interaction.guild_id
        channel_id: int | None = interaction.channel_id if here else None
        desc: str = 'Preferences for ' + (f'<#{channel_id}>' if channel_id else '**Server-wide override**') + '\n'
        feat: set[_supp_autr_features] = set() # noqa because empty set
        pref: GuildChannelPreferenceData = self.pref.guild_channel_autoreplies_enabled(guild_id, channel_id)
        if numbers:
            feat.add('number')
            desc += f'**Number:** {not pref.number}\n'
        if letters:
            feat.add('letter')
            desc += f'**Letter:** {not pref.letter}\n'
        if text:
            feat.add('text')
            desc += f'**Text:** {not pref.text}\n'
        if saying:
            feat.add('saying')
            desc += f'**Saying:** {not pref.saying}\n'

        assert feat.__sizeof__() > 0, 'Set of selected features is 0 even though some feature was selected.'

        self.pref.toggle_autoreply_feature(guild_id, channel_id, feat)

        desc = desc.removesuffix('\n')
        await interaction.edit_original_response(embed=discord.Embed(
            title='Guild autoreply preferences updated',
            description=desc,
        ))
