import random as _r
from datetime import datetime

from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.fact import GlobalAdminFactInterface, FactEditorData


class TestFactDatabase(GlobalAdminFactInterface):
    def __init__(self):
        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

        # todo: caching

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_kill_switch = not self.local_fact_kill_switch
        return self.local_fact_kill_switch

    def is_killswitch(self) -> bool:
        return self.local_fact_kill_switch

    # region Regular
    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        return f'Fact for guildid {guild_id} at index {index}'

    def get_fact_count(self, guild_id: int | None) -> int:
        return 0 if guild_id is None else guild_id
    # endregion

    # region Local
    def create_fact(self, guild_id: int, user_id: int, fact: str):
        pass

    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: int, editor_id: int, new_fact: str | None):
        pass

    def delete_fact(self, guild_id: int):
        pass

    def get_local_fact(self, guild_id: int, index: int) -> FactEditorData:
        return FactEditorData(guild_id, index, str(index), index)

    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        return [FactEditorData(guild_id, i, str(i), i) for i in range(10)]
    # endregion

    # region Global
    def create_global_fact(self, user_id: int, fact: str):
        pass

    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int, new_fact: str | None):
        pass

    def get_global_fact(self, index: int) -> FactEditorData:
        return FactEditorData(None , index, str(index), index)

    def get_global_facts(self) -> list[FactEditorData]:
        return [FactEditorData(None, i, str(i), i) for i in range(10)]

    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        return {
            g: [
                FactEditorData(g, i, str(i), i) for i in range(10)
            ]
            for g in range(5)
        }
    # endregion