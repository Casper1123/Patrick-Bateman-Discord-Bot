from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.other import LocalAdminDataInterface

"""
Table(s) and design:

local_log_channels:
- guild_id int PK
- channel_id int

If logging disabled, no entry with guild_id
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

