from abc import ABC, abstractmethod

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

    # todo: how to index into?
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