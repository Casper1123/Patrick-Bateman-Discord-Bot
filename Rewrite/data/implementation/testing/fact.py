import random as _r

from Rewrite.data.implementation.abstract import AbstractSQLDatabase
from Rewrite.data.interfaces.fact import GlobalAdminFactInterface, FactEditorData


class TestFactDatabase(AbstractSQLDatabase, GlobalAdminFactInterface):
    def __init__(self, path: str):
        super().__init__(path, "data/schemas/fact.sql")

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
        pass

    def get_fact_count(self, guild_id: int | None) -> int:
        pass
    # endregion

    # region Local
    def create_fact(self, guild_id: int, user_id: int, fact: str):
        pass

    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: int, editor_id: int, new_fact: str | None):
        pass

    def delete_fact(self, guild_id: int):
        pass

    def get_local_fact(self, guild_id: int, index: int) -> FactEditorData:
        pass

    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        pass
    # endregion

    # region Global
    def create_global_fact(self, user_id: int, fact: str):
        pass

    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int, new_fact: str | None):
        pass

    def get_global_fact(self, index: int) -> FactEditorData:
        pass

    def get_global_facts(self) -> list[FactEditorData]:
        pass

    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        pass
    # endregion