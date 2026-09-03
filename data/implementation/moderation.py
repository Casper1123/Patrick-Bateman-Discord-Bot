from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.moderation import GlobalAdminModerationInterface

"""
Table(s) and design:


"""


class ModerationDatabase(CachedAbstractSQLDatabase, GlobalAdminModerationInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/mod.sql')
