import random as _r

from data.implementation.utilities.abstract import AbstractSQLDatabase
from data.interfaces.fact import GlobalAdminFactInterface

"""
Table(s) and design:

# GlobalFacts:
- str; Text
- int; CreatedAt (UNIX Timestamp) (order on for index offset; needs to remain static regardless of edits)
- int; AuthorID (keep track of last modified user ID)
- int; ModifiedAt (UNIX Timestamp) (Moderation purposes)
PK: Text

# LocalFacts:
- str; Text
- int; GuildID (Guild local fact belongs to)
- int; CreatedAt (UNIX Timestamp) (to order for indexing)
- int; AuthorID (keep track of last modified user ID)
- int; ModifiedAt (UNIX Timestamp) (Moderation purposes)
PK: (GuildID, Text)

Order by CreatedAt for Indexing purposes.
Disallows users adding duplicate facts, which is good.
"""


class FactDatabase(AbstractSQLDatabase, GlobalAdminFactInterface):
    def __init__(self, path: str):
        super().__init__(path, "data/schemas/fact.sql")

        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

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
