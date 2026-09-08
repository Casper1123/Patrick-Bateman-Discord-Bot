from data.interfaces.moderation import GlobalAdminModerationInterface


class TestModerationDatabase(GlobalAdminModerationInterface):
    def toggle_guild_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        pass

    def toggle_user_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        pass

    def __init__(self, user_banned: bool, banned_guild: bool, super_guild: bool) -> None:
        self.user_banned = user_banned
        self.banned_guild = banned_guild
        self.super_guild = super_guild

    def is_banned_user(self, user_id: int) -> bool:
        return self.user_banned

    def is_banned_guild(self, guild_id: int) -> bool:
        return self.banned_guild

    def is_super_server(self, guild_id: int) -> bool:
        return self.super_guild
