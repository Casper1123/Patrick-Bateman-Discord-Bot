from typing import Literal

from discord import Interaction, TextChannel, Guild, Embed

from Rewrite.data.interfaces.fact import FactEditorData, LocalAdminFactInterface
from Rewrite.data.interfaces.other import LocalAdminDataInterface
from Rewrite.discorduser.user.abstract import BotClient

console_loggable = Literal['fact_create', 'fact_edit', 'fact_delete', 'set_log_channel']

class LocalLoggerConfig:
    def __init__(self):
        self.output_to_console: dict[console_loggable, bool] = ...
        self.actively_logging: dict[console_loggable, bool] = ...

class LocalLogger:
    def __init__(self, client: BotClient, config: LocalLoggerConfig, db: LocalAdminDataInterface):
        self.config = config
        self.db = db
        self.client = client

    def _get_log_channel(self, guild: Guild) -> TextChannel | None:
        res = self.db.get_log_channel(guild.id)
        if res is None:
            return None
        channel = guild.get_channel(res)
        if channel is None:
            self.db.set_log_output(guild.id, None) # Do this to prevent the call of get_channel getting used for no reason.
            return None
        return channel

    # region log out
    def _console_log(self, out: str, act: console_loggable) -> None:
        if self.config.output_to_console[act]:
            print(out)

    # todo: buffer messages for x seconds and then send one thing with multiple embeds in one go to prevent ratelimiting?
    async def _channel_log(self, channel: TextChannel, embed: Embed, act: console_loggable) -> None:
        if self.config.actively_logging[act]:
            await channel.send(embed=embed)
    # endregion

    async def fact_create(self, interaction: Interaction, text: str) -> None:
        raise NotImplementedError()

    async def fact_edit(self, interaction: Interaction, old: FactEditorData, text: str) -> None:
        raise NotImplementedError()

    async def fact_remove(self, interaction: Interaction, old: FactEditorData) -> None:
        raise NotImplementedError()

    async def set_log_channel(self, interaction: Interaction, channel: TextChannel) -> None:
        raise NotImplementedError()