from discord import Interaction, TextChannel, Guild, Embed, Colour, VoiceChannel, StageChannel, Thread, Member
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
            title='Fact created',
            description=f'**New:**\n'
                        f'{text}',
            colour=Colour.green()
        )
        if isinstance(interaction.user, Member):
            embed.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        await self._channel_log(interaction.guild, embed=embed, act='fact_create')

    async def fact_edit(self, interaction: Interaction, guild: Guild | None, old: SimpleFactEditorData, text: str, externally_modified: bool = False) -> None:
        """
        :param interaction: Interaction that caused this loggable event.
        :param guild: Guild the edit was for (so where it should be logged to)
        :param old: Old fact data
        :param text: New fact text data
        :param externally_modified:
        """
        embed: Embed = Embed(
            title='Fact edited',
            description=f'**Old:**\n'
                        f'{old.text}\n'
                        f'\n'
                        f'**New:**\n'
                        f'{text}',
            colour=Colour.yellow()
        )
        if externally_modified:
            embed.add_field(
                name='Externally modified',
                value='This action was performed externally by a global administrator.'
            )
            embed.colour = Colour.purple()

            # noinspection unresolved-references
            # Avatar available at runtime.
            embed.set_footer(
                text=f'Global Administrator',
                icon_url=self.client.user.display_avatar.url
            )
        elif isinstance(interaction.user, Member):
            embed.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        await self._channel_log(guild, embed=embed, act='fact_edit')

    async def fact_remove(self, interaction: Interaction, guild: Guild | None, old: SimpleFactEditorData, externally_modified: bool = False) -> None:
        embed: Embed = Embed(
            title='Fact removed',
            description=f'**Old:**\n'
                        f'{old.text}',
            colour=Colour.red()
        )
        if externally_modified:
            embed.add_field(
                name='Externally modified',
                value='This action was performed externally by a global administrator.'
            )
            embed.colour = Colour.dark_purple()

            # noinspection unresolved-references
            # Avatar available at runtime.
            embed.set_footer(
                text=f'Global Administrator',
                icon_url=self.client.user.display_avatar.url
            )
        elif isinstance(interaction.user, Member):
            embed.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        await self._channel_log(guild, embed=embed, act='fact_delete')

    async def set_log_channel(self, interaction: Interaction, channel: TextChannel | VoiceChannel | StageChannel | Thread) -> None:
        embed1: Embed = Embed(
            title='Log output channel changed',
            description=f'Log output moved to <#{channel.id}>',
            colour=Colour.default()
        )

        embed2: Embed = Embed(
            title='Log output channel changed',
            description=f'This channel has been set as the log output channel.',
            colour=Colour.default()
        )

        if isinstance(interaction.user, Member):
            embed1.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
            embed2.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed1.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
            embed2.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        await self._channel_log(interaction.guild, embed=embed1, act='set_log_channel')
        await channel.send(embed=embed2)

    async def set_channel_preferences(self, interaction: Interaction, channel: TextChannel | VoiceChannel | StageChannel | Thread | None, new: GuildChannelPreferenceData) -> None:
        # todo: implement!
        # Do not forget to figure out what kinds of channels require this; Probably just messageable channels? (See above)
        embed: Embed = Embed(
            title='Channel Autoreply preferences changed',
            description=f'**Preferences for** {'Server-wide override' if not channel else f'<#{channel.id}>'}\n'
                        f'\n'
                        f'Letter: **{new.letter}**\n'
                        f'Number: **{new.number}**\n'
                        f'Text: **{new.text}**\n'
                        f'Saying: **{new.saying}**',
            colour=Colour.default()
        )

        if isinstance(interaction.user, Member):
            embed.set_footer(
                text=f'{interaction.user.nick if interaction.user.nick else interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(
                text=f'{interaction.user.display_name} ({interaction.user.id})',
                icon_url=interaction.user.display_avatar.url
            )

        await self._channel_log(interaction.guild, embed=embed, act='set_channel_preferences')