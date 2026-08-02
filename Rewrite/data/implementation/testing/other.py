from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.other import GlobalAdminDataInterface


class TestGeneralDatabase(AbstractSQLDatabase, GlobalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/other.sql')

    def get_log_channel(self, guild_id: int) -> int | None:
        pass

    def get_super_server_ids(self) -> list[int]:
        pass

    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        pass