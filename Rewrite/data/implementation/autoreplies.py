from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface, AliasData, TriggerData, ReplyData, \
    _reply_types, _trigger_types


"""
Table(s) and design:


"""

class AutoreplyDatabase(AbstractSQLDatabase, GlobalTextAutorepliesInterface):
    def __init__(self, path: str):
        super().__init__(path, 'data/schemas/autoreplies.sql')