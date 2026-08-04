from Rewrite.data.interfaces.other import LocalAdminDataInterface


class TestGeneralDatabase(LocalAdminDataInterface):
    def __init__(self, test_output_channel_id: int | None, super_guilds: list[int]):
        self.test_output_channel_id: int | None = test_output_channel_id
        self.super_guilds: list[int] = super_guilds

    def get_log_channel(self, guild_id: int) -> int | None:
        return self.test_output_channel_id if self.test_output_channel_id else None

    def set_log_output(self, guild_id: int, channel_id: int | None) -> None:
        pass