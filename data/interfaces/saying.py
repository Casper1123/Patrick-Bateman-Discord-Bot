from abc import ABC, abstractmethod
from datetime import datetime, timezone

from data.interfaces.utilities import AbstractDTO


# todo: add Saying types just like Reply types? Maybe automatically react to things?
class SimpleSayingEditorData(AbstractDTO):
    """
    Simplified record class for Saying Editor data.
    """

    def __init__(self, text: str) -> None:
        self.text = text

    def as_json(self) -> dict[str, int | float | None | str | bool]:
        return {
            'text': self.text,
        }


class SayingEditorData(SimpleSayingEditorData):
    """
    Record class for Saying Editor data
    """

    def __init__(self, text: str, author_id: int, modified_at: int, ) -> None:
        super().__init__(text)

        # Moderation purposes
        self.author_id: int = author_id
        self.modified_at: datetime = datetime.fromtimestamp(modified_at, timezone.utc)

    def as_json(self) -> dict[str, int | float | None | str]:
        val = super().as_json()
        val['author_id'] = self.author_id
        val['modified_at'] = int(self.modified_at.timestamp())
        return val


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
    def create_saying(self, text: str, author_id: int) -> None:
        """
        Creates PISS-compatible autoreply saying using given text.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_saying(self, index: int, text: str, author_id: int) -> SimpleSayingEditorData:
        """
        Edit a saying at a given index.
        Raises IndexError if index is out of range.
        :param index: Index of editing saying.
        :param text: PISS-compatible replacement text
        :param author_id: ID of modifying author
        :returns: The old saying data before editing.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_saying(self, index: int) -> SayingEditorData:
        """
        Delete a saying at the given index.
        Raises IndexError if index is out of range.
        :param index: Index of saying to delete.
        :returns: The old saying data before removal.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_sayings(self) -> list[SayingEditorData]:
        """
        Get all sayings and their full data.
        """
        raise NotImplementedError()
