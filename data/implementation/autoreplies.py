from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.autoreplies import GlobalTextAutoreplyInterface

"""
Table(s) and design:


"""


class AutoreplyDatabase(CachedAbstractSQLDatabase, GlobalTextAutoreplyInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')
