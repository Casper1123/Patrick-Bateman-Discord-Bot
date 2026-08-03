from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.pref import PreferencesInterface, UserPreferenceData, _supp_autr_features, \
    GuildChannelPreferenceData



class TestPreferencesDatabase(PreferencesInterface):
    def pause_all_in_channel(self, guild_id: int, channel_id: int | None) -> None:
        pass

    def is_paused_channel(self, guild_id: int, channel_id: int) -> bool:
        return False

    def toggle_autoreply_feature(self, guild_id: int, channel_id: int | None,
                                 features: set[_supp_autr_features]) -> None:
        pass

    def is_autoreply_enabled(self, guild_id: int, channel_id: int | None, feature: _supp_autr_features) -> bool:
        if feature == 'text':
            return self.text
        elif feature == 'letter':
            return self.letter
        elif feature == 'number':
            return self.number

        return True

    def guild_channel_autoreplies_enabled(self, guild_id: int, channel_id: int | None) -> GuildChannelPreferenceData:
        return GuildChannelPreferenceData(
            text=self.text, letter=self.letter, number=self.number, saying=True # saying configurable but leaving True to make testing easier.
        )

    def toggle_user_autoreply_feature(self, user_id: int, features: set[_supp_autr_features]) -> None:
        pass

    def is_user_autoreply_enabled(self, user_id: int, feature: _supp_autr_features) -> bool:
        if feature == 'text':
            return self.text
        elif feature == 'letter':
            return self.letter
        elif feature == 'number':
            return self.number

        return True

    def user_autoreplies_enabled(self, user_id: int) -> UserPreferenceData:
        return UserPreferenceData(
            text=self.text, letter=self.letter, number=self.number, saying=True
        )

    def __init__(self, text: bool, letter: bool, number: bool):
        self.text = text
        self.letter = letter
        self.number = number
