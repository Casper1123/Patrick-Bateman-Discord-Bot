from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface


class TestModerationDatabase(GlobalAdminModerationInterface):
    def __init__(self) -> None:
        ...

    # region Local
    def is_banned_user(self, user_id: int) -> bool:
        pass

    def is_banned_guild(self, guild_id: int) -> bool:
        pass

    def is_super_server(self, guild_id: int) -> bool:
        pass
    # endregion

    # region Global
    def ban_user(self, user_id: int) -> None:
        pass

    def unban_user(self, user_id: int) -> None:
        pass

    def ban_guild(self, guild_id: int) -> None:
        pass

    def unban_guild(self, guild_id: int) -> None:
        pass
    # endregion