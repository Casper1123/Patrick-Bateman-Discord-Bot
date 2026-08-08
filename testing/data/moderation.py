from data.interfaces.moderation import GlobalAdminModerationInterface


class TestModerationDatabase(GlobalAdminModerationInterface):
    def __init__(self, user_banned: bool, banned_guild: bool, super_guild: bool) -> None:
        self.user_banned = user_banned
        self.banned_guild = banned_guild
        self.super_guild = super_guild

    # region Local
    def is_banned_user(self, user_id: int) -> bool:
        return self.user_banned

    def is_banned_guild(self, guild_id: int) -> bool:
        return self.banned_guild

    def is_super_server(self, guild_id: int) -> bool:
        return self.super_guild

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
