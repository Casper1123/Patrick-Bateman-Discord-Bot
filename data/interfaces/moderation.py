from abc import ABC, abstractmethod

class ModerationInterface(ABC):
    ...

class LocalAdminModerationInterface(ModerationInterface):
    @abstractmethod
    def is_banned_user(self, user_id: int) -> bool:
        """
        :param user_id: User ID
        :return: User is banned.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_banned_guild(self, guild_id: int) -> bool:
        """
        :param guild_id: Guild ID
        :return: Guild is banned.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_super_server(self, guild_id: int) -> bool:
        """
        Returns guild Super Server status.
        :param guild_id: Guild ID for which to check.
        :return: Whether the Guild is a Super Server.
        """
        raise NotImplementedError()

class GlobalAdminModerationInterface(LocalAdminModerationInterface):
    # region User Moderation
    @abstractmethod
    def ban_user(self, user_id: int) -> None:
        """
        Bans the given user.
        :param user_id:
        """
        raise NotImplementedError()

    @abstractmethod
    def unban_user(self, user_id: int) -> None:
        """
        Unbans the given user.
        :param user_id:
        """
        raise NotImplementedError()

    # endregion

    # region Server Moderation
    @abstractmethod
    def ban_guild(self, guild_id: int) -> None:
        """
        Bans the given guild.
        :param guild_id:
        """
        raise NotImplementedError()

    @abstractmethod
    def unban_guild(self, guild_id: int) -> None:
        """
        Unbans the given guild.
        :param guild_id:
        """
        raise NotImplementedError()
    # endregion