import random as _r

from data.implementation.utilities.abstract import AbstractSQLDatabase, CachedAbstractSQLDatabase
from data.interfaces.saying import GlobalAdminSayingInterface, SayingEditorData, SimpleSayingEditorData

"""
Table(s) and design:

SAYING:
- text: str; PISS-compatible data.
- author: int; ID of author
- creation: int; timestamp of creation
- modification: int; timestamp of modification
PK: Creation
"""


class SayingDatabase(CachedAbstractSQLDatabase, GlobalAdminSayingInterface):
    def __init__(self, path: str) -> None:
        super().__init__(
            db_path=path,
            schema_name='saying',
            schema_version=1
        )

    def create_saying(self, text: str, author_id: int) -> None:
        pass

    def edit_saying(self, index: int, text: str, author_id: int) -> SimpleSayingEditorData:
        pass

    def delete_saying(self, index: int) -> SayingEditorData:
        pass

    def get_sayings(self) -> list[SayingEditorData]:
        pass

    def get_saying(self) -> str:
        with self._connection() as conn:
            cursor = conn.cursor()
            # todo: double check table implementation
            cursor.execute("SELECT COUNT(*) FROM Saying")
            count = cursor.fetchone()[0]

            if not count:
                print('No sayings. Add some.')
                return 'I wish I had something to say right now, as I\'m out of inspiration.'

            index: int = _r.randrange(count)

            cursor.execute(
                """
                SELECT Text
                FROM Saying
                ORDER BY CreatedAt DESC LIMIT 1
                OFFSET ?
                """,
                (index,)
            )

            row = cursor.fetchone()
            if row is None:
                return 'My head\'s a mess right now'

            return row['Text']
