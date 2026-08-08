from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.saying import GlobalAdminSayingInterface

"""
Table(s) and design:


"""


class SayingDatabase(AbstractSQLDatabase, GlobalAdminSayingInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/saying.sql')
