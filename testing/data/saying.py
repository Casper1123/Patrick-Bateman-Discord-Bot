from data.interfaces.saying import GlobalAdminSayingInterface, SimpleSayingEditorData, SayingEditorData


class TestSayingDatabase(GlobalAdminSayingInterface):
    def __init__(self) -> None:
        ...

    # region Regular
    def get_saying(self) -> str:
        return 'PISS-compatible saying for {user}'

    # endregion

    # region Global
    def create_saying(self, text: str) -> None:
        pass

    def edit_saying(self, index: int, text: str) -> SimpleSayingEditorData:
        return SimpleSayingEditorData(text=f'Edited saying at index {index}: {text}')

    def delete_saying(self, index: int) -> SayingEditorData:
        return SayingEditorData(text=f'Deleted saying at index {index}', author_id=0, modified_at=0)

    def get_sayings(self) -> list[SayingEditorData]:
        return [
            SayingEditorData('PISS-compatible saying for {user}', author_id=0, modified_at=0),
        ]

    def get_saying_by_index(self, index: int) -> SimpleSayingEditorData:
        return SimpleSayingEditorData('PISS-compatible saying for {user} at index ' + str(index))
    # endregion
