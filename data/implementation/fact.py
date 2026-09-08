import random as _r
import time as _time

from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.fact import GlobalAdminFactInterface, SimpleFactEditorData

"""
Table(s) and design:

todo: fill this in.
"""


class FactDatabase(CachedAbstractSQLDatabase, GlobalAdminFactInterface):
    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='fact',
            schema_version=1
        )

        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

    def create_global_fact(self, user_id: int, fact: str) -> None:
        self._cache.unregister(
            keys=('global',)
        )

        now = int(_time.time())

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO globalfact (text,
                                        modified_by,
                                        modified_at,
                                        created_at)
                VALUES (?, ?, ?, ?)
                """,
                (fact, user_id, now, now),
            )

    def edit_global_fact(self, index: int, editor_id: int, new_fact: str) -> SimpleFactEditorData:
        if index < 1:
            raise IndexError('Index must not be smaller than 1.')


        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text
                FROM globalfact
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (index - 1,),
            ).fetchone()

            if row is None:
                raise IndexError('Index out of range.')

            self._cache.unregister(
                keys=('global',)
            )

            conn.execute(
                """
                UPDATE globalfact
                SET text        = ?,
                    modified_by = ?,
                    modified_at = ?
                WHERE id = ?
                """,
                (new_fact, editor_id, int(_time.time()), row['id']),
            )

            return SimpleFactEditorData(
                text=row['text'],
                guild_id=None,
                author_id=editor_id,
            )

    def delete_global_fact(self, index: int) -> SimpleFactEditorData:
        if index < 1:
            raise IndexError('Index must not be smaller than 1.')

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text, modified_by
                FROM globalfact
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (index - 1,),
            ).fetchone()

            if row is None:
                raise IndexError('Index out of range.')

            self._cache.unregister(
                keys=('global',),
            )

            conn.execute(
                """
                DELETE
                FROM globalfact
                WHERE id = ?
                """,
                (row['id'],),
            )

            return SimpleFactEditorData(
                text=row['text'],
                guild_id=None,
                author_id=row['modified_by'],
            )

    def get_global_facts(self) -> list[SimpleFactEditorData]:
        val = self._cache.get_cached(
            keys=('global',),
            out_type=list[SimpleFactEditorData]
        )
        if val is not None:
            return val

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT text, modified_by
                FROM globalfact
                ORDER BY created_at, id
                """
            ).fetchall()

        val = [
            SimpleFactEditorData(
                text=row['text'],
                guild_id=None,
                author_id=row['modified_by'],
            )
            for row in rows
        ]

        self._cache.register(
            keys=('global',),
            val=val,
            timeout=120,
            auto_refresh=(
                30,
                60
            )
        )

        return val

    def get_all_local_facts(self) -> dict[int, list[SimpleFactEditorData]]:
        # No caching on purpose, as this is only used in the index command.
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT guild_id, text, modified_by
                FROM localfact
                ORDER BY guild_id, created_at, id
                """
            ).fetchall()

        facts: dict[int, list[SimpleFactEditorData]] = {}

        for row in rows:
            facts.setdefault(row['guild_id'], []).append(
                SimpleFactEditorData(
                    text=row['text'],
                    guild_id=row['guild_id'],
                    author_id=row['modified_by'],
                )
            )

        return facts

    def create_fact(self, guild_id: int, user_id: int, fact: str) -> None:
        self._cache.unregister(
            keys=('local', guild_id),
        )

        now = int(_time.time())

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO localfact (text,
                                       guild_id,
                                       modified_by,
                                       modified_at,
                                       created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fact, guild_id, user_id, now, now),
            )

    def edit_fact(self, guild_id: int, index: int, new_fact: str, editor_id: int) -> SimpleFactEditorData:
        if index < 1:
            raise IndexError('Index must not be smaller than 1.')

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text, modified_by
                FROM localfact
                WHERE guild_id = ?
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (guild_id, index - 1),
            ).fetchone()

            if row is None:
                raise IndexError('Index out of range.')

            self._cache.unregister(
                keys=('global',)
            )

            conn.execute(
                """
                UPDATE localfact
                SET text        = ?,
                    modified_by = ?,
                    modified_at = ?
                WHERE id = ?
                """,
                (new_fact, editor_id, int(_time.time()), row['id']),
            )

            return SimpleFactEditorData(
                text=row['text'],
                guild_id=guild_id,
                author_id=row['modified_by'],
            )

    def delete_fact(self, guild_id: int, index: int) -> SimpleFactEditorData:
        if index < 1:
            raise IndexError('Index must not be smaller than 1.')

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, text, modified_by
                FROM localfact
                WHERE guild_id = ?
                ORDER BY created_at, id LIMIT 1
                OFFSET ?
                """,
                (guild_id, index - 1),
            ).fetchone()

            if row is None:
                raise IndexError('Index out of range.')

            self._cache.unregister(
                keys=('global',),
            )

            conn.execute(
                """
                DELETE
                FROM localfact
                WHERE id = ?
                """,
                (row['id'],),
            )

            return SimpleFactEditorData(
                text=row['text'],
                author_id=row['modified_by'],
                guild_id=guild_id
            )

    def get_local_facts(self, guild_id: int) -> list[SimpleFactEditorData]:
        val = self._cache.get_cached(
            keys=('local', guild_id),
            out_type=list[SimpleFactEditorData]
        )
        if val is not None:
            return val

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT text, modified_by
                FROM localfact
                WHERE guild_id = ?
                ORDER BY created_at, id
                """,
                (guild_id,),
            ).fetchall()

        val = [
            SimpleFactEditorData(
                text=row['text'],
                guild_id=guild_id,
                author_id=row['modified_by']
            )
            for row in rows
        ]

        self._cache.register(
            keys=('local', guild_id),
            val=val,
            timeout=120,
            auto_refresh=(
                30,
                60
            )
        )

        return val

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_kill_switch = not self.local_fact_kill_switch
        return self.local_fact_kill_switch

    def is_killswitch(self) -> bool:
        return self.local_fact_kill_switch

    # region Regular
    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        if index is not None and index < 1:
            raise IndexError('Index must not be smaller than 1.')
        with self._connection() as conn:

            global_count = conn.execute('SELECT COUNT(*) FROM globalfact').fetchone()[0]

            local_count = 0
            if guild_id is not None:
                local_count = conn.execute(
                    'SELECT COUNT(*) FROM localfact WHERE guild_id = ?',
                    (guild_id,)
                ).fetchone()[0]

            total = global_count + local_count

            # transform index into table ordering offset.
            if index is None:
                if total == 0:
                    raise IndexError('No facts available.')
                offset = _r.randrange(total)
            else:
                offset = index - 1
                if offset >= total:
                    raise IndexError('Index out of range.')

            cursor = conn.cursor()
            # offset implies table to select from
            if offset < global_count:
                cursor.execute(
                    """
                    SELECT text
                    FROM globalfact
                    ORDER BY created_at, id ASC
                    LIMIT 1 OFFSET ?
                    """,
                    (offset,)
                )
            else:
                if guild_id is None:
                    raise IndexError('Index out of range.')

                cursor.execute(
                    """
                    SELECT text
                    FROM localfact
                    WHERE guild_id = ?
                    ORDER BY created_at, id ASC
                    LIMIT 1 OFFSET ?
                    """,
                    (guild_id, offset - global_count)
                )

            row = cursor.fetchone()
            if row is None:
                raise IndexError('Index out of range.')

            return row['text']

    def get_fact_count(self, guild_id: int | None) -> int:
        with self._connection() as conn:
            cursor = conn.cursor()

            if guild_id is None:
                cursor.execute('SELECT COUNT(*) FROM globalfact')
            else:
                cursor.execute(
                    'SELECT COUNT(*) FROM localfact WHERE guild_id = ?',
                    (guild_id,)
                )
            return int(cursor.fetchone()[0])
    # endregion
