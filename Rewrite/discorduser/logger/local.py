from discord import Interaction, TextChannel, Guild, Embed, Colour

from Rewrite.data.interfaces.fact import FactEditorData
from Rewrite.data.interfaces.other import LocalAdminDataInterface
from config.local import LocalLoggerConfig, loggable


class LocalLogger:
    def __init__(self, config: LocalLoggerConfig, db: LocalAdminDataInterface):
        self.config = config
        self.db = db

    def _get_log_channel(self, guild: Guild) -> TextChannel | None:
        res = self.db.get_log_channel(guild.id)
        if res is None:
            return None
        channel = guild.get_channel(res)
        if channel is None:
            self.db.set_log_output(guild.id, None) # Do this to prevent the call of get_channel getting used for no reason.
            return None
        return channel

    # region log out
    # todo: buffer messages for x seconds and then send one thing with multiple embeds in one go to prevent ratelimiting?
    async def _channel_log(self, guild: Guild, embed: Embed, act: loggable) -> None:
        if self.config.actively_logging[act]:
            channel: TextChannel = self._get_log_channel(guild)
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

    async def fact_edit(self, interaction: Interaction, old: FactEditorData, text: str) -> None:
        embed: Embed = Embed(
            title='[FACT_EDIT]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}\n'
                        f'Edited by: {interaction.user.name} ({interaction.user.id})',
            colour=Colour.yellow()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(interaction.guild, embed=embed, act='fact_edit')

    async def fact_remove(self, interaction: Interaction, old: FactEditorData) -> None:
        embed: Embed = Embed(
            title='[FACT_REMOVE]',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'Removed by: {interaction.user.name} ({interaction.user.id})',
            colour=Colour.red()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(interaction.guild, embed=embed, act='fact_delete')

    async def set_log_channel(self, interaction: Interaction, channel: TextChannel) -> None:
        embed: Embed = Embed(
            title='[LOG_CHANNEL_MOVE]',
            description=f'**New channel:**:\n'
                        f'<#{channel.id}> ({channel.name} / {channel.id})\n'
                        f'Set by: {interaction.user.name} ({interaction.user.id})',
            colour=Colour.blue()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await self._channel_log(interaction.guild, embed=embed, act='set_log_channel')