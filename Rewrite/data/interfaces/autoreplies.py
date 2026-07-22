from _ast import alias
from abc import ABC, abstractmethod
from typing import Literal

_trigger_types = Literal['regex']
_reply_types = Literal['text', 'reaction']

class AliasData:
    """
    Record class for alias data
    """
    def __init__(self, name: str, rate: int):
        """
        Represents Data Transfer Object for Alias data.
        :param name: Alias name. Unique.
        :param rate: Rate of alias in [1..256]. Probability of trigger in alias activating, if not overridden by trigger.
        :param uid: Unique ID of alias. Primarily for internal use.
        """
        self.name: str = name
        self.rate: int = rate

class TriggerData:
    """
    Record class for trigger data.
    """
    def __init__(self, trigger_type: _trigger_types, data: str, rate: int | None, uid: str, alias: AliasData,):
        """
        Represents Data Transfer Object for Trigger data.
        :param trigger_type: Type of trigger. Needs to be supported.
        :param data: Unprocess PISS-compatible string.
        :param alias: Alias of the trigger.
        :param rate: If present, overrides rate of alias in [1..256].
        :param uid: Unique ID of trigger. Primarily for internal use.
        """
        self.type: _trigger_types = trigger_type # todo: validate type correctness?
        self.data: str = data
        self.alias: AliasData = alias # todo: alias name only?
        self.rate: int | None = rate
        self.id: str = uid

class ReplyData:
    """
    Record for reply data.
    """
    def __init__(self, reply_type: _reply_types, data: str, weight: int, uid: str, alias: AliasData,):
        self.type: _reply_types = reply_type
        self.data: str = data
        self.alias: AliasData = alias # todo: alias name only?
        self.weight: int = weight
        self.id = uid

class TextAutorepliesInterface(ABC):
    """
    Abstract class for autoreplies interface.
    """

    @abstractmethod
    def get_reply(self, alias: str) -> ReplyData | None:
        """
        Get a random reply based on the given alias and the corresponding reply pool's weights.
        :param alias: Alias of the reply to get.
        :return: Unprocessed PISS-compatible string or NONE if no replies exist for this Alias.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_triggers_by_alias(self) -> dict[AliasData, list[TriggerData]]:
        """
        Gets all triggers bundled by Aliases.
        :return: Aliases indexed by alias name
        """
        raise NotImplementedError()

class GlobalTextAutorepliesInterface(TextAutorepliesInterface):
    """
    Extension of the standard authorization interface, which includes methods to modify the autoreply pool.
    """
    # region alias
    @abstractmethod
    def create_alias(self, name: str, rate: int):
        """
        Creates an alias with the given name. Raises ValueError if already exists.
        :param name: New alias name.
        :param rate: The default activation rate of the new alias in [1..256]
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None):
        """
        Rename given alias name to new name or change it's rate.
        Raises ValueError if either old_name does not exist, or new_name is already taken.
        :param old_name: Old alias name.
        :param new_name: New alias name.
        :param rate: The default activation rate of the alias in [1..256]
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_alias(self, name: str):
        """
        Deletes given Alias. Raises ValueError if it did not exist.
        :param name: Alias name to remove.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_aliases(self) -> list[AliasData]:
        """
        Gets all aliases with their activation rates.
        """
        raise NotImplementedError()

    @abstractmethod
    def exists_alias(self, name: str) -> bool:
        """
        Alias with given name exists or not.
        """
        raise NotImplementedError()

    # endregion

    # region trigger
    @abstractmethod
    def add_trigger(self, alias: str, trigger_type: _trigger_types, data: str, rate: int | None):
        """
        Creates a new Trigger for the given Alias.
        :param alias: Name of the Alias. Raises ValueError if given Alias does not exist.
        :param trigger_type: Type of the Trigger
        :param data: Trigger Data
        :param rate: Optional Trigger rate in [1..256]
        """
        raise NotImplementedError()
    # endregion

    # region reply
    @abstractmethod
    def add_reply(self, alias: str, reply_type: _reply_types, data, weight):
        """
        Creates a new Reply of the given type, with the given weight, for the given Alias.
        :param alias: Name of the Alias. Raises ValueError if given Alias does not exist.
        :param reply_type: Type of the Reply. Only supported times may be taken in.
        :param data: Raw reply data in string form. Input type depends on Reply type.
        :param weight: Relative reply weight.
        """
        raise NotImplementedError()
    # endregion