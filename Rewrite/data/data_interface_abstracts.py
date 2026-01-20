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
    # endregion


class GlobalAdminDataInterface(LocalAdminDataInterface):
    """
    The strongest layer of power, stronger than `LocalAdminDataInterface`.
    Can perform operations on the global data other than retrieving.
    """
    # region Facts
    # endregion