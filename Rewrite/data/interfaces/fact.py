from abc import ABC, abstractmethod
from datetime import datetime, timezone


class FactEditorData:
    """
    Purely a record class to hold Fact data.
    """
    def __init__(self, text: str, guild_id: int | None, created_at: int, author_id: int, modified_at: int):
        """
        Represents the object data that should be returned for some subfunctions.
        :param guild_id: Only None when Global fact
        :param author_id:
        :param text:
        :param modified_at:
        """
        self.text: str = text
        self.guild_id: int | None = guild_id
        self.created_at: datetime = datetime.fromtimestamp(created_at, timezone.utc)

        # Moderation purposes
        self.author_id: int = author_id
        self.modified_at: datetime = datetime.fromtimestamp(modified_at, timezone.utc)

class FactInterface(ABC):
    """
    Class responsible for the most minimal data access, primarily for regular effect data.
    As it is an Abstract Base Class, you are expected to inherit from this class.
    Each method will have descriptions listing the functionality required.
    """
    @abstractmethod
    def get_fact(self, guild_id: int | None, index: int | None)  -> str:
        """
        Retrieves a fact from the database.

        If passed an int for the index, fetches at that index's fact.
        If the index is out of range, throws an IndexError.

        If passed guild_id as None, retrieves only from the global fact pool.
        If passed a known guild_id, appends local fact pool to the index range and fact pool.
        :param guild_id: Guild ID for local facts. Can be None to use only global.
        :param index: If not None, will try getting the fact at the given index. Otherwise picks randomly.
        :return: Unprocessed PISS-compatible string.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_fact_count(self, guild_id: int | None) -> int:
        """
        Gets the number of facts for the given guild.

        As it just gets the quantity, guild_id is optional to either get global count or local count.
        :param guild_id: If not None, gets the given guild's local fact count, otherwise gets global fact count.
        :return: Number of facts for the given guild.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_killswitch(self) -> bool:
        """
        Are local-fact services temporarily disabled?
        """
        raise NotImplementedError()


class LocalAdminFactInterface(FactInterface):
    """
    An extra layer of power, stronger than `DataInterface`.
    Can do basic local-administrator operations, like adding local facts.
    """
    @abstractmethod
    def create_fact(self, guild_id: int, user_id: int, fact: str) -> None:
        """
        Creates a new Local fact under the given user id
        :param guild_id: Guild the new Local fact will belong to.
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Local fact. Ensure it compiles before being added.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_fact(self, guild_id: int, index: int, new_fact: str, editor_id: int) -> FactEditorData:
        """
        Edits a fact, setting the old content to the new.
        Raises IndexError if index is out of range.

        :param guild_id: Guild of the belonging fact.
        :param index: index of the fact to be edited.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        :returns: The old fact, before modification.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_fact(self, guild_id: int, index: int) -> FactEditorData:
        """
        Deletes the local fact at the given index.
        Raises IndexError if index is out of range.

        :param guild_id: Guild of the belonging fact.
        :param index: Index to delete.
        :return: The old fact.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        """
        Gets all local facts for guild.
        Ordered on edit date.
        """
        raise NotImplementedError()


class GlobalAdminFactInterface(LocalAdminFactInterface):
    """
    The strongest layer of power, stronger than `LocalAdminDataInterface`.
    Can perform operations on the global data other than retrieving.
    """
    @abstractmethod
    def toggle_local_fact_killswitch(self) -> bool:
        """
        Toggle the local-fact service killswitch.
        :return: Updated state
        """
        raise NotImplementedError()

    @abstractmethod
    def create_global_fact(self, user_id: int, fact: str) -> None:
        """
        Creates a new Global fact under the given user id
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Global fact. Ensure it compiles before being added.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_global_fact(self, index: int, editor_id: int,
                  new_fact: str) -> FactEditorData:
        """
        Edits a fact, setting the new content to the old.
        Raises IndexError if index is out of range.

        :param index: Index of the fact to be edited.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        :returns: The old fact, before modification.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_global_fact(self, index: int) -> FactEditorData:
        """
        Deletes the global fact at the given index.
        Raises IndexError if index is out of range.

        :param index: Index of the fact.
        :returns: The old fact.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_global_facts(self) -> list[FactEditorData]:
        """
        Gets all global facts.
        Ordered on creation date.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        """
        Gets all local facts, indexed by guild ID.
        """
        raise NotImplementedError()