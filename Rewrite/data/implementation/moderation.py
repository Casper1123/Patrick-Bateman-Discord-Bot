from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface


"""
Table(s) and design:


"""

class ModerationDatabase(AbstractSQLDatabase, GlobalAdminModerationInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/mod.sql')