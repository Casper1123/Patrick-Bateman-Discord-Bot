from abc import ABC, abstractproperty, abstractmethod, abstractstaticmethod

class FactEditorData:
    """
    Purely a record class to hold Fact data.
    """
    def __init__(self, guild_id: int, author_id: int, text: str, modified_at: int):
        """
        Represents the object data that should be returned for some subfunctions.
        :param guild_id:
        :param author_id:
        :param text:
        :param modified_at:
        """
        self.text: str = text
        self.guild_id: int = guild_id
        self.author_id: int = author_id
        self.modified_at: int = modified_at


class DataInterface(ABC):
    """
    Class responsible for the most minimal data access, primarily for regular effect data.
    As it is an Abstract Base Class, you are expected to inherit from this class.
    Each method will have descriptions listing the functionality required.
    """

    # region Facts
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
        :return: An unprocessed fact. Usually requires variables parsing.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_fact_count(self, guild_id: int | None) -> int:
        """
        Gets the number of facts from the domain.

        As it just gets the quantity, guild_id is optional to either get global count or local count.
        :param guild_id: If not None, gets the given guild's local fact count, otherwise gets global fact count.
        :return: Number of facts in given domain.
        """
        raise NotImplementedError()
    # endregion


class LocalAdminDataInterface(DataInterface):
    """
    An extra layer of power, stronger than `DataInterface`.
    Can do basic local-administrator operations, like adding local facts.
    """
    # region Facts
    @abstractmethod
    def create_fact(self, guild_id: int, user_id: int, fact: str) -> bool: # todo: better return information?
        """
        Creates a new Local fact under the given user id
        :param guild_id: Guild the new Local fact will belong to.
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Local fact. Ensure it compiles before being added.
        :return: Creation succes.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: str, editor_id: int, new_fact: str | None) -> bool: # todo: better return information?
        """
        Edits a fact, setting the new content to the old. If new_fact is empty or None, it is removed instead.
        :param guild_id: Guild of the belonging fact.
        :param previous_author_id: ID of the previous author of the fact.
        :param old_fact: Old fact string.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        :return: Edit success.
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
    # endregion

    # region authorized
    @abstractmethod
    def is_banned_user(self, user_id: int) -> bool:
        """
        :param user_id: User ID
        :return: User is banned.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_banned_guild(self, guild_id: int) -> bool:
        """
        :param guild_id: Guild ID
        :return: Guild is banned.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_super_server(self, guild_id: int) -> bool:
        """
        Returns guild Super Server status.
        :param guild_id: Guild ID for which to check.
        :return: Whether the Guild is a Super Server.
        """
        raise NotImplementedError()
    # endregion

    # region other
    @abstractmethod
    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        """
        Sets the local logging output channel for a given guild.
        Unique per guild.
        :param guild_id: The guild ID.
        :param channel_id: Channel ID to log to. If none, remove entry.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_log_channel(self, guild_id: int) -> int | None:
        """
        Gets the ID of  the logging channel for the given guild.
        Returns None if none found.
        :param guild_id: Guild for the logging action.
        :return: Channel ID if found, otherwise None
        """
        # todo: DEFINITELY WORK WITH CACHING HERE.
        raise NotImplementedError()
    # endregion


class GlobalAdminDataInterface(LocalAdminDataInterface):
    """
    The strongest layer of power, stronger than `LocalAdminDataInterface`.
    Can perform operations on the global data other than retrieving.
    """
    # region Facts
    @abstractmethod
    def create_global_fact(self,  user_id: int, fact: str) -> bool:  # todo: better return information?
        """
        Creates a new Global fact under the given user id
        :param user_id: The ID of the user adding the new Local fact.
        :param fact: The new Global fact. Ensure it compiles before being added.
        :return: Creation succes.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int,
                  new_fact: str | None) -> bool:  # todo: better return information?
        """
        Edits a fact, setting the new content to the old. If new_fact is empty or None, it is removed instead.
        :param previous_author_id: ID of the previous author of the fact.
        :param old_fact: Old fact string.
        :param editor_id: Id of the editor of the fact.
        :param new_fact: New fact string.
        :return: Edit success.
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
        Ordered on edit date.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        """
        Gets all local facts, indexed by guild ID.
        """
        raise NotImplementedError()
    # endregion

    @abstractmethod
    def get_super_server_ids(self) -> list[int]:
        """
        Gets the list of super server IDs.
        Primarily used for tree synchronization.
        """
        raise NotImplementedError()

    @abstractmethod
    def ban_user(self, user_id: int) -> None:
        """
        Bans the given user.
        :param user_id:
        """
        raise NotImplementedError()

    @abstractmethod
    def unban_user(self, user_id: int) -> None:
        """
        Unbans the given user.
        :param user_id:
        """
        raise NotImplementedError()

    @abstractmethod
    def ban_guild(self, guild_id: int) -> None:
        """
        Bans the given guild.
        :param guild_id:
        """
        raise NotImplementedError()

    @abstractmethod
    def unban_guild(self, guild_id: int) -> None:
        """
        Unbans the given guild.
        :param guild_id:
        """
        raise NotImplementedError()

