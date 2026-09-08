import time as _time
from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.moderation import GlobalAdminModerationInterface

from configuration.global_config import CFG

"""
Table(s) and design:

banned_users, banned_guilds:
- id
- reason
- since
- banned_by

"""


class ModerationDatabase(CachedAbstractSQLDatabase, GlobalAdminModerationInterface):
    def __init__(self, path: str) -> None:
        super().__init__(
            db_path=path,
            schema_name='moderation',
            schema_version=1
        )

    def toggle_guild_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        self._cache.unregister(
            keys=('guild', identifier)
        )

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM banned_guilds
                WHERE guild_id = ?
                """,
                (identifier,),
            ).fetchone()

            if row is not None:
                conn.execute(
                    """
                    DELETE
                    FROM banned_guilds
                    WHERE guild_id = ?
                    """,
                    (identifier,),
                )
                return False

            conn.execute(
                """
                INSERT INTO banned_guilds (guild_id,
                                           reason,
                                           banned_by,
                                           since)
                VALUES (?, ?, ?, ?)
                """,
                (identifier, reason, author, int(_time.time())),
            )
            return True

    def toggle_user_ban(self, identifier: int, author: int, reason: str | None) -> bool:
        self._cache.unregister(
            keys=('user', identifier)
        )

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM banned_users
                WHERE user_id = ?
                """,
                (identifier,),
            ).fetchone()

            if row is not None:
                conn.execute(
                    """
                    DELETE
                    FROM banned_users
                    WHERE user_id = ?
                    """,
                    (identifier,),
                )
                return False

            conn.execute(
                """
                INSERT INTO banned_users (user_id,
                                          reason,
                                          banned_by,
                                          since)
                VALUES (?, ?, ?, ?)
                """,
                (identifier, reason, author, int(_time.time())),
            )
            return True

    def is_banned_user(self, user_id: int) -> bool:
        val = self._cache.get_cached(
            keys=('user', user_id),
            out_type=bool,
        )
        if val is not None:
            return val

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM banned_users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        val = row is not None

        self._cache.register(
            keys=('user', user_id),
            val=val,
            timeout=30,
            auto_refresh=(
                10,
                30
            )
        )

        return val

    def is_banned_guild(self, guild_id: int) -> bool:
        val = self._cache.get_cached(
            keys=('guild', guild_id),
            out_type=bool,
        )
        if val is not None:
            return val

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM banned_guilds
                WHERE guild_id = ?
                """,
                (guild_id,),
            ).fetchone()

        val = row is not None

        self._cache.register(
            keys=('guild', guild_id),
            val=val,
            timeout=30,
            auto_refresh=(
                10,
                30
            )
        )

        return val

    def is_super_server(self, guild_id: int) -> bool:
        # Global admin server always super server
        return guild_id in CFG.SUPER_SERVER_IDS or guild_id == CFG.GLOBAL_ADMIN_SERVER_ID
