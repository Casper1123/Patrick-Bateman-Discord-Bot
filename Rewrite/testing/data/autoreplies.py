from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, AliasData, TriggerData, ReplyData, \
    _reply_types, _trigger_types, SimpleReplyData, SimpleTriggerData, SimpleAliasData


class TestAutoreplyDatabase(AbstractSQLDatabase, GlobalTextAutorepliesInterface):
    def create_alias(self, name: str, rate: int) -> None:
        pass

    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None = None) -> None:
        pass

    def delete_alias(self, name: str) -> SimpleAliasData:
        return SimpleAliasData(name=name, rate=256)

    def add_trigger(self, alias: str, trigger_type: _trigger_types, data: str, rate: int | None) -> None:
        pass

    def edit_trigger(self, alias: str, index: int, trigger_type: _trigger_types, data: str | None,
                     rate: int | None) -> None:
        pass

    def remove_trigger(self, alias: str, index: int) -> SimpleTriggerData:
        return SimpleTriggerData(trigger_type='regex', data=f'Trigger from alias {alias} at index {index}', rate=None)

    def add_reply(self, alias: str, reply_type: _reply_types, data, weight) -> None:
        pass

    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None) -> None:
        pass

    def remove_reply(self, alias: str, index: int) -> SimpleReplyData:
        return SimpleReplyData(reply_type='text', data=f'Reply from alias {alias} at index {index}', weight=1)

    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')

    def get_reply(self, alias: str) -> SimpleReplyData | None:
        if alias == 'reaction':
            return SimpleReplyData('reaction', data='🐑;🙃', weight=1)
        elif alias == 'text':
            return SimpleReplyData('text', data='Autoreply in <#{channel} !', weight=1)
        else:
            return SimpleReplyData('text', data=f'Numerical input with alias {alias}', weight=1)

    def get_triggers_by_alias(self) -> dict[SimpleAliasData, list[SimpleTriggerData]]:
        return {
            SimpleAliasData(name='reaction', rate=256): [
                SimpleTriggerData(trigger_type='regex', data=r'^reaction_test$', rate=None)
            ],
            SimpleAliasData(name='text', rate=256): [
                SimpleTriggerData(trigger_type='regex', data=r'^text_autoreply_test$', rate=None)
            ],
            SimpleAliasData(name='number_wildcard_test', rate=256): [
                SimpleTriggerData(trigger_type='regex', data=r'^number_(\d)+$', rate=None)
            ]
        }

    def get_aliases(self) -> list[SimpleAliasData]:
        return [
            SimpleAliasData(name='reaction', rate=256),
            SimpleAliasData(name='text', rate=256),
            SimpleAliasData(name='number_wildcard_test', rate=256)
        ]

    def exists_alias(self, name: str) -> bool:
        return name in ['reaction', 'text', 'number_wildcard_test']

    def get_trigger_by_index(self, alias: str, index: int) -> SimpleTriggerData:
        if alias == 'reaction':
            return SimpleTriggerData(trigger_type='regex', data=r'^reaction_test$', rate=None)
        elif alias == 'text':
            return SimpleTriggerData(trigger_type='regex', data=r'^text_autoreply_test$', rate=None)
        else:
            return SimpleTriggerData(trigger_type='regex', data=r'^number_(\d)+$', rate=None)

    def get_reply_by_index(self, alias: str, index: int) -> SimpleReplyData:
        if alias == 'reaction':
            return SimpleReplyData('reaction', data='🐑;🙃', weight=1)
        elif alias == 'text':
            return SimpleReplyData('text', data='Autoreply in <#{channel} !', weight=1)
        else:
            return SimpleReplyData('text', data=f'Numerical input with alias {alias}', weight=1)

