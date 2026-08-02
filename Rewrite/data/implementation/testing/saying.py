from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface, SayingEditorData


class TestSayingDatabase(AbstractSQLDatabase, GlobalAdminSayingInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/saying.sql')

    # region Regular
    def get_saying(self) -> str:
        pass
    # endregion

    # region Global
    def create_saying(self, text: str) -> None:
        pass

    def edit_saying(self, index: int, text: str) -> None:
        pass

    def delete_saying(self, index: int):
        pass

    def get_sayings(self) -> list[SayingEditorData]:
        pass
    # endregion