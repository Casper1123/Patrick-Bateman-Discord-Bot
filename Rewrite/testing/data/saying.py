from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface, SimpleSayingEditorData


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

    def delete_saying(self, index: int) -> SimpleSayingEditorData:
        return SimpleSayingEditorData(text=f'Deleted saying at index {index}')

    def get_sayings(self) -> list[SimpleSayingEditorData]:
        return [
            SimpleSayingEditorData('PISS-compatible saying for {user}')
        ]

    def get_saying_by_index(self, index: int) -> SimpleSayingEditorData:
        return SimpleSayingEditorData('PISS-compatible saying for {user} at index ' + str(index))
    # endregion