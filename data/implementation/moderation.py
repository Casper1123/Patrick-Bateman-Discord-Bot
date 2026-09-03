from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.moderation import GlobalAdminModerationInterface

"""
Table(s) and design:

BANNEDGUILDS:
- GuildID: int ID of banned guild

BANNEDUSERS:
- UserID: int ID of banned user

Inclusion implies ban.
PK trivial
"""


class ModerationDatabase(CachedAbstractSQLDatabase, GlobalAdminModerationInterface):
    def toggle_guild_ban(self, identifier: int) -> bool:
        pass

    def toggle_user_ban(self, identifier: int) -> bool:
        pass

    def is_banned_user(self, user_id: int) -> bool:
        pass

    def is_banned_guild(self, guild_id: int) -> bool:
        pass

    def is_super_server(self, guild_id: int) -> bool:
        pass

    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/mod.sql')
