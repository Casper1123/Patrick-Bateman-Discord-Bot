from __future__ import annotations

from typing import get_args

from discord import Interaction, Embed, Guild, TextChannel, User, Message

from Rewrite.discorduser.logger.config.abstract import AbstractJSONConfig
from Rewrite.discorduser.logger.config.local import LocalLoggerConfig
from config.local import loggable as local_loggable
from Rewrite.data.interfaces.autoreplies import _reply_types, _trigger_types, ReplyData, TriggerData
from Rewrite.data.interfaces.fact import FactEditorData
from Rewrite.discorduser.user.abstract import BotClient
from Rewrite.utilities.exceptions import CustomDiscordException
from config.universal import loggable, GlobalLoggerLoggerConfig

class GlobalLogger:
    def __init__(self, client: BotClient, config: GlobalLoggerLoggerConfig) -> None:
        """
        :param client: The BotClient to perform the logging. Can be separate from main PB client instance.
        :param config: Configuration data.
        """
        self.client = client
        self.config = config
        self.target_channels: dict[loggable, TextChannel | None] = { i: None for i in get_args(loggable)}

    def update_output_channel(self, act: loggable, target: TextChannel):
        self.target_channels[act] = target
        self.config.update_target_channel(act, target.id)

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
        # todo: double check that this is well implemented
        self._console_log(
            f'[LOCAL FACT_CREATE] {interaction.user.id} : {interaction.user.name} in {guild.id} : {guild.name} :: {text}',
            'local_fact_create')

        embed: Embed = Embed(
            title='[FACT_CREATE]',
            description=f'{text}\n'
                        f'Created by: {interaction.user.name} ({interaction.user.id})\n'
                        f'In: {guild.name} : {guild.id}',
        )
        embed.set_author(name=guild.name, icon_url=guild.icon.url)
        await self._channel_log(embed=embed, act='fact_create')

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
        self._console_log(
            f'[ALIAS_EDIT] {interaction.user.id} : {interaction.user.name} from [{old_name}] :: [Name: {new_name}; Rate: {rate}]',
            'edit_alias')
        embed: Embed = Embed(
            title='[ALIAS_EDIT]',
            description=f'**Old:**\n'
                        f'\t{old_name}\n'
                        f'\n'
                        f'Removed by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_alias')

    async def delete_alias(self, interaction: Interaction, old_name: str):
        self._console_log(
            f'[ALIAS_DELETE] {interaction.user.id} : {interaction.user.name} :: [{old_name}]',
            'delete_alias')
        embed: Embed = Embed(
            title='[ALIAS_DELETE]',
            description=f'**Old:**\n'
                        f'\t{old_name}\n'
                        f'\n'
                        f'Removed by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_alias')
    # endregion
    # region trigger
    async def create_trigger(self, interaction: Interaction, alias: str, trigger_type: _trigger_types, data: str, rate: int | None):
        self._console_log(
            f'[TRIGGER_CREATE] {interaction.user.id} : {interaction.user.name} to Alias {alias} :: [Type: {trigger_type}; Rate: {rate}; Data: {data}]',
            'edit_trigger')
        embed: Embed = Embed(
            title='[TRIGGER_CREATE]',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'\tType: {trigger_type}'
                        f'\tData: {data}\n'
                        f'\tRate: {rate}\n'
                        f'\n'
                        f'Created by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='create_trigger')

    async def edit_trigger(self, interaction: Interaction, old: TriggerData, data: str, rate: int | None) -> None:
        self._console_log(
            f'[TRIGGER_EDIT] {interaction.user.id} : {interaction.user.name} from Alias {old.alias.name}, Old: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}] :: [Rate: {rate}; Data: {data}]',
            'edit_trigger')
        embed: Embed = Embed(
            title='[REPLY_EDIT]',
            description=f'**Alias:** {old.alias.name}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tRate: {old.rate}\n'
                        f'\n'
                        f'**New:**\n'
                        f'\tData: {data}\n'
                        f'\tRate: {rate}\n'
                        f'\n'
                        f'Edited by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_trigger')

    async def delete_trigger(self, interaction: Interaction, alias: str, old: TriggerData):
        self._console_log(
            f'[TRIGGER_DELETE] {interaction.user.id} : {interaction.user.name} from Alias {old.alias.name} :: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}]',
            'delete_trigger')
        embed: Embed = Embed(
            title='[TRIGGER_DELETE]',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tRate: {old.rate}\n'
                        f'\n'
                        f'Removed by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_trigger')
    # endregion
    # region reply
    async def create_reply(self, interaction: Interaction, alias: str, reply_type: _reply_types, data: str, weight: int | None):
        self._console_log(
            f'[REPLY_CREATE] {interaction.user.id} : {interaction.user.name} to Alias {alias} :: [Type: {reply_type}; Weight: {weight}; Data: {data}]',
            'edit_reply')
        embed: Embed = Embed(
            title='[REPLY_CREATE]',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'\tType: {reply_type}'
                        f'\tData: {data}\n'
                        f'\tWeight: {weight}\n'
                        f'\n'
                        f'Created by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='create_reply')

    async def edit_reply(self, interaction: Interaction, old: ReplyData, data: str, weight: int | None):
        self._console_log(
            f'[REPLY_EDIT] {interaction.user.id} : {interaction.user.name} from Alias {old.alias.name}, Old: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}] :: [Weight: {weight}; Data: {data}]',
            'edit_reply')
        embed: Embed = Embed(
            title='[REPLY_EDIT]',
            description=f'**Alias:** {old.alias.name}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tWeight: {old.weight}\n'
                        f'\n'
                        f'**New:**\n'
                        f'\tData: {data}\n'
                        f'\tWeight: {weight}\n'
                        f'\n'
                        f'Edited by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_reply')

    async def delete_reply(self, interaction: Interaction, old: ReplyData):
        self._console_log(
            f'[REPLY_DELETE] {interaction.user.id} : {interaction.user.name} from Alias {old.alias.name} :: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}]',
            'delete_reply')
        embed: Embed = Embed(
            title='[REPLY_DELETE]',
            description=f'**Alias:** {old.alias.name}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tWeight: {old.weight}\n'
                        f'\n'
                        f'Removed by: {interaction.user.name} ({interaction.user.id})',
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_reply')
    # endregion
    # endregion
    # endregion