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
    def get_reply(self, alias: str) -> str:
        """
        Get a random reply based on the given alias and the corresponding reply pool's weights.
        Throws a ValueError if not possible.
        :param alias: Alias of the reply to get.
        :return: Unprocessed PISS-compatible string.
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
    @abstractmethod
    def add_trigger(self, alias: str, trigger_type: _trigger_types, data: str, rate: int | None):
        """
        Creates a new Trigger for the given Alias.
        :param alias: Name of the Alias
        :param trigger_type: Type of the Trigger
        :param data: Trigger Data
        :param rate: Optional Trigger rate in [1..256]
        """
        raise NotImplementedError()