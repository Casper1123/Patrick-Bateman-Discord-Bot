from abc import ABC, abstractmethod, abstractproperty, abstractmethod, abstractstaticmethod

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


class GlobalAdminDataInterface(LocalAdminDataInterface):
    """
    The strongest layer of power, stronger than `LocalAdminDataInterface`.
    Can perform operations on the global data other than retrieving.
    """
    # region Facts
    # endregion