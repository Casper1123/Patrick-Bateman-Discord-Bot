from Rewrite.data.data_interface_abstracts import GlobalAdminDataInterface, FactEditorData


class SQLDataBase(GlobalAdminDataInterface):
    def __init__(self):
        pass

    # region facts
    # region DataInterface
    def get_fact(self, guild_id: int | None, index: int | None) -> str:
        raise NotImplementedError()

    def get_fact_count(self, guild_id: int | None) -> int:
        raise NotImplementedError()
    # endregion
    # region LocalAdminDataInterface
    def create_fact(self, guild_id: int, user_id: int, fact: str) -> bool:  # todo: better return information?
        raise NotImplementedError()

    def edit_fact(self, guild_id: int, previous_author_id: int, old_fact: str, editor_id: int,
                  new_fact: str | None) -> bool:
        raise NotImplementedError()

    def get_local_fact(self, guild_id: int, index: int) -> FactEditorData:
        raise NotImplementedError()

    def get_local_facts(self, guild_id: int) -> list[FactEditorData]:
        raise NotImplementedError()
    # endregion
    # region GlobalAdminDataInterface
    def get_all_local_facts(self) -> dict[int, list[FactEditorData]]:
        raise NotImplementedError()
    # endregion
    # endregion
    # region global facts
    def create_global_fact(self, user_id: int, fact: str) -> bool:
        raise NotImplementedError()

    def edit_global_fact(self, previous_author_id: int, old_fact: str, editor_id: int,
                         new_fact: str | None) -> bool:
        raise NotImplementedError()

    def get_global_fact(self, index: int) -> FactEditorData:
        raise NotImplementedError()
    def get_global_facts(self) -> list[FactEditorData]:
        raise NotImplementedError()
    # endregion
    # region moderation
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
    # region LocalAdminDataInterface
    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        raise NotImplementedError()

    def get_log_channel(self, guild_id: int) -> int | None:
        raise NotImplementedError()
    # endregion
    # endregion