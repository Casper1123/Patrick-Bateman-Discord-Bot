"""

On fact create
On fact edit

"""

from __future__ import annotations

import discord
from discord.ext import commands

from Rewrite.discorduser import BotClient


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

