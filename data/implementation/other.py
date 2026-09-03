from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.other import LocalAdminDataInterface

"""
Table(s) and design:


"""


class GeneralDatabase(CachedAbstractSQLDatabase, LocalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/other.sql')
