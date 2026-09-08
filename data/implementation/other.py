from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
from data.interfaces.other import LocalAdminDataInterface

"""
Table(s) and design:

local_log_channels:
- guild_id int PK
- channel_id int

If logging disabled, no entry with guild_id
"""


class GeneralDatabase(CachedAbstractSQLDatabase, LocalAdminDataInterface):
    def __init__(self, path: str):
        super().__init__(
            db_path=path,
            schema_name='other',
            schema_version=1,
            default_cache_timeout=10
        )

    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        self._cache.unregister(
            keys=('log_output', guild_id),
        )
        
        with self._connection() as conn:
            if channel_id is None:
                conn.execute(
                    """
                    DELETE
                    FROM local_log_channels
                    WHERE guild_id = ?
                    """,
                    (guild_id,),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO local_log_channels (guild_id, channel_id)
                    VALUES (?, ?) ON CONFLICT(guild_id) DO
                    UPDATE SET
                        channel_id = excluded.channel_id
                    """,
                    (guild_id, channel_id),
                )

    def get_log_channel(self, guild_id: int) -> int | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT channel_id
                FROM local_log_channels
                WHERE guild_id = ?
                """,
                (guild_id,),
            ).fetchone()

        if row is None:
            val = None
        else:
            val = row["channel_id"]

        self._cache.register(
            keys=('log_channel', guild_id),
            val=val,
            timeout=60,
            auto_refresh=(
                15,
                30
            )
        )

