from datetime import datetime, timezone
from abc import ABC, abstractmethod


class SayingEditorData:
    """
    Record class for Saying Editor data
    """
    def __init__(self, text: str, author_id: int, modified_at: int,) -> None:
        self.text: str = text

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
    def edit_saying(self, index: int, text: str) -> None:
        """
        Edit a saying at a given index. Raises ValueError if it did not exist.
        :param index: Index of editing saying.
        :param text: PISS-compatible replacement text
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_saying(self, index: int):
        """
        Delete a saying at the given index. Raises ValueError if it did not exist.
        :param index: Index of saying to delete.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_sayings(self) -> list[SayingEditorData]:
        """
        Get all sayings, ordered by creation date (index).
        """
        raise NotImplementedError()

    def get_saying_by_index(self, index: int) -> SayingEditorData:
        """
        Get a saying at a given index. Throws IndexError if out of bounds.
        """
        raise NotImplementedError()