from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.autoreplies import GlobalTextAutoreplyInterface, SimpleTriggerData, SimpleAliasData, \
    SimpleReplyData, reply_types, trigger_types

"""
Table(s) and design:

ALIAS:
- ID: str - UUID-8 Identifier, unique
- name: str
- rate: int
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

TRIGGER:
- alias: str - FK ID of Alias
- type: str [specifically the literal for options]
- data: str
? rate: int | null - Can be left empty (null) if not overriding the Alias rate.
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

REPLY:
- alias: str - FK ID of Alias
- type: str [specifically the literal for options]
- data: str
- weight: int
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

todo: what PK's?
"""


class AutoreplyDatabase(CachedAbstractSQLDatabase, GlobalTextAutoreplyInterface):
    def create_alias(self, name: str, rate: int) -> None:
        pass

    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None = None) -> None:
        pass

    def delete_alias(self, name: str) -> SimpleAliasData:
        pass

    def get_aliases(self) -> list[SimpleAliasData]:
        pass

    def add_trigger(self, alias: str, trigger_type: trigger_types, data: str, rate: int | None) -> None:
        pass

    def get_trigger_by_index(self, alias: str, index: int) -> SimpleTriggerData:
        pass

    def edit_trigger(self, alias: str, index: int, trigger_type: trigger_types, data: str | None,
                     rate: int | None) -> None:
        pass

    def remove_trigger(self, alias: str, index: int) -> SimpleTriggerData:
        pass

    def add_reply(self, alias: str, reply_type: reply_types, data, weight) -> None:
        pass

    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None) -> None:
        pass

    def remove_reply(self, alias: str, index: int) -> SimpleReplyData:
        pass

    def get_reply_by_index(self, alias: str, index: int) -> SimpleReplyData:
        pass

    def get_replies_by_alias(self, alias: str) -> list[SimpleReplyData]:
        pass

    def get_reply(self, alias: str) -> SimpleReplyData | None:
        pass

    def get_triggers_by_alias(self) -> dict[SimpleAliasData, list[SimpleTriggerData]]:
        pass

    def get_triggers_for_alias(self, alias: str) -> list[SimpleTriggerData]:
        pass

    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')
