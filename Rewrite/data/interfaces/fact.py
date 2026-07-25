from abc import ABC, abstractmethod
from datetime import datetime, timezone


class FactEditorData:
    """
    Purely a record class to hold Fact data.
    """
    def __init__(self, guild_id: int | None, author_id: int, text: str, modified_at: int):
        """
        Represents the object data that should be returned for some subfunctions.
        :param guild_id: Only None when Global fact
        :param author_id:
        :param text:
        :param modified_at:
        """
        self.text: str = text
        self.guild_id: int | None = guild_id
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
        :param index: If not None, will try getting the fact at the given index. Throws IndexError when out of bounds.
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
    def create_fact(self, guild_id: int, user_id: int, fact: str):
        """
        Creates a new Local fact under the given user id
        :param guild_id: Guild the new Local fact will belong to.
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Local fact. Ensure it compiles before being added.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: str, editor_id: int, new_fact: str | None): # todo: better return information?
        """
        Edits a fact, setting the new content to the old. If new_fact is empty or None, it is removed instead.
        :param guild_id: Guild of the belonging fact.
        :param previous_author_id: ID of the previous author of the fact.
        :param old_fact: Old fact string.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_local_fact(self, guild_id: int, index: int) -> FactEditorData:
        """
        Get a local fact for the purpose of editing. Needs to be directly indexed.
        Raises IndexError if index is out of range.
        :param guild_id: Guild to look in.
        :param index: Index of the fact.
        :return: FactEditorData object containing author and edit data of the fact, as well as fact content.
        """
        raise NotImplementedError()

    @abstractmethod # todo: add filter parameters?
    def get_local_facts(self, guild_id:int) -> list[FactEditorData]:
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
    def create_global_fact(self,  user_id: int, fact: str):
        """
        Creates a new Global fact under the given user id
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Global fact. Ensure it compiles before being added.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int,
                  new_fact: str | None):
        """
        Edits a fact, setting the new content to the old. If new_fact is empty or None, it is removed instead.
        :param previous_author_id: ID of the previous author of the fact.
        :param old_fact: Old fact string.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_global_fact(self, index: int) -> FactEditorData:
        """
        Get a local fact for the purpose of editing. Needs to be directly indexed.
        Raises IndexError if index is out of range.
        :param index: Index of the fact.
        :return: FactEditorData object containing author and edit data of the fact, as well as fact content.
        """
        raise NotImplementedError()

    @abstractmethod  # todo: add filter parameters?
    def get_global_facts(self) -> list[FactEditorData]:
        """
        Gets all global facts.
        Ordered on edit date. todo: why the fuck did I make this up?
        """
        raise NotImplementedError()

    @abstractmethod
    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        """
        Gets all local facts, indexed by guild ID.
        """
        raise NotImplementedError()