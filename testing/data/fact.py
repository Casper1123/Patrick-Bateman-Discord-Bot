from data.interfaces.fact import GlobalAdminFactInterface, SimpleFactEditorData


class TestFactDatabase(GlobalAdminFactInterface):
    def create_global_fact(self, user_id: int, fact: str) -> None:
        pass

    def edit_global_fact(self, index: int, editor_id: int, new_fact: str) -> SimpleFactEditorData:
        if not index == 1:
            raise IndexError()
        return SimpleFactEditorData(f'Edited global fact at index {index}', None, 0)

    def delete_global_fact(self, index: int) -> SimpleFactEditorData:
        if not index == 1:
            raise IndexError()
        return SimpleFactEditorData(f'Deleted global fact at index {index}', None, 0)

    def get_global_facts(self) -> list[SimpleFactEditorData]:
        return [
            SimpleFactEditorData(f'Global fact at index {i}', None, 0) for i in range(10)
        ]

    def get_all_local_facts(self) -> dict[int, list[SimpleFactEditorData]]:
        return {
            g:
                [
                    SimpleFactEditorData(f'Local fact at index {i}', g, 0) for i in range(10)
                ]
            for g in range(5)
        }

    def create_fact(self, guild_id: int, user_id: int, fact: str) -> None:
        pass

    def edit_fact(self, guild_id: int, index: int, new_fact: str, editor_id: int) -> SimpleFactEditorData:
        return SimpleFactEditorData(f'Edited local fact at index {index}', guild_id, 0)

    def delete_fact(self, guild_id: int, index: int) -> SimpleFactEditorData:
        return SimpleFactEditorData(f'Deleted local fact at index {index}', guild_id, 0)

    def get_local_facts(self, guild_id: int) -> list[SimpleFactEditorData]:
        return [
            SimpleFactEditorData(f'Local fact at index {i}', guild_id, 0) for i in range(10)
        ]

    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        if index is not None and index < 1:
            raise IndexError('index out of range, obviously')
        return 'PISS-test fact: {guild}, {user} at index ' + str(index)

    def get_fact_count(self, guild_id: int | None) -> int:
        return 0 if not guild_id else 1

    def __init__(self):
        self.local_fact_kill_switch: bool = False
        # This killswitch is disabled on-launch, but allows temporary disabling of the Local Fact service in case something goes HORRIBLY wrong.
        # Mostly intended for Moderation purposes.

    def toggle_local_fact_killswitch(self) -> bool:
        self.local_fact_kill_switch = not self.local_fact_kill_switch
        return self.local_fact_kill_switch

    def is_killswitch(self) -> bool:
        return self.local_fact_kill_switch
