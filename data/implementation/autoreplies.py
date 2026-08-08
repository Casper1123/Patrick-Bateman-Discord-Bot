from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.autoreplies import GlobalTextAutoreplyInterface

"""
Table(s) and design:


"""

class AutoreplyDatabase(AbstractSQLDatabase, GlobalTextAutoreplyInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')