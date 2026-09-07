import random as _r
import time as _time

from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
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
        self._cache.unregister(
            keys=('get_sayings',),
        )

        now = int(_time.time())

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO saying (text,
                                    modified_by,
                                    modified_at,
                                    created_at)
                VALUES (?, ?, ?, ?)
                """,
                (text, author_id, now, now),
            )

    def edit_saying(self, index: int, text: str, author_id: int) -> SimpleSayingEditorData:
        if index < 1:
            raise IndexError(f"Saying index {index} is out of range.")

        self._cache.unregister(
            keys=('get_sayings',),
        )

        now = int(_time.time())

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text
                FROM saying
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (index - 1,),
            ).fetchone()

            if row is None:
                raise IndexError(f"Saying index {index} is out of range")

            conn.execute(
                """
                UPDATE saying
                SET text        = ?,
                    modified_by = ?,
                    modified_at = ?
                WHERE id = ?
                """,
                (text, author_id, now, row["id"]),
            )

        return SimpleSayingEditorData(text=row["text"])

    def delete_saying(self, index: int) -> SayingEditorData:
        if index < 1:
            raise IndexError(f"Saying index {index} is out of range.")

        self._cache.unregister(
            keys=('get_sayings',),
        )

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text, modified_by, modified_at
                FROM saying
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (index - 1,),
            ).fetchone()

            if row is None:
                raise IndexError(f"Saying index {index} is out of range")

            conn.execute(
                """
                DELETE
                FROM saying
                WHERE id = ?
                """,
                (row["id"],),
            )

        return SayingEditorData(
            text=row["text"],
            author_id=row["modified_by"],
            modified_at=row["modified_at"]
        )

    def get_sayings(self) -> list[SayingEditorData]:
        val = self._cache.get_cached(
            keys=('get_sayings',),
            out_type=list[SayingEditorData],
        )
        if val is not None:
            return val

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT text, modified_by, modified_at
                FROM saying
                ORDER BY created_at, id
                """
            ).fetchall()

        val = [
            SayingEditorData(
                text=row["text"],
                author_id=row["modified_by"],
                modified_at=row["modified_at"],
            )
            for row in rows
        ]

        self._cache.register(
            keys=('get_sayings',),
            val=val,
            timeout=60,
            auto_refresh=(
                15,
                30
            )
        )
        return val

    def get_saying(self) -> str:
        val = self._cache.get_cached(
            keys=('get_sayings',),
            out_type=list[SayingEditorData],
        )
        if val is not None and val:
            # I mean, if it's cached anyway might as well snag it, no?
            return _r.choice(val)

        with self._connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM saying"
            ).fetchone()[0]

            if count == 0:
                return (
                    "I wish I had something to say right now, "
                    "as I'm out of inspiration."
                )

            index = _r.randrange(count)

            row = conn.execute(
                """
                SELECT text
                FROM saying
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (index,),
            ).fetchone()

            if row is None:
                return "My head's a mess right now."

            return row["text"]
