from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.pref import PreferencesInterface

"""
Table(s) and design:


"""

class PreferencesDatabase(AbstractSQLDatabase, PreferencesInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/pref.sql')

