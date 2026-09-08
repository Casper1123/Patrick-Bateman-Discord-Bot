import random as _r
import time as _time

import sqlite3 as _sql

from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.autoreplies import GlobalTextAutoreplyInterface, SimpleTriggerData, SimpleAliasData, \
    SimpleReplyData, reply_types, trigger_types

"""
Table(s) and design:

ALIAS:
- ID: str - UUID-8 Identifier, unique
- name: str
- rate: int
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

TRIGGER:
- alias: str - FK ID of Alias
- type: str [specifically the literal for options]
- data: str
? rate: int | null - Can be left empty (null) if not overriding the Alias rate.
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

REPLY:
- alias: str - FK ID of Alias
- type: str [specifically the literal for options]
- data: str
- weight: int
- authorID: int - ID of author
- modifiedAt: int - timestamp of modification date

todo: what PK's?
"""


class AutoreplyDatabase(CachedAbstractSQLDatabase, GlobalTextAutoreplyInterface):
    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='autoreplies',
            schema_version=1
        )
        
    def create_alias(self, name: str, rate: int, author: int) -> None:
        with self._connection() as conn:
            count = conn.execute(
                    'SELECT COUNT(*) FROM aliases WHERE name = ?',
                    (name,)
                ).fetchone()[0]

            if count > 0:
                raise ValueError(f'Alias already exists: {name}')

            self._cache.unregister(
                keys=('aliases',),
            )

            conn.execute(
                """
                INSERT INTO aliases (name,
                                     rate,
                                     modified_by,
                                     modified_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, rate, author, int(_time.time())),
            )

    def edit_alias(self, old_name: str, author: int, new_name: str | None, rate: int | None = None) -> None:
        if new_name is None and rate is None:
            raise AttributeError('No replacement data was given.')

        with self._connection() as conn:
            old = conn.execute(
                """
                SELECT id
                FROM aliases
                WHERE name = ?
                """,
                (old_name,),
            ).fetchone()

            if old is None:
                raise ValueError(f'Alias not found: {old_name}')

            if new_name is not None:
                existing = conn.execute(
                    """
                    SELECT 1
                    FROM aliases
                    WHERE name = ?
                    """,
                    (new_name,),
                ).fetchone()

                if existing is not None:
                    raise ValueError(f'Alias already exists: {new_name}')

            self._cache.unregister(
                keys=('aliases',),
            )

            now = int(_time.time())

            if new_name is not None:
                conn.execute(
                    """
                    UPDATE aliases
                    SET name        = ?,
                        rate        = COALESCE(?, rate),
                        modified_by = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (new_name, rate, author, now, old['id']),
                )
            else:
                conn.execute(
                    """
                    UPDATE aliases
                    SET rate        = ?,
                        modified_by = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (rate, author, now, old['id']),
                )

    def delete_alias(self, name: str) -> SimpleAliasData:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, rate
                FROM aliases
                WHERE name = ?
                """,
                (name,),
            ).fetchone()

            if row is None:
                raise ValueError(f'Alias not found: {name}')

            self._cache.unregister(
                keys=('aliases',),
            )

            conn.execute(
                """
                DELETE
                FROM aliases
                WHERE id = ?
                """,
                (row['id'],),
            )

        return SimpleAliasData(
            name=row['name'],
            rate=row['rate'],
        )

    def get_aliases(self) -> list[SimpleAliasData]:
        val = self._cache.get_cached(
            keys=('aliases',),
            out_type=list[SimpleAliasData]
        )
        if val is not None:
            return val

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT name, rate
                FROM aliases
                ORDER BY id
                """
            ).fetchall()

        val = [
            SimpleAliasData(
                name=row['name'],
                rate=row['rate'],
            )
            for row in rows
        ]

        self._cache.register(
            keys=('aliases',),
            val=val,
            timeout=60,
            auto_refresh=(
                15,
                30
            )
        )

        return val

    def add_trigger(self, alias: str, trigger_type: trigger_types, data: str, rate: int | None, author: int) -> None:
        pass

    def get_trigger_by_index(self, alias: str, index: int) -> SimpleTriggerData:
        pass

    def edit_trigger(self, alias: str, index: int, trigger_type: trigger_types, data: str | None, rate: int | None,
                     author: int) -> None:
        pass

    def remove_trigger(self, alias: str, index: int) -> SimpleTriggerData:
        pass

    def add_reply(self, alias: str, reply_type: reply_types, data: str, weight: int, author: int) -> None:
        pass

    def edit_reply(self, alias: str, index: int, text: str | None, weight: int | None, author: int) -> None:
        pass

    def remove_reply(self, alias: str, index: int) -> SimpleReplyData:
        pass

    def get_reply_by_index(self, alias: str, index: int) -> SimpleReplyData:
        pass

    def get_replies_by_alias(self, alias: str) -> list[SimpleReplyData]:
        pass

    def get_reply(self, alias: str) -> SimpleReplyData | None:
        replies = self.get_replies_by_alias(alias)

        if not replies:
            return None

        total_weight = sum(reply.weight for reply in replies)

        if total_weight == 0:
            return None

        target = _r.randrange(total_weight)

        for reply in replies:
            if target < reply.weight:
                return reply
            target -= reply.weight

        # Should be unreachable
        raise RuntimeError('Failed to select weighted reply.')

    def get_triggers_by_alias(self) -> dict[SimpleAliasData, list[SimpleTriggerData]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT a.name,
                       a.rate AS alias_rate,
                       t.type,
                       t.data,
                       t.rate
                FROM aliases AS a
                         LEFT JOIN triggers AS t
                                   ON t.alias_id = a.id
                ORDER BY a.id, t.id
                """
            ).fetchall()

        result: dict[SimpleAliasData, list[SimpleTriggerData]] = {}

        for row in rows:
            alias_data = SimpleAliasData(
                name=row['name'],
                rate=row['alias_rate'],
            )

            if alias_data not in result:
                result[alias_data] = []

            if row['type'] is not None:
                result[alias_data].append(
                    SimpleTriggerData(
                        trigger_type=row['type'],
                        data=row['data'],
                        rate=row['rate'],
                    )
                )

        return result

    def get_triggers_for_alias(self, alias: str) -> list[SimpleTriggerData]:
        with self._connection() as conn:
            alias_row = conn.execute(
                """
                SELECT id
                FROM aliases
                WHERE id = ?
                """,
                (alias,),
            ).fetchone()

            if alias_row is None:
                raise ValueError(f'Alias not found: {alias}')

            rows = conn.execute(
                """
                SELECT type, data, rate
                FROM triggers
                WHERE alias_id = ?
                ORDER BY id
                """,
                (alias_row['id'],),
            ).fetchall()

        return [
            SimpleTriggerData(
                trigger_type=row['type'],
                data=row['data'],
                rate=row['rate'],
            )
            for row in rows
        ]