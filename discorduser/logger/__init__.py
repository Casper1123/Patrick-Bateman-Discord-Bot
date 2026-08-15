from __future__ import annotations

from typing import get_args

from discord import Interaction, Embed, Guild, TextChannel, User, Colour, VoiceChannel, StageChannel, Thread, Member
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

    # region visualization-helpers
    # noinspection method-may-be-static
    def _performed_by(self, vis: Embed, interaction: Interaction) -> Embed:
        """
        Standard visualization for 'performed by this person'. It does this by setting the footer.
        Returns object after mutation.
        """

        # noinspection DuplicatedCode
        if isinstance(interaction.user, Member):
            vis.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            vis.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        return vis

    # endregion

    async def log_general(self, console: str, channel: Embed) -> None:
        """
        Log given data to the 'general' channel.
        :param console: Console printable string.
        :param channel: Embed to be sent into the log channel
        """
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
            out=f'[ LOCAL FACT_CREATE ] in {guild.name} ({guild.id}) by {interaction.user.display_name} ({interaction.user.id}) :: {text}',
            act='local_fact_create'
        )

        embed: Embed = Embed(
            title='Local fact created',
            description=f'**New:**\n'
                        f'{text}',
            colour=Colour.green()
        )

        self._performed_by(embed, interaction)

        try:
            # noinspection unresolved-references
            embed.set_author(name=f'{guild.name} ({guild.id})', icon_url=guild.icon.url)
        except AttributeError:
            embed.set_author(name=f'{guild.name} ({guild.id})')

        await self._channel_log(embed=embed, act='local_fact_create')

    async def local_fact_edit(self, guild: Guild, interaction: Interaction, old: SimpleFactEditorData,
                              text: str) -> None:
        self._console_log(
            out=f'[ LOCAL FACT EDIT ] in {guild.name} ({guild.id}) by {interaction.user.display_name} ({interaction.user.id}) :: {old.text} ::to:: {text}',
            act='local_fact_edit'
        )

        embed: Embed = Embed(
            title='Local fact edited',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)
        
        try:
            # noinspection unresolved-references
            embed.set_author(name=f'{guild.name} ({guild.id})', icon_url=guild.icon.url)
        except AttributeError:
            embed.set_author(name=f'{guild.name} ({guild.id})')

        await self._channel_log(embed=embed, act='local_fact_edit')

    async def local_fact_delete(self, guild: Guild, interaction: Interaction, old: SimpleFactEditorData) -> None:
        self._console_log(
            out=f'[ LOCAL FACT DELETE ] in {guild.name} ({guild.id}) by {interaction.user.display_name} ({interaction.user.id}) ::old:: {old.text}',
            act='local_fact_delete'
        )

        embed: Embed = Embed(
            title='Local fact deleted',
            description=f'**Old:**\n'
                        f'{old.text}',
            colour=Colour.red()
        )

        embed.set_footer(
            text=f'{interaction.user.display_name} ({interaction.user.id})',
            icon_url=interaction.user.display_avatar.url
        )

        try:
            # noinspection unresolved-references
            embed.set_author(name=f'{guild.name} ({guild.id})', icon_url=guild.icon.url)
        except AttributeError:
            embed.set_author(name=f'{guild.name} ({guild.id})')

        await self._channel_log(embed=embed, act='local_fact_delete')

    # endregion
    # region other local
    async def local_set_log_channel(self, guild: Guild, interaction: Interaction, channel: TextChannel | VoiceChannel | StageChannel | Thread) -> None:
        self._console_log(
            f'[LOCAL SET LOG CHANNEL ] in {guild.name} ({guild.id}) by {interaction.user.display_name} ({interaction.user.id}) :: {channel.name} ({channel.id})',
            'local_log_channel_modify')

        embed: Embed = Embed(
            title='Local log channel set',
            description=f'Set to: {channel.name} ({channel.id})',
            colour=Colour.default()
        )

        self._performed_by(embed, interaction)

        try:
            # noinspection unresolved-references
            embed.set_author(name=f'{guild.name} ({guild.id})', icon_url=guild.icon.url)
        except AttributeError:
            embed.set_author(name=f'{guild.name} ({guild.id})')

        await self._channel_log(embed, 'local_log_channel_modify')

    # endregion
    # endregion

    # region global-action
    # region fact
    async def fact_create(self, interaction: Interaction, text: str) -> None:
        self._console_log(
            out=f'[ FACT CREATE ] by {interaction.user.display_name} ({interaction.user.id}) :: {text}',
            act='fact_create'
        )

        embed: Embed = Embed(
            title='Fact created',
            description=f'**New:**\n'
                        f'{text}',
            colour=Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='fact_create')

    async def fact_edit(self, interaction: Interaction, old: SimpleFactEditorData, text: str) -> None:
        self._console_log(
            f'[ FACT EDIT ] by {interaction.user.display_name} ({interaction.user.id}) :: {old.text} ::to:: {text}',
            'fact_edit')

        embed: Embed = Embed(
            title='Fact edited',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}\n',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='fact_edit')

    async def fact_delete(self, interaction: Interaction, old: SimpleFactEditorData):
        self._console_log(
            f'[FACT_DELETE] by {interaction.user.display_name} ({interaction.user.id}) :: {old.text}',
            'fact_delete')

        embed: Embed = Embed(
            title='Fact deleted',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'Removed by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.red()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='fact_delete')

    async def fact_modify(self, interaction: Interaction, guild_id: int, old: SimpleFactEditorData, text: str | None) -> None:
        guild = self.client.get_guild(guild_id) # todo: api call?

        self._console_log(
            f'[ FACT MODIFY ] by {interaction.user.display_name} ({interaction.user.id}) for guild {f'{guild.name} ({guild.id})' if guild else guild_id} :: {old.text} by {old.author_id} ::to:: {text if text else 'Deleted'}',
            'fact_modify')

        embed: Embed = Embed(
            title='Fact modified',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text if text else 'Deleted'}\n'
                        f'\n'
                        f'For Guild **{guild.name if guild else '[fetch failed]'}** ({guild_id})',
            colour=Colour.purple() if text is not None else Colour.dark_purple()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='fact_modify')

    # endregion
    # region moderation
    async def ban_user(self, interaction: Interaction, user_id: int, user: User | None, banned: bool,
                       reason: str | None) -> None:
        self._console_log(
            f'[ BAN USER ] by {interaction.user.display_name} ({interaction.user.id}) {'banned' if banned else 'unbanned'} {f'{user.display_name} ({user.id})' if user else user_id} {'' if not reason else f'({reason})'}',
            'ban_user')

        # todo: api call for this information? Should be a rare command.

        embed: Embed = Embed(
            title=f'User {'banned' if banned else 'unbanned'}',
            description=f'**{'Banned' if banned else 'Unbanned'}**\n'
                        f'{f'{user.display_name} ({user.id})' if user else user_id}\n'
                        f'<@{user_id}>\n'
                        f'\n'
                        f'{'' if not reason else f'\nReason: *{reason}*'}',
            colour=Colour.red() if banned else Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed, 'ban_user')

    async def ban_guild(self, interaction: Interaction, guild_id: int, guild: Guild | None, banned: bool,
                        reason: str | None) -> None:
        self._console_log(
            f'[ BAN GUILD ] by {interaction.user.display_name} ({interaction.user.id}) {'banned' if banned else 'unbanned'} {f'{guild.name} ({guild.id})' if guild else guild_id} {'' if not reason else f'({reason})'}',
            'ban_guild')

        # todo: api call for this information? Should be a rare command.

        embed: Embed = Embed(
            title=f'Guild {'banned' if banned else 'unbanned'}',
            description=f'**{'Banned' if banned else 'Unbanned'}**\n'
                        f'{f'{guild.name} ({guild.id})' if guild else guild_id}\n'
                        f'\n'
                        f'{'' if not reason else f'\nReason: *{reason}*'}',
            colour=Colour.red() if banned else Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed, 'ban_guild')

    async def set_log_channel(self, interaction: Interaction, action: loggable, target: TextChannel | VoiceChannel | StageChannel | Thread):
        """
        Call BEFORE moving channel!
        """
        self._console_log(
            f'[ SET LOG CHANNEL ] by {interaction.user.display_name} ({interaction.user.id}) set {action} to {target.name} ({target.id})',
            'general')

        embed: Embed = Embed(
            title='Log channel set',
            description=f'Moving of {action} logging to <#{target.id}> ({target.name}; {target.id})\n'
                        f'\n'
                        f'Moved by: {interaction.user.display_name} ({interaction.user.id})',
            colour=Colour.blue()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act=action)  # logging to old output channel that it's been moved
        await self._channel_log(embed=embed, act='general')

    # endregion
    # region autoreply
    # region alias
    async def alias_create(self, interaction: Interaction, name: str, rate: int) -> None:
        self._console_log(
            f'[ ALIAS CREATE ] by {interaction.user.display_name} ({interaction.user.id}) :: [Name: {name}; Rate: {rate}]',
            'create_alias')
        embed: Embed = Embed(
            title='Alias created',
            description=f'Name: {name}\n'
                        f'Rate: {rate}',
            colour=Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='create_alias')

    async def alias_edit(self, interaction: Interaction, old_name: str, new_name: str | None, rate: int | None) -> None:
        self._console_log(
            f'[ ALIAS EDIT ] by {interaction.user.display_name} ({interaction.user.id}) from [{old_name}] :: [Name: {new_name}; Rate: {rate}]',
            'edit_alias')
        embed: Embed = Embed(
            title='Alias edited',
            description=f'**Old:**\n'
                        f'Name: {old_name}\n' # todo: fix this information properly.
                        f'\n'
                        f'**New:**\n'
                        f'Name: {new_name}\n'
                        f'Rate: {rate}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='edit_alias')

    async def alias_delete(self, interaction: Interaction, old_name: str):
        self._console_log(
            f'[ ALIAS DELETE ] by {interaction.user.display_name} ({interaction.user.id}) :: [{old_name}]',
            'delete_alias')

        embed: Embed = Embed(
            title='Alias deleted',
            description=f'**Old:**\n'
                        f'Name: {old_name}',
            colour=Colour.red()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='delete_alias')

    # endregion
    # region trigger
    async def trigger_create(self, interaction: Interaction, alias: str, trigger_type: trigger_types, data: str,
                             rate: int | None):
        self._console_log(
            f'[ TRIGGER CREATE ] by {interaction.user.display_name} ({interaction.user.id}) to Alias {alias} :: [Type: {trigger_type}; Rate: {rate}; Data: {data}]',
            'create_trigger')
        embed: Embed = Embed(
            title='Trigger created',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'Type: {trigger_type}\n'
                        f'Rate: {rate}\n'
                        f'Data: {data}',
            colour=Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='create_trigger')

    async def trigger_edit(self, interaction: Interaction, alias: str, old: SimpleTriggerData, data: str | None,
                           rate: int | None) -> None:
        self._console_log(
            f'[ TRIGGER EDIT]  by {interaction.user.display_name} ({interaction.user.id}) from Alias {alias}, Old: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}] ::to:: [Rate: {rate}; Data: {data}]',
            'edit_trigger')
        embed: Embed = Embed(
            title='Trigger edited',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'Type: {old.type}\n'
                        f'Data: {old.data}\n'
                        f'Rate: {old.rate}\n'
                        f'\n'
                        f'**New:**\n'
                        f'Data: {data if data is not None else '[ Not changed ]'}\n'
                        f'Rate: {rate if rate is not None else '[ Not changed ]'}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='edit_trigger')

    async def trigger_delete(self, interaction: Interaction, alias: str, old: SimpleTriggerData):
        self._console_log(
            f'[ TRIGGER DELETE ] by {interaction.user.display_name} ({interaction.user.id}) from Alias {alias} :: [Type: {old.type}; Rate: {old.rate}; Data: {old.data}]',
            'delete_trigger')
        embed: Embed = Embed(
            title='Trigger deleted',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'Type: {old.type}\n'
                        f'Data: {old.data}\n'
                        f'Rate: {old.rate}',
            colour=Colour.red()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='delete_trigger')

    # endregion
    # region reply
    async def reply_create(self, interaction: Interaction, alias: str, reply_type: reply_types, data: str,
                           weight: int | None):
        self._console_log(
            f'[ REPLY CREATE ] by {interaction.user.display_name} ({interaction.user.id}) to Alias {alias} :: [Type: {reply_type}; Weight: {weight}; Data: {data}]',
            'edit_reply')
        embed: Embed = Embed(
            title='Reply created',
            description=f'**Alias:** {alias}\n'
                        f'**New:**\n'
                        f'Type: {reply_type}'
                        f'Data: {data if data is not None else '[ Not changed ]'}\n'
                        f'Weight: {weight if weight is not None else '[ Not changed ]'}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='create_reply')

    async def reply_edit(self, interaction: Interaction, alias: str, old: SimpleReplyData, data: str | None,
                         weight: int | None):
        self._console_log(
            f'[ REPLY EDIT ] by {interaction.user.display_name} ({interaction.user.id}) from Alias {alias}, Old: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}] ::to:: [Weight: {weight}; Data: {data}]',
            'edit_reply')

        embed: Embed = Embed(
            title='Reply edited',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'Type: {old.type}\n'
                        f'Data: {old.data}\n'
                        f'Weight: {old.weight}\n'
                        f'\n'
                        f'**New:**\n'
                        f'Data: {data}\n'
                        f'Weight: {weight}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='edit_reply')

    async def reply_delete(self, interaction: Interaction, alias: str, old: SimpleReplyData):
        self._console_log(
            f'[ REPLY DELETE ] by {interaction.user.display_name} ({interaction.user.id}) from Alias {alias} :: [Type: {old.type}; Weight: {old.weight}; Data: {old.data}]',
            'delete_reply')
        embed: Embed = Embed(
            title='Reply deleted',
            description=f'**Alias:** {alias}\n'
                        f'**Old:**\n'
                        f'\tType: {old.type}\n'
                        f'\tData: {old.data}\n'
                        f'\tWeight: {old.weight}',
            colour=Colour.red()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='delete_reply')

    # endregion
    # endregion
    # region saying
    async def saying_create(self, interaction: Interaction, text: str):
        self._console_log(
            f'[ SAYING CREATE ] by {interaction.user.display_name} ({interaction.user.id}) :: {text}',
            'saying_create'
        )

        embed: Embed = Embed(
            title='Saying created',
            description=f'**New:**\n'
                        f'{text}',
            colour=Colour.green()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='saying_create')

    async def saying_edit(self, interaction: Interaction, old: SimpleSayingEditorData, text: str):
        self._console_log(
            f'[ SAYING EDIT ] by {interaction.user.display_name} ({interaction.user.id}) :: {old.text} ::to:: {text}',
            'saying_edit')

        embed: Embed = Embed(
            title='Saying edited',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}',
            colour=Colour.yellow()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='saying_edit')

    async def saying_delete(self, interaction: Interaction, old: SimpleSayingEditorData):
        self._console_log(
            f'[ SAYING DELETE ] by {interaction.user.display_name} ({interaction.user.id}) :: {old.text}',
            'saying_delete')

        embed: Embed = Embed(
            title='Saying deleted',
            description=f'**Old:**\n'
                        f'{old.text}',
            colour=Colour.red()
        )

        self._performed_by(embed, interaction)

        await self._channel_log(embed=embed, act='saying_delete')
    # endregion
    # endregion
