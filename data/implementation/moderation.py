from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.moderation import GlobalAdminModerationInterface

"""
Table(s) and design:


"""


class ModerationDatabase(AbstractSQLDatabase, GlobalAdminModerationInterface):
    def __init__(self, path: str) -> None:
        super().__init__(path, 'data/schemas/mod.sql')
