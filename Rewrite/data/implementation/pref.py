from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.pref import PreferencesInterface, UserPreferenceData, _supp_autr_features, \
    GuildChannelPreferenceData


"""
Table(s) and design:


"""

class PreferencesDatabase(AbstractSQLDatabase, PreferencesInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/pref.sql')

