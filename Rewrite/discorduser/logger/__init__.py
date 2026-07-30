from __future__ import annotations

from enum import Enum
from mailbox import Message
from typing import Literal, get_args

from discord import Interaction, Embed, Guild, TextChannel, User
from discord.ext import commands

from Rewrite.data.interfaces.autoreplies import AliasData, _reply_types, ReplyData
from Rewrite.data.interfaces.fact import FactEditorData
from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.utilities.exceptions import CustomDiscordException

loggable = Literal['general', 'error',
    'local_fact_create', 'local_fact_edit', 'local_fact_delete',
    'local_log_channel_modify',

    'fact_create', 'fact_edit', 'fact_delete', 'fact_modify',
    'ban_user', 'ban_guild',

    'create_alias', 'edit_alias', 'delete_alias',
    'create_trigger', 'edit_trigger', 'delete_trigger',
    'create_reply', 'edit_reply', 'delete_reply',
]

class GlobalLoggerConfig:
    def __init__(self, output_to_console: dict[loggable, bool], actively_logging: dict[loggable, bool], target_channels: dict[loggable, int]):
        """
        Each dict requires exactly all, and no other, of the `loggable` properties to be set, otherwise it will raise an AssertionError.
        :param output_to_console: Should this loggable be printed to console?
        :param actively_logging: Should this loggable be sent into its respective channel?
        :param target_channels: Channel ids for actively logged actions. **WARNING:** If this channel is not found at runtime, the program will terminate with error code `1`.
        """
        # Validation of input
        validation: set[str] = set(get_args(loggable))
        assert set(output_to_console.keys()) == validation, 'output_to_console must contain only and all loggables'
        assert set(actively_logging.keys()) == validation, 'actively_logging must contain only and all loggables'
        assert set(target_channels.keys()) == validation, 'target_channels must contain only and all loggables'

        self.output_to_console: dict[loggable, bool] = output_to_console
        self.actively_logging: dict[loggable, bool] = actively_logging
        self.target_channels: dict[loggable, int] = target_channels

    @staticmethod
    def build_config():
        from local import console_loggable as local_console_loggable
        ... # todo: Create YAML file data for all required settings

class GlobalLogger:
    def __init__(self, client: BotClient, config: GlobalLoggerConfig) -> None:
        """
        :param client: The BotClient to perform the logging. Can be separate from main PB client instance.
        :param config: Configuration data.
        """
        self.client = client
        self.config = config
        self.target_channels: dict[loggable, TextChannel | None] = { i: None for i in get_args(loggable)}

    def update_output_channel(self, act: loggable, target: TextChannel):
        self.target_channels[act] = target
        self.config.target_channels[act] = target.id
        # todo: update read file with new path
        # todo: create command to set value.

    # region log out
    def _console_log(self, out: str, act: loggable) -> None:
        try:
            if self.config.output_to_console[act]:
                print(out)
        except KeyError:
            print(f'Could not find output setting for action type {act}.\n\t{out}')

    # todo: buffer messages for x seconds and then send one thing with multiple embeds in one go to prevent ratelimiting?
    # Man, knowing that any exception thrown here goes on 'forever' is annoying.
    async def _channel_log(self, embed: Embed, act: loggable) -> None:
        if not self.config.actively_logging[act]:
            return

        # Get channel if found, otherwise default to something.
        if self.target_channels[act]:
            channel = self.target_channels[act]
        else:
            try:
                channel = self.client.get_channel(self.config.target_channels[act])
            except KeyError:
                channel = None

            if not channel:
                await self.client.close() # This is harsh. But it's easily the most secure way; if cannot log information, crash application.
                print(f'Closed application as logging channel for action type {act} could not be retrieved. Leftover information:\n'
                      f'{embed.title}\n'
                      f'{embed.description}')
                import sys
                sys.exit(1)


        await channel.send(embed=embed)
    # endregion

    async def log_general(self, guild: Guild, message: Message | Interaction, *args, **kwargs) -> None:
        raise NotImplementedError()

    async def error(self, interaction: Interaction | Message, error: CustomDiscordException | Exception) -> None:
        raise NotImplementedError()

    # region local-action
    # region fact
    async def local_fact_create(self, guild: Guild, interaction: Interaction, text: str) -> None:
        raise NotImplementedError()

    async def local_fact_edit(self, guild: Guild, interaction: Interaction, old: FactEditorData, text: str) -> None:
        raise NotImplementedError()

    async def local_fact_remove(self, guild: Guild, interaction: Interaction, old: FactEditorData) -> None:
        raise NotImplementedError()
    # endregion
    # region other local
    async def local_set_log_channel(self, guild: Guild, interaction: Interaction, channel: TextChannel) -> None:
        raise NotImplementedError()
    # endregion
    # endregion

    # region global-action
    # region fact
    async def fact_create(self, interaction: Interaction, text: str) -> None:
        raise NotImplementedError()

    async def fact_edit(self, interaction: Interaction, old: FactEditorData, text: str) -> None:
        raise NotImplementedError()

    async def fact_remove(self, interaction: Interaction, old: FactEditorData):
        raise NotImplementedError()

    async def fact_modify(self, interaction: Interaction, guild_id: int, old: FactEditorData, text: str) -> None:
        raise NotImplementedError() # note: this is specifically for the moderation of other servers.
    # endregion
    # region moderation
    async def ban_user(self, interaction: Interaction, user_id: int, user: User | None, new_state: bool) -> None:
        raise NotImplementedError()

    async def ban_guild(self, interaction: Interaction, guild_id: int, guild: Guild | None, new_state: bool) -> None:
        raise NotImplementedError()

    async def set_log_channel(self, interaction: Interaction, action: loggable, target: TextChannel):
        raise NotImplementedError() # Logged as a general action.

    # endregion
    # region autoreply
    # region alias
    async def create_alias(self, interaction: Interaction, name: str, rate: int) -> None:
        raise NotImplementedError()

    async def edit_alias(self, interaction: Interaction, old_name: str, new_name: str | None, rate: int | None) -> None:
        raise NotImplementedError()

    async def delete_alias(self, interaction: Interaction, old_name: str):
        raise NotImplementedError()
    # endregion
    # region trigger
    async def create_trigger(self, interaction: Interaction, alias: str, text: str, rate: int | None):
        raise NotImplementedError()

    async def edit_trigger(self, interaction: Interaction, alias: str, index: int, text: str | None, rate: int | None) -> None:
        raise NotImplementedError()

    async def delete_trigger(self, interaction: Interaction, alias: str, index: int, old_data: str):
        raise NotImplementedError()
    # endregion
    # region reply
    async def create_reply(self, interaction: Interaction, alias: str, reply_type: _reply_types, data: str, weight: int | None):
        raise NotImplementedError()

    async def edit_reply(self, interaction: Interaction, old: ReplyData, data: str, weight: int | None):
        raise NotImplementedError()

    async def delete_reply(self, interaction: Interaction, old: ReplyData):
        raise NotImplementedError()
    # endregion
    # endregion
    # endregion