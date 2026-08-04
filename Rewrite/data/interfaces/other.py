from abc import ABC, abstractmethod

class DataInterface(ABC):
    @abstractmethod
    def get_log_channel(self, guild_id: int) -> int | None:
        """
        Gets the ID of  the logging channel for the given guild.
        Returns None if none found.
        :param guild_id: Guild for the logging action.
        :return: Channel ID if found, otherwise None
        """
        raise NotImplementedError()

class LocalAdminDataInterface(DataInterface):
    @abstractmethod
    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        """
        Sets the local logging output channel for a given guild.
        Unique per guild.
        :param guild_id: The guild ID.
        :param channel_id: Channel ID to log to. If none, remove entry.
        """
        raise NotImplementedError()