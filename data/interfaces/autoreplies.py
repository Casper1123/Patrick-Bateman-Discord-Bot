from abc import ABC, abstractmethod
from typing import Literal, TypeAlias

from data.interfaces.utilities import AbstractDTO

trigger_types: TypeAlias = Literal['regex']
reply_types: TypeAlias = Literal['text', 'reaction']


class SimpleAliasData(AbstractDTO):
    """
    Simplified Record class for alias data
    """

    def as_json(self) -> dict[str, int | float | None | str | bool | dict | list]:
        return {
            'name': self.name,
            'rate': self.rate,
        }

    def __init__(self, name: str, rate: int):
        """
        Represents Data Transfer Object for Alias data.
        :param name: Alias name. Unique.
        :param rate: Rate of alias in [1..256]. Probability of trigger in alias activating, if not overridden by trigger.
        """
        self.name: str = name
        self.rate: int = rate

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return other == self.name
        if not isinstance(other, SimpleAliasData):
            return False
        return self.name == other.name


class AliasData(SimpleAliasData):
    """
    Record class for alias data
    """

    def __init__(self, name: str, rate: int, editor_id: int, modified_at: int):
        """
        Represents expanded Data Transfer Object for Alias data.
        :param name: Alias name. Unique.
        :param rate: Rate of alias in [1..256]. Probability of trigger in alias activating, if not overridden by trigger.
        :param editor_id: ID of last editor of Alias.
        :param modified_at: POSIX (rounded to int) timestamp of last modification of Alias.
        """
        super().__init__(name, rate)

        # Moderation purposes
        self.editor_id: int = editor_id
        self.modified_at: float = modified_at

    def as_json(self) -> dict[str, int | float | None | str | bool | dict | list]:
        val = super().as_json()
        val['editor_id'] = self.editor_id
        val['modified_at'] = self.modified_at
        return val


class SimpleTriggerData(AbstractDTO):
    def as_json(self) -> dict[str, int | float | None | str | bool | dict | list]:
        val = {
            'type': self.type,
            'data': self.data,
        }
        if self.rate is not None:
            val['rate'] = self.rate
        return val

    def __init__(self, trigger_type: trigger_types, data: str, rate: int | None):
        """
        Represents Data Transfer Object for Trigger data.
        :param trigger_type: Type of trigger. Needs to be supported.
        :param data: Unprocess PISS-compatible string.
        :param rate: If present, overrides rate of alias in [1..256].
        """
        self.type: trigger_types = trigger_type
        self.data: str = data
        self.rate: int | None = rate


class TriggerData(SimpleTriggerData):
    """
    Record class for trigger data.
    """

    def __init__(self, trigger_type: trigger_types, data: str, rate: int | None, alias: AliasData, editor_id: int,
                 modified_at: int):
        """
        Represents Data Transfer Object for Trigger data.
        :param trigger_type: Type of trigger. Needs to be supported.
        :param data: Unprocess PISS-compatible string.
        :param rate: If present, overrides rate of alias in [1..256].
        :param alias: Alias of the trigger.
        :param editor_id: ID of last editor of Trigger.
        :param modified_at: POSIX (rounded to int) timestamp of last modification of Trigger.
        """
        super().__init__(trigger_type, data, rate)
        self.alias: AliasData = alias

        # Moderation purposes
        self.editor_id: int = editor_id
        self.modified_at: int = modified_at

    def as_json(self, include_alias: bool = False) -> dict[str, int | float | None | str | bool | dict | list]:
        val = super().as_json()
        val['editor_id'] = self.editor_id
        val['modified_at'] = self.modified_at
        if include_alias:
            val['alias'] = self.alias.as_json()
        return val


class SimpleReplyData(AbstractDTO):
    """
    Simple record for reply data. Really only used for direct usage of data.
    """

    def as_json(self) -> dict[str, int | float | None | str | bool | dict | list]:
        return {
            'type': self.type,
            'data': self.data,
            'weight': self.weight,
        }

    def __init__(self, reply_type: reply_types, data: str, weight: int):
        self.type = reply_type
        self.data: str = data
        self.weight: int = weight


class ReplyData(SimpleReplyData):
    """
    Record for reply data.
    """

    def __init__(self, reply_type: reply_types, data: str, weight: int, alias: AliasData, editor_id: int,
                 modified_at: int):
        """
        :param data: For type `text`, PISS-compatible string. For type `reaction`, unicode characters seperated by `;`
        :param alias: Alias of the trigger.
        :param editor_id: ID of last editor of Reply.
        :param modified_at: POSIX (rounded to int) timestamp of last modification of Reply.
        """
        super().__init__(reply_type, data, weight)
        self.alias: AliasData = alias

        # Moderation purposes
        self.editor_id: int = editor_id
        self.modified_at: int = modified_at

    def as_json(self, include_alias: bool = False) -> dict[str, int | float | None | str | bool | dict | list]:
        val = super().as_json()
        val['editor_id'] = self.editor_id
        val['modified_at'] = self.modified_at
        if include_alias:
            val['alias'] = self.alias.as_json()
        return val


class TextAutoreplyInterface(ABC):
    """
    Abstract class for autoreply interface.
    """

    @abstractmethod
    def get_reply(self, alias: str) -> SimpleReplyData | None:
        """
        Get a random reply based on the given alias and the corresponding reply pool's weights.
        :param alias: Alias of the reply to get. Raises ValueError if not found.
        :return: Unprocessed raw Reply data or NONE if no replies exist for this Alias.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_triggers_by_alias(self) -> dict[SimpleAliasData, list[SimpleTriggerData]]:
        """
        Gets all triggers bundled by Aliases.
        :return: Triggers indexed by alias name
        """
        raise NotImplementedError()

    @abstractmethod
    def get_triggers_for_alias(self, alias: str) -> list[SimpleTriggerData]:
        """
        Gets all triggers for the given Alias only.
        :param alias: Alias to filter for, raises IndexError if not found.
        """
        raise NotImplementedError()


class GlobalTextAutoreplyInterface(TextAutoreplyInterface):
    """
    Extension of the standard authorization interface, which includes methods to modify the autoreply pool.
    """

    # region alias
    @abstractmethod
    def create_alias(self, name: str, rate: int) -> None:
        """
        Creates an alias with the given name. Raises ValueError if already exists.
        :param name: New alias name.
        :param rate: The default activation rate of the new alias in [1..256]
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None = None) -> None:
        """
        Rename given alias name to new name or change it's rate.
        Raises ValueError if either old_name does not exist, or new_name is already taken.
        :param old_name: Old alias name.
        :param new_name: New alias name.
        :param rate: The default activation rate of the alias in [1..256] (default 256)
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_alias(self, name: str) -> SimpleAliasData:
        """
        Deletes given Alias. Raises ValueError if it did not exist.
        Also deletes all of the Alias' components. Tread carefully.
        :param name: Alias name to remove.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_aliases(self) -> list[SimpleAliasData]:
        """
        Gets all aliases with their activation rates.
        """
        raise NotImplementedError()

    @abstractmethod
    def alias_exists(self, alias: str) -> bool:
        """
        Does the given Alias exist?
        """
        raise NotImplementedError()

    # endregion

    # region trigger
    @abstractmethod
    def add_trigger(self, alias: str, trigger_type: trigger_types, data: str, rate: int | None) -> None:
        """
        Creates a new Trigger for the given Alias.
        :param alias: Name of the Alias. Raises ValueError if given Alias does not exist.
        :param trigger_type: Type of the Trigger
        :param data: Trigger Data
        :param rate: Optional Trigger rate in [1..256]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_trigger_by_index(self, alias: str, index: int) -> SimpleTriggerData:
        """
        Gets the  TriggerData for the trigger at the given index.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_trigger(self, alias: str, index: int, trigger_type: trigger_types, data: str | None,
                     rate: int | None) -> None:
        """
        Edits the Trigger at the given index, for the given Alias.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        Raises AttributeError if no replacement data was given.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_trigger(self, alias: str, index: int) -> SimpleTriggerData:
        """
        Removes the trigger at the given index, for the given Alias.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        :return: Trigger data of removed trigger.
        """
        raise NotImplementedError()

    # endregion

    # region reply
    @abstractmethod
    def add_reply(self, alias: str, reply_type: reply_types, data, weight) -> None:
        """
        Creates a new Reply of the given type, with the given weight, for the given Alias.
        :param alias: Name of the Alias. Raises ValueError if given Alias does not exist.
        :param reply_type: Type of the Reply. Only supported times may be taken in.
        :param data: Raw reply data in string form. Input type depends on Reply type.
        :param weight: Relative reply weight.
        """
        raise NotImplementedError()

    @abstractmethod
    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None) -> None:
        """
        Edits the reply at the given index, for the given Alias.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        Raises AttributeError if no replacement data was given.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_reply(self, alias: str, index: int) -> SimpleReplyData:
        """
        Removes the reply at the given index, for the given Alias.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        :returns: Reply data of removed reply.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_reply_by_index(self, alias: str, index: int) -> SimpleReplyData:
        """
        Gets a reply with a given index from the Alias.
        Raises ValueError if the Alias does not exist.
        Raises IndexError if given index is out of range.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_replies_by_alias(self, alias: str) -> list[SimpleReplyData]:
        """
        Gets all Replies with the given Alias.
        Raises ValueError if the Alias does not exist.
        """
        raise NotImplementedError()
    # endregion

    # todo: create indexing command options to dump complete data into file.
