from abc import ABC, abstractmethod
from typing import Literal

_supp_autr_features = Literal['saying', 'text', 'letter', 'number']

class UserPreferenceData:
    """
    Record for User Preference data.
    """
    def __init__(self, text: bool, letter: bool, number: bool):
        """
        Creates a Data Transfer Object containing data on each of the supported features for the given user id.
        """
        self.text = text
        self.letter = letter
        self.number = number

class GuildChannelPreferenceData:
    """
    Record for Guild Preference data.
    """
    def __init__(self, text: bool, letter: bool, number: bool, saying: bool):
        self.text = text
        self.letter = letter
        self.number = number
        self.saying = saying

class PreferencesInterface(ABC):
    @abstractmethod
    async def run_cache_manager(self):
        """
        Asynchronous function to manage the cache.
        Can be left empty in implementation, but is here to enforce caching compatibility.
        """
        raise NotImplementedError()

    # region Server - Channel Pause
    @abstractmethod
    def pause_all_in_channel(self, guild_id: int, channel_id: int | None) -> None:
        """
        Temporarily pauses all interactions in this channel, or disables it if already paused.
        :param guild_id:
        :param channel_id: Leave empty for entire guild.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_paused_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Is interaction in this channel temporarily paused?
        :param guild_id:
        :param channel_id:
        """
        raise NotImplementedError()

    # endregion

    # region Server - Autoreply Features
    @abstractmethod
    def toggle_autoreply_feature(self, guild_id: int, channel_id: int | None, features: set[_supp_autr_features]) -> None:
        """
        Flips the activity state on each of the passed features.
        :param guild_id:
        :param channel_id: Leave empty for 'all channels' option.
        :param features: Set of supported features. At least ONE needs to be selected.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_autoreply_enabled(self, guild_id: int, channel_id: int | None, feature: _supp_autr_features) -> bool:
        """
        Gets enabled state for guild channel's autoreply feature.
        :param guild_id:
        :param channel_id:
        :param feature: Given feature to check status for. todo: needs one for all features for command inputs?
        :return: Feature availability status.
        """
        raise NotImplementedError()

    @abstractmethod
    def user_autoreplies_enabled(self, user_id: int) -> UserPreferenceData:
        """
        Gets all user preferences. Use over `is_autoreply_enabled` if you intend to request more than one data point.
        :param user_id: User ID to get for.
        :return: UserPreferenceData for the given data.
        """
        raise NotImplementedError()

    @abstractmethod
    def guild_channel_autoreplies_enabled(self, guild_id: int, channel_id: int | None) -> GuildChannelPreferenceData:
        """
        Gets all guild preferences for the current channel. Use over `is_autoreply_enabled` if you intend to request more than one data point.
        :param guild_id: The guild ID to get for.
        :param channel_id: The channel ID to get for. NONE if all channels.
        :return: GuildChannelPreferenceData for the given data.
        """
        raise NotImplementedError()
    # endregion

    # region User - Autoreply Features
    @abstractmethod
    def toggle_user_autoreply_feature(self, user_id: int, features: set[_supp_autr_features]) -> None:
        """
        Flips the activity state on each of the passed features.
        :param user_id:
        :param features: Set of supported features. At least ONE needs to be selected.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_user_autoreply_enabled(self, user_id: int, feature: _supp_autr_features) -> bool:
        """
        Gets enabled state for user's autoreply feature.
        :param user_id
        :param feature: Given feature to check status for. todo: needs one for all features for command inputs?
        :return: Feature availability status.
        """
        raise NotImplementedError()
    # endregion