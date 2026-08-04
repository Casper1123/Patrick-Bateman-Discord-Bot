from datetime import datetime, timezone
from abc import ABC, abstractmethod


class SimpleSayingEditorData:
    """
    Simplified record class for Saying Editor data.
    """
    def __init__(self, text: str) -> None:
        self.text = text

class SayingEditorData(SimpleSayingEditorData):
    """
    Record class for Saying Editor data
    """
    def __init__(self, text: str, author_id: int, modified_at: int,) -> None:
        super().__init__(text)

        # Moderation purposes
        self.author_id: int = author_id
        self.modified_at: datetime = datetime.fromtimestamp(modified_at, timezone.utc)

class SayingInterface(ABC):
    @abstractmethod
    def get_saying(self) -> str:
        """
        Gets a random saying.
        :return: Unprocessed PISS-compatible string.
        """
        raise NotImplementedError()

class GlobalAdminSayingInterface(SayingInterface):
    @abstractmethod
    def create_saying(self, text: str) -> None:
        """
        Creates PISS-compatible autoreply saying using given text.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_saying(self, index: int, text: str) -> SimpleSayingEditorData:
        """
        Edit a saying at a given index. Raises IndexError if index is out of range.
        :param index: Index of editing saying.
        :param text: PISS-compatible replacement text
        :returns: The old saying data before editing.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_saying(self, index: int) -> SayingEditorData:
        """
        Delete a saying at the given index. Raises IndexError if index is out of range.
        :param index: Index of saying to delete.
        :returns: The old saying data before removal.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_sayings(self) -> list[SimpleSayingEditorData]:
        """
        Get all sayings, ordered by creation date (index).
        """
        raise NotImplementedError()

    @abstractmethod
    def get_saying_by_index(self, index: int) -> SimpleSayingEditorData:
        """
        Get a saying at a given index. Raises IndexError if index is out of range.
        """
        raise NotImplementedError()