from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.other import LocalAdminDataInterface


"""
Table(s) and design:


"""

class GeneralDatabase(AbstractSQLDatabase, LocalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/other.sql')