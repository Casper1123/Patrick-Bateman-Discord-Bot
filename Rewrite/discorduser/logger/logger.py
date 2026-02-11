from __future__ import annotations

from enum import Enum

import discord
from discord import Guild, Interaction, Embed
from discord.ext import commands

from Rewrite.data.data_interface_abstracts import FactEditorData


# from Rewrite.discorduser import BotClient # fixme: circular import

class LogTypes(Enum):
    GENERAL = 0
    ERROR = 10

    FACT_CREATE = 1
    FACT_UPDATE = 2
    FACT_DELETE = 3

    GLOBAL_FACT_CREATE = -1
    GLOBAL_FACT_UPDATE = -2
    GLOBAL_FACT_DELETE = -3

class LoggerConfiguration:
    def __init__(self):
        ...

    @staticmethod
    def from_source() -> LoggerConfiguration:
        raise NotImplementedError()


class Logger:
    def __init__(self, client: BotClient, config: LoggerConfiguration) -> None:
        self.client = client
        self.config = config

    async def general_event(self, embed: Embed):
        """
        TODO: REQUIRES HEAVY EXTRA DESIGN
        """
        ...

    async def error(self, error: Exception, interaction: Interaction):
        ...

    # region local
    async def fact_create(self, interaction: Interaction, text: str):
        ...
    async def fact_edit(self, interaction: Interaction, text: str | None, old: FactEditorData):
        ...
    # endregion
    # region global fact
    async def global_fact_create(self, interaction: Interaction, text: str):
        ...
    async def global_fact_edit(self, interaction: Interaction, text: str | None, old: FactEditorData):
        ...
    # endregion
    # region admin

    # endregion