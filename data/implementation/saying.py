from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.saying import GlobalAdminSayingInterface, SayingEditorData, SimpleSayingEditorData

"""
Table(s) and design:

SAYING:
- text: str; PISS-compatible data.
- author: int; ID of author
- creation: int; timestamp of creation
- modification: int; timestamp of modification
PK: Creation
"""


class SayingDatabase(CachedAbstractSQLDatabase, GlobalAdminSayingInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/saying.sql')


    def create_saying(self, text: str) -> None:
        pass

    def edit_saying(self, index: int, text: str) -> SimpleSayingEditorData:
        pass

    def delete_saying(self, index: int) -> SayingEditorData:
        pass

    def get_sayings(self) -> list[SayingEditorData]:
        pass

    def get_saying(self) -> str:
        pass

