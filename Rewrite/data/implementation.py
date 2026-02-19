import sqlite3 as _sql
import random as _r

from Rewrite.data.data_interface_abstracts import GlobalAdminDataInterface, FactEditorData


class SQLDataBase(GlobalAdminDataInterface):
    def __init__(self, path: str):
        self.path = path
        # setting up table if not existent.
        with _sql.connect(path) as conn:
            with open("data/schema.sql", "r") as f:
                conn.executescript(f.read())
        # todo: do not forget to implement caching!

        self.super_server_cache: list[int] = []

    # region caching
    def cache_super_server(self, guild_id: int):
        self.super_server_cache.append(guild_id)
    def clear_super_server_cache(self):
        self.super_server_cache = []
    # endregion

    # region sqlite helpers
    def _connection(self) -> _sql.Connection:
        conn = _sql.connect(self.path)
        conn.row_factory = _sql.Row
        return conn
    # endregion

    # region facts
    """
    Table(s) and design:
    # LocalFacts:
    - int; AuthorID (keep track of last modified user ID)
    - str; Text
    - int; GuildID
    - int; ModifiedAt (UNIX Timestamp) (Moderation purposes)
    - int; CreatedAt (UNIX Timestamp) (to order for indices)
    PK: (GuildID, Text)
    Order by ModifiedAt for Indexing purposes.
    Disallows users adding duplicate facts.
    """
    # region DataInterface
    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        if index is not None and index < 1:
            raise IndexError('Index must not be smaller than 1.')
        with self._connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM GlobalFacts")
            global_count = cursor.fetchone()[0]

            local_count = 0
            if guild_id is not None:
                cursor.execute(
                    "SELECT COUNT(*) FROM LocalFacts WHERE GuildID = ?",
                    (guild_id,)
                )
                local_count = cursor.fetchone()[0]

            total = global_count + local_count

            # transform index into table ordering offset.
            if index is None:
                if total == 0:
                    raise IndexError("No facts available.")
                offset = _r.randrange(total)
            else:
                offset = index - 1
                if offset >= total:
                    raise IndexError("Index out of range.")

            # offset implies table to select from
            if offset < global_count:
                cursor.execute(
                    """
                    SELECT Text
                    FROM GlobalFacts
                    ORDER BY CreatedAt DESC
                    LIMIT 1 OFFSET ?
                    """,
                    (offset,)
                )
            else:
                if guild_id is None:
                    raise IndexError("Index out of range.")

                cursor.execute(
                    """
                    SELECT Text
                    FROM LocalFacts
                    WHERE GuildID = ?
                    ORDER BY CreatedAt DESC
                    LIMIT 1 OFFSET ?
                    """,
                    (guild_id, offset - global_count)
                )

            row = cursor.fetchone()
            if row is None:
                raise IndexError("Index out of range.")

            return row['Text']

    def get_fact_count(self, guild_id: int | None) -> int:
        with self._connection() as conn:
            cursor = conn.cursor()

            if guild_id is None:
                cursor.execute("SELECT COUNT(*) FROM GlobalFacts")
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM LocalFacts WHERE GuildID = ?",
                    (guild_id,)
                )
            return int(cursor.fetchone()[0])
    # endregion
    # region LocalAdminDataInterface
    def create_fact(self, guild_id: int, user_id: int, fact: str) -> bool:  # todo: better return information?
        raise NotImplementedError()

    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: str, editor_id: int,
                  new_fact: str | None) -> bool:
        raise NotImplementedError()

    def get_local_fact(self, guild_id: int, index: int) -> FactEditorData:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Text
                FROM LocalFacts
                WHERE GuildID = ?
                ORDER BY CreatedAt DESC
                LIMIT 1 OFFSET ?
                """,
                (guild_id, index - 1)
            )
            row = cursor.fetchone()
            if row is None:
                raise IndexError("Index out of range.")
            return FactEditorData(row['GuildID'], row['AuthorID'], row['Text'], row['ModifiedAt'])

    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        raise NotImplementedError()
    # endregion
    # region GlobalAdminDataInterface
    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        raise NotImplementedError()
    # endregion
    # endregion
    # region global facts
    """
    Table(s) and design:
    # GlobalFacts:
    - int; AuthorID (keep track of last modified user ID)
    - str; Text
    - int; ModifiedAt (UNIX Timestamp) (Moderation purposes)
    - int; CreatedAt (UNIX Timestamp) (to order for indices)
    PK: (Text)
    Order by ModifiedAt for Indexing purposes.
    Disallows users adding duplicate facts.
    """
    def create_global_fact(self, user_id: int, fact: str) -> bool:
        raise NotImplementedError()

    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int,
                         new_fact: str | None) -> bool:
        raise NotImplementedError()

    def get_global_fact(self, index: int) -> FactEditorData:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT Text
                FROM GlobalFacts
                ORDER BY CreatedAt DESC
                LIMIT 1 OFFSET ?
                """,
                (index - 1,)
            )
            row = cursor.fetchone()
            if row is None:
                raise IndexError("Index out of range.")
            return FactEditorData(None, row['AuthorID'], row['Text'], row['ModifiedAt'])
    def get_global_facts(self) -> list[FactEditorData]:
        raise NotImplementedError()
    # endregion
    # region moderation
    """
    Table(s) and design:
    # BannedUsers
    - int; UserID
    PK: (UserID)
    
    # BannedGuilds
    - int; GuildID
    PK: (GuildID)
    
    # SuperServers
    - int; GuildID
    PK: (GuildID)
    
    All three simple lists of ids to keep track of.
    """
    # region LocalAdminDataInterface
    def is_banned_user(self, user_id: int) -> bool:
        raise NotImplementedError()

    def is_banned_guild(self, guild_id: int) -> bool:
        raise NotImplementedError()

    def is_super_server(self, guild_id: int) -> bool:
        raise NotImplementedError()
    # endregion
    # region GlobalAdminDataInterface
    def get_super_server_ids(self) -> list[int]:
        raise NotImplementedError()

    def ban_user(self, user_id: int) -> None:
        raise NotImplementedError()

    def unban_user(self, user_id: int) -> None:
        raise NotImplementedError()

    def ban_guild(self, guild_id: int) -> None:
        raise NotImplementedError()

    def unban_guild(self, guild_id: int) -> None:
        raise NotImplementedError()
    # endregion
    # endregion

    # region other
    """
    Table(s) and design:
    # LocalLogChannels
    - int; GuildID
    - int; ChannelID
    PK: (GuildID)
    """
    # region LocalAdminDataInterface
    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        raise NotImplementedError()

    def get_log_channel(self, guild_id: int) -> int | None:
        raise NotImplementedError()
    # endregion
    # endregion