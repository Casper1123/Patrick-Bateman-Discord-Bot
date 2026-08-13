import re

from discord import Interaction, TextChannel
from discord.app_commands import Transformer, Choice

_NROF_AUTOCOMPLETES: int = 10 # Max 25, gives up TO this number.
_SUPP_CHANNELS: list[type] = [TextChannel]

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

    async def autocomplete(self, interaction: Interaction, value: str | float | int,) -> list[Choice[str]]:
        if interaction.guild is None:
            return []
        if not isinstance(value, str):
            try:
                value = str(value)
            except ValueError:
                value = ''
        value = value.lower()

        # noinspection unresolved-references
        # guild.channels could be none, but handled above.
        channels = [
            channel
            for channel in interaction.guild.channels
            if value in channel.name.lower() and type(channel) in _SUPP_CHANNELS
        ]

        # noinspection unresolved-references
        # category name
        return [
            Choice[str](
                name=f"#{channel.name}" + (f' ({channel.category.name})' if channel.category else ''),
                value=str(channel.id),
            )
            for channel in channels[:_NROF_AUTOCOMPLETES]
        ]