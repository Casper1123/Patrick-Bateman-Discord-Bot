from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.moderation import GlobalAdminModerationInterface

"""
Table(s) and design:

banned_users, banned_guilds:
- id
- reason
- since
- banned_by

"""


class ModerationDatabase(CachedAbstractSQLDatabase, GlobalAdminModerationInterface):
    def toggle_guild_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        pass

    def toggle_user_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        pass

    def __init__(self, path: str) -> None:
        super().__init__(
            db_path=path,
            schema_name='moderation',
            schema_version=1
        )

    def is_banned_user(self, user_id: int) -> bool:
        pass

    def is_banned_guild(self, guild_id: int) -> bool:
        pass

    def is_super_server(self, guild_id: int) -> bool:
        pass
