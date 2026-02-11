from discord import Interaction, TextChannel, Guild

from Rewrite.data.data_interface_abstracts import FactEditorData, LocalAdminDataInterface
from Rewrite.discorduser import BotClient


class LocalLogger:
    def __init__(self, client: BotClient, db: LocalAdminDataInterface):
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

    async def fact_create(self, interaction: Interaction, text: str) -> None:
        raise NotImplementedError()

    async def fact_edit(self, interaction: Interaction, old: FactEditorData, index: int, text: str) -> None:
        raise NotImplementedError()