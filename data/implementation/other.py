from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.other import LocalAdminDataInterface

"""
Table(s) and design:


"""


class GeneralDatabase(AbstractSQLDatabase, LocalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/other.sql')
