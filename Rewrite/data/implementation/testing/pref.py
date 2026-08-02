from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.pref import PreferencesInterface, UserPreferenceData, _supp_autr_features, \
    GuildChannelPreferenceData



class TestPreferencesDatabase(AbstractSQLDatabase, PreferencesInterface):
    def pause_all_in_channel(self, guild_id: int, channel_id: int | None) -> None:
        pass

    def is_paused_channel(self, guild_id: int, channel_id: int) -> bool:
        pass

    def toggle_autoreply_feature(self, guild_id: int, channel_id: int | None,
                                 features: set[_supp_autr_features]) -> None:
        pass

    def is_autoreply_enabled(self, guild_id: int, channel_id: int | None, feature: _supp_autr_features) -> bool:
        pass

    def guild_channel_autoreplies_enabled(self, guild_id: int, channel_id: int | None) -> GuildChannelPreferenceData:
        pass

    def toggle_user_autoreply_feature(self, user_id: int, features: set[_supp_autr_features]) -> None:
        pass

    def is_user_autoreply_enabled(self, user_id: int, feature: _supp_autr_features) -> bool:
        pass

    def user_autoreplies_enabled(self, user_id: int) -> UserPreferenceData:
        pass

    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/pref.sql')

