from abc import ABC, abstractmethod
from typing import Literal

_trigger_types = Literal['regex']

class AliasData:
    """
    Record class for alias data
    """
    def __init__(self, name: str, rate: int, uid: str):
        """
        Represents Data Transfer Object for Alias data.
        :param name: Alias name. Unique.
        :param rate: Rate of alias in [1..100]. Probability of alias triggering, if not overriden by trigger.
        :param uid: Unique ID of alias. Primarily for internal use.
        """
        self.name: str = name
        self.uid: str = uid
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
        :param rate: If present, overrides rate of alias in [1..100].
        :param uid: Unique ID of trigger. Primarily for internal use.
        """
        self.type: _trigger_types = trigger_type # todo: validate type correctness?
        self.data: str = data
        self.alias: AliasData = alias # todo: alias uid only?
        self.rate: int | None = rate
        self.id: str = uid

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
    def get_triggers(self, alias: str) -> list[TriggerData]:
        """
        Get all triggers of a given alias.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_aliases(self) -> list[AliasData]:
        """
        Get all aliases.
        """
        raise NotImplementedError()