from typing import Any

from discord import Interaction, TextChannel, Guild, Embed, Colour, VoiceChannel, StageChannel, Thread
from discord.abc import Messageable
from discord.ext import commands

from configuration.logger.local import LocalLoggerConfig, loggable
from data.interfaces.fact import SimpleFactEditorData
from data.interfaces.other import LocalAdminDataInterface
from data.interfaces.pref import GuildChannelPreferenceData


class LocalLogger:
    def __init__(self, client: commands.Bot, config: LocalLoggerConfig, db: LocalAdminDataInterface):
        self.client = client
        self.config = config
        self.db = db

    def _get_log_channel(self, guild: Guild) -> Messageable | None:
        if not guild:
            return None
        res = self.db.get_log_channel(guild.id)
        if res is None:
            return None
        channel = guild.get_channel(res)
        if not isinstance(channel, Messageable):
            self.db.set_log_output(guild.id,
                                   None)  # Do this to prevent the call of get_channel getting used for no reason.
            return None
        return channel

    # region log out
    # todo: buffer messages for x seconds and then send one thing with multiple embeds in one go to prevent ratelimiting?
    async def _channel_log(self, guild: Guild | None, embed: Embed, act: loggable) -> None:
        if not guild:
            return

        if self.config.actively_logging[act]:
            channel: Messageable | None = self._get_log_channel(guild)
            if channel:
                await channel.send(embed=embed)

    # endregion

    async def fact_create(self, interaction: Interaction, text: str) -> None:
        embed: Embed = Embed(
            title='[FACT_CREATE]',
            description=f'{text}\n'
                        f'Created by: {interaction.user.name} ({interaction.user.id})',
            colour=Colour.green()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(interaction.guild, embed=embed, act='fact_create')

    async def fact_edit(self, interaction: Interaction, guild: Guild | None, old: SimpleFactEditorData, text: str, externally_modified: bool = False) -> None:
        embed: Embed = Embed(
            title='[FACT_EDIT]',
            colour=Colour.yellow()
        )

        description: str = (f'**Old:**\n'
                            f'{old.text}\n'
                            f'\n'
                            f'**New:**\n'
                            f'{text}')

        if not externally_modified:
            description += f'\nEdited by: {interaction.user.name} ({interaction.user.id})'
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        else:
            description += f'\nExternally modified by a Global staff member.'
            # noinspection unresolved-references
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.id)

        embed.description = description
        await self._channel_log(guild, embed=embed, act='fact_edit')

    async def fact_remove(self, interaction: Interaction, guild: Guild | None, old: SimpleFactEditorData, externally_modified: bool = False) -> None:
        embed: Embed = Embed(
            title='[FACT_REMOVE]',
            colour=Colour.red()
        )

        description: str = (f'**Old:**\n'
                            f'{old.text}\n')

        if not externally_modified:
            description += f'\n\nRemoved by: {interaction.user.name} ({interaction.user.id})'
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        else:
            description += f'\n\nExternally modified by a Global staff member.'
            # noinspection unresolved-references
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.id)

        embed.description = description
        await self._channel_log(guild, embed=embed, act='fact_delete')

    async def set_log_channel(self, interaction: Interaction, channel: TextChannel | VoiceChannel | StageChannel | Thread) -> None:
        embed: Embed = Embed(
            title='[LOG_CHANNEL_MOVE]',
            description=f'**New channel:**:\n'
                        f'<#{channel.id}> ({channel.name} / {channel.id})\n'
                        f'Set by: {interaction.user.name} ({interaction.user.id})',
            colour=Colour.blue()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(interaction.guild, embed=embed, act='set_log_channel')

    async def set_channel_preferences(self, interaction: Interaction, channel: Any, new: GuildChannelPreferenceData) -> None:
        # todo: implement!
        # Do not forget to figure out what kinds of channels require this; Probably just messageable channels? (See above)
        pass