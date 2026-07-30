from __future__ import annotations

from enum import Enum
from mailbox import Message
from typing import Literal

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
    def __init__(self):
        self.output_to_console: dict[loggable, bool] = ...
        self.actively_logging: dict[loggable, bool] = ...
        self.target_channels: dict[loggable, int] = ...

class GlobalLogger: # todo: make this a bot subclass, to be able to pass it a different token for a different logging account?
    def __init__(self, client: BotClient, config: GlobalLoggerConfig) -> None:
        self.client = client
        self.config = config
        self.target_channels: dict[loggable, int | None] = { i: None for i in loggable}

    # region log out
    def _console_log(self, out: str, act: loggable) -> None:
        if self.config.output_to_console[act]:
            print(out)

    # todo: buffer messages for x seconds and then send one thing with multiple embeds in one go to prevent ratelimiting?
    async def _channel_log(self, embed: Embed, act: loggable) -> None:
        if self.config.actively_logging[act]:
            # Get channel if found, otherwise default to something.
            if not self.target_channels[act]:
                channel = self.client.get_channel(self.config.target_channels[act])
                if not channel:
                    await self.client.close() # This is harsh. But it's easily the most secure way.
                    print(f'Closed application as logging channel for action type {act} could not be retrieved. Leftover information:\n'
                          f'{embed.title}\n'
                          f'{embed.description}')
                    import sys
                    sys.exit(1)
            else:
                channel = self.target_channels[act]
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