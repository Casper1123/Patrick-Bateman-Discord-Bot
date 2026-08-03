from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.other import GlobalAdminDataInterface


"""
Table(s) and design:


"""

class GeneralDatabase(AbstractSQLDatabase, GlobalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/other.sql')