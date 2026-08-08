import re

from discord import Interaction
from discord.app_commands import Transformer, Choice

_NROF_AUTOCOMPLETES: int = 10 # Max 25, gives up TO this number.

_CHANNEL_MENTION_RE = re.compile(r"^<#(?P<id>\d{18,20})>$")
_CHANNEL_ID_RE = re.compile(r"^(?P<id>\d{18,20})$")


class ChannelIDTransformer(Transformer):
    """
    Accepts either a channel mention (<#123...>) or a raw channel ID
    and transforms it into an integer channel ID.
    """
    async def transform(self, interaction: Interaction, value: str) -> int:
        match = _CHANNEL_MENTION_RE.fullmatch(value)
        if match:
            return int(match.group("id"))

        match = _CHANNEL_ID_RE.fullmatch(value)
        if match:
            return int(match.group("id"))

        raise ValueError("Expected a channel mention or a valid channel ID.")

    async def autocomplete(self, interaction: Interaction, value: str,) -> list[Choice[str]]:
        if interaction.guild is None:
            return []

        value = value.lower()

        channels = [
            channel
            for channel in interaction.guild.channels
            if value in channel.name.lower()
        ]

        return [
            Choice(
                name=f"#{channel.name}" + ('' if not channel.category else f' ({channel.category.name})'),
                value=str(channel.id),
            )
            for channel in channels[:_NROF_AUTOCOMPLETES]
        ]