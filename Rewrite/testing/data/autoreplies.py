from typing import get_args

from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, _reply_types, _trigger_types, \
    SimpleReplyData, SimpleTriggerData, SimpleAliasData


class TestAutoreplyDatabase(GlobalTextAutorepliesInterface):
    def get_triggers_for_alias(self, alias: str) -> list[SimpleTriggerData]:
        # Small enough custom sample to do it this shoddy way.
        dat = self.get_triggers_by_alias()
        for k, v in dat.items():
            if k.name == alias:
                return v
        raise ValueError('bad alias name')

    def alias_exists(self, alias: str) -> bool:
        return alias in ['reaction', 'text', 'number_wildcard_test']

    def create_alias(self, name: str, rate: int) -> None:
        if self.alias_exists(name):
            raise ValueError('duplicate alias')
        if not (1 <= rate <= 256):
            raise Exception('rate out of bounds')

    def edit_alias(self, old_name: str, new_name: str | None, rate: int | None = None) -> None:
        if not self.alias_exists(old_name):
            raise ValueError('invalid alias name')
        if self.alias_exists(new_name):
            raise ValueError('duplicate alias')
        if rate is not None and not (1 <= rate <= 256):
            raise Exception('rate out of bounds')

    def delete_alias(self, name: str) -> SimpleAliasData:
        if not self.alias_exists(name):
            raise ValueError('invalid alias name')

        return SimpleAliasData(name=name, rate=256)

    def add_trigger(self, alias: str, trigger_type: _trigger_types, data: str, rate: int | None) -> None:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not trigger_type in get_args(_trigger_types):
            raise Exception('invalid trigger type')
        if rate is not None and not (1 <= rate <= 256):
            raise Exception('rate out of bounds')

    def edit_trigger(self, alias: str, index: int, trigger_type: _trigger_types, data: str | None,
                     rate: int | None) -> None:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')
        if not trigger_type in get_args(_trigger_types):
            raise Exception('invalid trigger type')
        if rate is not None and not (1 <= rate <= 256):
            raise Exception('rate out of bounds')
        if data is None and rate is None:
            raise AttributeError('both inputs None')

    def remove_trigger(self, alias: str, index: int) -> SimpleTriggerData:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')

        return SimpleTriggerData(trigger_type='regex', data=f'Trigger from alias {alias} at index {index}', rate=None)

    def add_reply(self, alias: str, reply_type: _reply_types, data, weight) -> None:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not reply_type in get_args(_reply_types):
            raise Exception('invalid trigger type')
        if not (weight >= 1):
            raise Exception('weight out of bounds')

    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None) -> None:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')
        if weight is not None and not (weight >= 1):
            raise Exception('weight out of bounds')
        if weight is None and text is None:
            raise AttributeError('both none')

    def remove_reply(self, alias: str, index: int) -> SimpleReplyData:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')

        return SimpleReplyData(reply_type='text', data=f'Reply from alias {alias} at index {index}', weight=1)

    def __init__(self):
        ... # not needed lmao

    def get_reply(self, alias: str) -> SimpleReplyData | None:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')

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

    def get_trigger_by_index(self, alias: str, index: int) -> SimpleTriggerData:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')

        if alias == 'reaction':
            return SimpleTriggerData(trigger_type='regex', data=r'^reaction_test$', rate=None)
        elif alias == 'text':
            return SimpleTriggerData(trigger_type='regex', data=r'^text_autoreply_test$', rate=None)
        else:
            return SimpleTriggerData(trigger_type='regex', data=r'^number_(\d)+$', rate=None)

    def get_reply_by_index(self, alias: str, index: int) -> SimpleReplyData:
        if not self.alias_exists(alias):
            raise ValueError('invalid alias name')
        if not index == 1:
            raise IndexError('index out of bounds')

        if alias == 'reaction':
            return SimpleReplyData('reaction', data='🐑;🙃', weight=1)
        elif alias == 'text':
            return SimpleReplyData('text', data='Autoreply in <#{channel} !', weight=1)
        else:
            return SimpleReplyData('text', data=f'Numerical input with alias {alias}', weight=1)

