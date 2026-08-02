from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, AliasData, TriggerData, ReplyData, \
    _reply_types, _trigger_types


"""
Table(s) and design:


"""

class AutoreplyDatabase(AbstractSQLDatabase, GlobalTextAutorepliesInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')

    # region Regular
    def get_reply(self, alias: str) -> ReplyData | None:
        pass

    def get_triggers_by_alias(self) -> dict[AliasData, list[TriggerData]]:
        pass
    # endregion

    # region Global
    def create_alias(self, name: str, rate: int):
        pass

    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None = None):
        pass

    def delete_alias(self, name: str):
        pass

    def get_aliases(self) -> list[AliasData]:
        pass

    def exists_alias(self, name: str) -> bool:
        pass

    def add_trigger(self, alias: str, trigger_type: _trigger_types, data: str, rate: int | None):
        pass

    def get_trigger_by_index(self, alias: str, index: int) -> TriggerData:
        pass

    def edit_trigger(self, alias: str, index: int, trigger_type: _trigger_types, data: str | None, rate: int | None):
        pass

    def remove_trigger(self, alias: str, index: int):
        pass

    def add_reply(self, alias: str, reply_type: _reply_types, data, weight):
        pass

    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None):
        pass

    def remove_reply(self, alias: str, index: int):
        pass

    def get_reply_by_index(self, alias: str, index: int) -> ReplyData:
        pass

    # endregion