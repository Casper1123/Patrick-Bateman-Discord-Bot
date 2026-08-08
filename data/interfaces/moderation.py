from abc import ABC, abstractmethod
from typing import Literal, TypeAlias

BanDomains: TypeAlias = Literal['user', 'guild']

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
    @abstractmethod
    def toggle_ban(self, ban_type: BanDomains, identifier: int) -> bool:
        """
        Toggles the ban on the given ID. Returns new state.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_banlist(self, ban_type: BanDomains) -> list[int]:
        """
        Gets the banned Identifiers for the given type.
        """
        raise NotImplementedError()
