from typing import get_args

from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.pref import PreferencesInterface, UserPreferenceData, supported_autoreply_features, \
    GuildChannelPreferenceData

"""
Table(s) and design:
Pausing: Handled completely through cache.

CHANNEL:
- GuildID: ID of the corresponding channel's guild.
- ChannelID: ID of the corresponding channel. 0 if global/None id
- saying
- text
- letter
- number
PK: (GuildID, ChannelID)

USER:
- UserID: ID of the corresponding user
- saying
- text
- letter
- number
PK: UserID
"""

_all_features: set[supported_autoreply_features] = {i for i in get_args(supported_autoreply_features)}

class PreferencesDatabase(CachedAbstractSQLDatabase, PreferencesInterface):
    # region abstract
    def pause_all_in_channel(self, guild_id: int, channel_id: int | None, duration: int) -> None:
        try:
            self._cache.register(
                keys=('paused', str(guild_id), str(channel_id),),
                val=channel_id if channel_id else 0,
                timeout=duration,
            )
        except ValueError:
            self._cache.refresh(
                keys=('paused', str(guild_id), str(channel_id),),
                timeout=duration,
            )

    def is_paused_channel(self, guild_id: int, channel_id: int) -> bool:
        # Registered under str(None) is 'all channels' which overrides this, obviously.
        val = self._cache.get_cached(
            keys=('paused', str(guild_id), str(None),),
            out_type=int,
        )
        if val is not None:
            return True
        val = self._cache.get_cached(
            keys=('paused', str(guild_id), str(channel_id),),
            out_type=int,
        )
        return val is not None

    def toggle_autoreply_feature(self, guild_id: int, channel_id: int | None,
                                 features: set[supported_autoreply_features]) -> None:
        pass

    def is_autoreply_enabled(self, guild_id: int, channel_id: int | None,
                             feature: supported_autoreply_features) -> bool:
        pass

    def guild_channel_autoreplies_enabled(self, guild_id: int, channel_id: int | None) -> GuildChannelPreferenceData:
        pass

    def toggle_user_autoreply_feature(self, user_id: int, features: set[supported_autoreply_features]) -> None:
        pass

    def is_user_autoreply_enabled(self, user_id: int, feature: supported_autoreply_features) -> bool:
        pass

    def user_autoreplies_enabled(self, user_id: int) -> UserPreferenceData:
        pass
    # endregion

    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='pref',
            schema_version=1
        )
