from Rewrite.data.interfaces.fact import GlobalAdminFactInterface, FactEditorData


class TestFactDatabase(GlobalAdminFactInterface):
    def create_global_fact(self, user_id: int, fact: str) -> None:
        pass

    def edit_global_fact(self, index: int, editor_id: int, new_fact: str) -> FactEditorData:
        if not index == 1:
            raise IndexError()
        return FactEditorData(f'Edited global fact at index {index}', None, 0, 0, 0)

    def delete_global_fact(self, index: int) -> FactEditorData:
        if not index == 1:
            raise IndexError()
        return FactEditorData(f'Deleted global fact at index {index}', None, 0, 0, 0)

    def get_global_facts(self) -> list[FactEditorData]:
        return [
            FactEditorData(f'Global fact at index {i}', None, 0, 0, 0) for i in range(10)
        ]

    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        return {
            g:
                [
                FactEditorData(f'Local fact at index {i}', g, 0, 0, 0) for i in range(10)
                ]
            for g in range(5)
        }

    def create_fact(self, guild_id: int, user_id: int, fact: str) -> None:
        pass

    def edit_fact(self, guild_id: int, index: int, new_fact: str, editor_id: int) -> FactEditorData:
        return FactEditorData(f'Edited local fact at index {index}', guild_id, 0, 0, 0)

    def delete_fact(self, guild_id: int, index: int) -> FactEditorData:
        return FactEditorData(f'Deleted local fact at index {index}', guild_id, 0, 0, 0)

    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        return [
            FactEditorData(f'Local fact at index {i}', guild_id, 0, 0, 0) for i in range(10)
        ]

    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        return 'PISS-test fact: {guild}, {user} at index ' + str(index)

    def get_fact_count(self, guild_id: int | None) -> int:
        return 0 if not guild_id else guild_id

    def __init__(self):
        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_kill_switch = not self.local_fact_kill_switch
        return self.local_fact_kill_switch

    def is_killswitch(self) -> bool:
        return self.local_fact_kill_switch