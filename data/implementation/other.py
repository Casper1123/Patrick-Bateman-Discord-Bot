from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.other import LocalAdminDataInterface

"""
Table(s) and design:

LOCALLOG:
- GuildID: int
- ChannelID: int
PK: GuildID

Makeshift GID -> CID mapping.
If logging disabled, is not present in GuildID
"""


class GeneralDatabase(CachedAbstractSQLDatabase, LocalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='other',
            schema_version=1
        )

    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        pass

    def get_log_channel(self, guild_id: int) -> int | None:
        pass

