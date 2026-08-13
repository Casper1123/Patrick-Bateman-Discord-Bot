from __future__ import annotations

from typing import get_args

from discord import Interaction, Embed, Guild, TextChannel, User, Colour, VoiceChannel, StageChannel, Thread
from discord.abc import Messageable
from discord.ext import commands

from configuration.logger import loggable, GlobalLoggerConfig
from data.interfaces.autoreplies import reply_types, trigger_types, SimpleReplyData, SimpleTriggerData
from data.interfaces.fact import SimpleFactEditorData
from data.interfaces.saying import SimpleSayingEditorData
from discorduser.logger.errors import LoggableErrorContext


class GlobalLogger:
    def __init__(self, client: commands.Bot, config: GlobalLoggerConfig) -> None:
        """
        :param client: Client to look for data for (i.e. logging channels).
        Usually should be the same as the one handling the interactions.
        :param config: Configuration data.
        """
        self.client = client
        self.config = config
        self.target_channels: dict[loggable, Messageable | None] = {i: None for i in get_args(loggable)}

    def update_output_channel(self, act: loggable, target: TextChannel | VoiceChannel | StageChannel | Thread):
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

        if self.target_channels[act] is not None:
            # See if-statement above.
            # noinspection bad-assignment
            channel: Messageable = self.target_channels[act]

        else:
            try:
                channel = self.client.get_channel(self.config.target_channels[act])
            except KeyError:
                channel = None

            if channel is None or not isinstance(channel, Messageable):
                await self.client.close()  # This is harsh. But it's easily the most secure way; if cannot log information, crash application.
                import sys
                sys.exit(f'Closing application as logging channel for action type {act} could not be retrieved. Leftover information:\n'
                    f'{embed.title}\n'
                    f'{embed.description}')
            else:
                channel: Messageable
                # update cache
                self.target_channels[act] = channel

        await channel.send(embed=embed)

    # endregion

    async def log_general(self, console: str, channel: Embed) -> None:
        self._console_log(console, 'general')

        await self._channel_log(channel, 'general')

    async def error(self, error_context: LoggableErrorContext) -> None:
        # todo: somehow build a cooldown into the error? As in, if the same error source has been reported recently, don't log it? (maybe based on interaction user)

        # WARNING: IF NOT ENABLED ALL CAUGHT EXCEPTION TYPES WILL FIZZLE
        self._console_log(error_context.as_console(), 'error')
        await self._channel_log(error_context.as_embed(), 'error')

    # region local-action
    # region fact

    # todo: redo embeds. See below:
    # Standard data
    #
    # Field: Created By
    # Name
    # Id
    # < icon_url to author avatar >
    #
    # Field: Created In
    # Guild name
    # Guild Id

    # Author: Guild, with icon
    #

    async def local_fact_create(self, guild: Guild, interaction: Interaction, text: str) -> None:
        self._console_log(
            f'[LOCAL FACT_CREATE] {interaction.user.id} : {interaction.user.display_name} in {guild.id} : {guild.name} :: {text}',
            'local_fact_create')

        embed: Embed = Embed(
            title='[LOCAL_FACT_CREATE]',
            description=f'{text}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})\n'
                        f'In: {guild.name} ({guild.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        await self._channel_log(embed=embed, act='local_fact_create')

    async def local_fact_edit(self, guild: Guild, interaction: Interaction, old: SimpleFactEditorData,
                              text: str) -> None:
        self._console_log(
            f'[LOCAL FACT_EDIT] {interaction.user.id} : {interaction.user.display_name} in {guild.id} : {guild.name} :: {text}',
            'local_fact_edit')

        embed: Embed = Embed(
            title='[LOCAL_FACT_EDIT]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})\n'
                        f'In: {guild.name} ({guild.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        await self._channel_log(embed=embed, act='local_fact_edit')

    async def local_fact_remove(self, guild: Guild, interaction: Interaction, old: SimpleFactEditorData) -> None:
        self._console_log(
            f'[LOCAL FACT_DELETE] {interaction.user.id} : {interaction.user.display_name} in {guild.id} : {guild.name} :: {old.text}',
            'local_fact_delete')

        embed: Embed = Embed(
            title='[LOCAL_FACT_DELETE]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})\n'
                        f'In: {guild.name} ({guild.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        await self._channel_log(embed=embed, act='local_fact_delete')

    # endregion
    # region other local
    async def local_set_log_channel(self, guild: Guild, interaction: Interaction, channel: TextChannel | VoiceChannel | StageChannel | Thread) -> None:
        self._console_log(
            f'[LOCAL SET_LOG_CHANNEL] Set logging channel for {guild.name} : {guild.id} :: {channel.id} set by {interaction.user.display_name} : {interaction.user.id}',
            'local_log_channel_modify')

        embed: Embed = Embed(
            title='[LOCAL_SET_LOG_CHANNEL]',
            description=f'Set to: {channel.name} ({channel.id})\n'
                        f'\n'
                        f'Set by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.blue()
        )
        try:
            # Handled.
            # noinspection unresolved-references
            embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        except AttributeError:
            embed.set_footer(text=guild.name)

        await self._channel_log(embed, 'local_log_channel_modify')

    # endregion
    # endregion

    # region global-action
    # region fact
    async def fact_create(self, interaction: Interaction, text: str) -> None:
        self._console_log(
            f'[FACT_CREATE] {interaction.user.id} : {interaction.user.display_name} :: {text}',
            'fact_create')

        embed: Embed = Embed(
            title='[FACT_CREATE]',
            description=f'{text}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='fact_create')

    async def fact_edit(self, interaction: Interaction, old: SimpleFactEditorData, text: str) -> None:
        self._console_log(
            f'[FACT_EDIT] {interaction.user.id} : {interaction.user.display_name} :: {text}',
            'fact_edit')

        embed: Embed = Embed(
            title='[FACT_EDIT]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='fact_edit')

    async def fact_remove(self, interaction: Interaction, old: SimpleFactEditorData):
        self._console_log(
            f'[FACT_DELETE] {interaction.user.id} : {interaction.user.display_name} :: {old.text}',
            'fact_delete')

        embed: Embed = Embed(
            title='[FACT_DELETE]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='fact_delete')

    async def fact_modify(self, interaction: Interaction, guild_id: int, old: SimpleFactEditorData, text: str | None) -> None:
        self._console_log(
            f'[FACT_MODIFY] {interaction.user.id} : {interaction.user.display_name} in GuildID {guild_id}, from {old.text} by {old.author_id} :: {text if text else 'Deleted'}',
            'fact_modify')

        try:
            guild = await self.client.fetch_guild(guild_id)
        except:
            guild = None

        embed: Embed = Embed(
            title='[FACT_MODIFY]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text if text else 'Deleted'}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})'
                        f'For Guild **{guild.name if guild else '[fetch failed]'}** ({guild_id})',
            colour=Colour.orange()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='fact_modify')

    # endregion
    # region moderation
    async def ban_user(self, interaction: Interaction, user_id: int, user: User | None, new_state: bool,
                       reason: str | None) -> None:
        self._console_log(
            f'[BAN USER] {interaction.user.id} : {interaction.user.display_name} {'UN' if not new_state else ''}BANNED {'NO NAME AVAILABLE' if not user else user.display_name} : {user_id} {'' if not reason else f'({reason})'}',
            'ban_user')
        # todo: api call for this information? Should be a rare command.
        embed: Embed = Embed(
            title='[BAN USER]',
            description=f'**{'UN' if not new_state else ''}BANNED**\n'
                        f'\n'
                        f'{'NO NAME AVAILABLE' if not user else user.display_name} : {user_id}\n'
                        f'\n'
                        f'Done by: {interaction.user.display_name} ({interaction.user.id})\n'
                        f'{'' if not reason else f'\nReason: *{reason}*'}',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed, 'ban_user')

    async def ban_guild(self, interaction: Interaction, guild_id: int, guild: Guild | None, new_state: bool,
                        reason: str | None) -> None:
        self._console_log(
            f'[BAN GUILD] {interaction.user.id} : {interaction.user.display_name} {'UN' if not new_state else ''}BANNED {'NO NAME AVAILABLE' if not guild else guild.name} : {guild_id} {'' if not reason else f'({reason})'}',
            'ban_guild')
        # todo: api call for this information? Should be a rare command.
        embed: Embed = Embed(
            title='[BAN GUILD]',
            description=f'**{'UN' if not new_state else ''}BANNED**\n'
                        f'\n'
                        f'{'NO NAME AVAILABLE' if not guild else guild.name} : {guild_id}\n'
                        f'\n'
                        f'Done by: {interaction.user.display_name} ({interaction.user.id})\n'
                        f'{'' if not reason else f'\nReason: *{reason}*'}',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed, 'ban_guild')

    async def set_log_channel(self, interaction: Interaction, action: loggable, target: TextChannel | VoiceChannel | StageChannel | Thread):
        """
        Call BEFORE moving channel!
        """
        self._console_log(
            f'[SET LOG CHANNEL] {interaction.user.id} : {interaction.user.display_name} set {action} to {target.id} : {target.name}',
            'general')

        embed: Embed = Embed(
            title='[SET_LOG_CHANNEL]',
            description=f'Moving of {action} logging to <#{target.id}> ({target.name}; {target.id})\n'
                        f'\n'
                        f'Moved by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.blue()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act=action)  # logging to old output channel that it's been moved
        await self._channel_log(embed=embed, act='general')

    # endregion
    # region autoreply
    # region alias
    async def create_alias(self, interaction: Interaction, name: str, rate: int) -> None:
        self._console_log(
            f'[ALIAS_CREATE] {interaction.user.id} : {interaction.user.display_name} :: [Rate: {rate}; Name: {name}]',
            'create_alias')
        embed: Embed = Embed(
            title='[ALIAS_CREATE]',
            description=f'Name: {name}\n'
                        f'Rate: {rate}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='create_alias')

    async def edit_alias(self, interaction: Interaction, old_name: str, new_name: str | None, rate: int | None) -> None:
        self._console_log(
            f'[ALIAS_EDIT] {interaction.user.id} : {interaction.user.display_name} from [{old_name}] :: [Name: {new_name}; Rate: {rate}]',
            'edit_alias')
        embed: Embed = Embed(
            title='[ALIAS_EDIT]',
            description=f'**Old:**\n'
                        f'\t{old_name}\n' # todo: fix this information properly.
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_alias')

    async def delete_alias(self, interaction: Interaction, old_name: str):
        self._console_log(
            f'[ALIAS_DELETE] {interaction.user.id} : {interaction.user.display_name} :: [{old_name}]',
            'delete_alias')
        embed: Embed = Embed(
            title='[ALIAS_DELETE]',
            description=f'**Old:**\n'
                        f'\t{old_name}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_alias')

    # endregion
    # region trigger
    async def create_trigger(self, interaction: Interaction, alias: str, trigger_type: trigger_types, data: str,
                             rate: int | None):
        self._console_log(
            f'[TRIGGER_CREATE] {interaction.user.id} : {interaction.user.display_name} to Alias {alias} :: [Type: {trigger_type}; Rate: {rate}; Data: {data}]',
            'edit_trigger')
        embed: Embed = Embed(
            title='[TRIGGER_CREATE]',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'\tType: {trigger_type}\n'
                        f'\tData: {data}\n'
                        f'\tRate: {rate}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='create_trigger')

    async def edit_trigger(self, interaction: Interaction, alias: str, old: SimpleTriggerData, data: str,
                           rate: int | None) -> None:
        self._console_log(
            f'[TRIGGER_EDIT] {interaction.user.id} : {interaction.user.display_name} from Alias {alias}, Old: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}] :: [Rate: {rate}; Data: {data}]',
            'edit_trigger')
        embed: Embed = Embed(
            title='[REPLY_EDIT]',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tRate: {old.rate}\n'
                        f'\n'
                        f'**New:**\n'
                        f'\tData: {data}\n'
                        f'\tRate: {rate}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_trigger')

    async def delete_trigger(self, interaction: Interaction, alias: str, old: SimpleTriggerData):
        self._console_log(
            f'[TRIGGER_DELETE] {interaction.user.id} : {interaction.user.display_name} from Alias {alias} :: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}]',
            'delete_trigger')
        embed: Embed = Embed(
            title='[TRIGGER_DELETE]',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tRate: {old.rate}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_trigger')

    # endregion
    # region reply
    async def create_reply(self, interaction: Interaction, alias: str, reply_type: reply_types, data: str,
                           weight: int | None):
        self._console_log(
            f'[REPLY_CREATE] {interaction.user.id} : {interaction.user.display_name} to Alias {alias} :: [Type: {reply_type}; Weight: {weight}; Data: {data}]',
            'edit_reply')
        embed: Embed = Embed(
            title='[REPLY_CREATE]',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'\tType: {reply_type}'
                        f'\tData: {data}\n'
                        f'\tWeight: {weight}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='create_reply')

    async def edit_reply(self, interaction: Interaction, alias: str, old: SimpleReplyData, data: str,
                         weight: int | None):
        self._console_log(
            f'[REPLY_EDIT] {interaction.user.id} : {interaction.user.display_name} from Alias {alias}, Old: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}] :: [Weight: {weight}; Data: {data}]',
            'edit_reply')
        embed: Embed = Embed(
            title='[REPLY_EDIT]',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tWeight: {old.weight}\n'
                        f'\n'
                        f'**New:**\n'
                        f'\tData: {data}\n'
                        f'\tWeight: {weight}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='edit_reply')

    async def delete_reply(self, interaction: Interaction, alias: str, old: SimpleReplyData):
        self._console_log(
            f'[REPLY_DELETE] {interaction.user.id} : {interaction.user.display_name} from Alias {alias} :: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}]',
            'delete_reply')
        embed: Embed = Embed(
            title='[REPLY_DELETE]',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tWeight: {old.weight}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='delete_reply')

    # endregion
    # endregion
    # region saying
    async def create_saying(self, interaction: Interaction, text: str):
        self._console_log(f'[SAYING_CREATE] {interaction.user.id} : {interaction.user.display_name} :: {text}', 'saying_create')

        embed: Embed = Embed(
            title='[SAYING_CREATE]',
            description=f'{text}\n'
                        f'\n'
                        f'Created by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='saying_create')

    async def edit_saying(self, interaction: Interaction, old: SimpleSayingEditorData, text: str):
        self._console_log(
            f'[SAYING_EDIT] {interaction.user.id} : {interaction.user.display_name} [{old.text}] :: {text}',
            'saying_edit')

        embed: Embed = Embed(
            title='[SAYING_EDIT]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}\n'
                        f'\n'
                        f'Edited by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='saying_edit')

    async def delete_saying(self, interaction: Interaction, old: SimpleSayingEditorData):
        self._console_log(
            f'[SAYING_DELETE] {interaction.user.id} : {interaction.user.display_name} :: {old.text}',
            'saying_delete')

        embed: Embed = Embed(
            title='[SAYING_DELETE]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(embed=embed, act='saying_delete')
    # endregion
    # endregion
