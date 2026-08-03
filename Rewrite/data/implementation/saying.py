from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface, SayingEditorData

"""
Table(s) and design:


"""

class SayingDatabase(AbstractSQLDatabase, GlobalAdminSayingInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/saying.sql')