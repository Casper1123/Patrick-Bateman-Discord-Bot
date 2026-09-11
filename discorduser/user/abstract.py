import asyncio
import sys
from asyncio import Task

import discord
from discord import Colour, Interaction, Message
from discord.app_commands import TransformerError, AppCommandError
from discord.ext import commands

from configuration.logger import LocalLoggerConfig, GlobalLoggerConfig
from data.implementation.utilities.caching import RecursiveCacheHandler
from data.interfaces.autoreplies import GlobalTextAutoreplyInterface
from data.interfaces.fact import GlobalAdminFactInterface
from data.interfaces.moderation import GlobalAdminModerationInterface
from data.interfaces.other import LocalAdminDataInterface
from data.interfaces.pref import PreferencesInterface
from data.interfaces.saying import GlobalAdminSayingInterface
from discorduser.logger import GlobalLogger, LoggableErrorContext
from discorduser.logger.errors import ListenerErrorContext, AppCommandErrorContext, \
    AutocompleteErrorContext, TaskErrorContext, TransformerErrorContext
from discorduser.logger.local import LocalLogger


class BotClient(commands.Bot):
    """
    Bot-inherited class with toolkit installed.
    WARNING: DOES NOT CONTAIN COGS.
    """

    def __init__(self, error_cache_timeout: float, global_logger_config: GlobalLoggerConfig, local_logger_config: LocalLoggerConfig,
                 autoreplies: GlobalTextAutoreplyInterface, fact: GlobalAdminFactInterface,
                 mod: GlobalAdminModerationInterface, db: LocalAdminDataInterface, pref: PreferencesInterface,
                 saying: GlobalAdminSayingInterface) -> None:
        self._error_cache_timeout: float = error_cache_timeout
        self.logger: GlobalLogger = GlobalLogger(self, global_logger_config)
        self.local_logger: LocalLogger = LocalLogger(self, local_logger_config, db)
        self.autoreplies: GlobalTextAutoreplyInterface = autoreplies
        self.fact: GlobalAdminFactInterface = fact
        self.mod: GlobalAdminModerationInterface = mod
        self.db: LocalAdminDataInterface = db
        self.pref: PreferencesInterface = pref
        self.saying: GlobalAdminSayingInterface = saying

        intents: discord.Intents = discord.Intents.default()
        # IDK why PyCharm decided this does not exist, as it does.
        # Anyhows, this will unfortunately have to do.

        # noinspection dunder-slots,unresolved-references
        intents.message_content = True  # Required for autoreplies

        # noinspection dunder-slots,unresolved-references
        intents.members = True # Required for random users in PISS

        super().__init__(command_prefix="?dev", intents=intents, help_command=None)

        async def on_error(event, *args, **kwargs):
            error = sys.exc_info()[1]
            if error is None:
                return

            if not isinstance(error, Exception):
                raise error

            params: tuple[tuple[str, str], ...] = (('?', '?',),)

            if event == '':
                event = 'No event name provided'
            elif event == 'on_message':
                message: Message = args[0]
                params = (
                    ('message_id', str(message.id)),
                    ('channel_id', str(message.channel.id)),
                    ('author_id', str(message.author.id)),
                    ('message_content', message.content),
                )

            error_ctx = ListenerErrorContext(
                    error=error,
                    event=event,
                    params=params
                )
            await self.handle_exception(
                error_context=error_ctx)

        self.on_error = on_error

        # Error logging cooldown cache.
        self._error_cooldown_cache: RecursiveCacheHandler = RecursiveCacheHandler()

    def _get_cache_task(self) -> asyncio.Task:
        return asyncio.create_task(
            name=f'!!! Client error cache maintenance !!!',
            coro=self._error_cooldown_cache.maintenance_loop(
                timeout=self._error_cache_timeout,
                clean_empty_nodes=True,
            )
        )

    # region error-handling
    async def setup_hook(self) -> None:
        async def on_tree_error(interaction: Interaction, error: AppCommandError):
            # noinspection broad-exception
            try:
                await interaction.response.defer(ephemeral=True, thinking=False)
            except Exception:  #  Shoddy attempt at hiding the error from users.
                pass
            # handle exceptions
            finally:
                context: LoggableErrorContext

                # Modify contexts for better feedback formatting for logger
                if isinstance(error, TransformerError):
                    context = TransformerErrorContext(error, interaction)
                else:
                    context = AppCommandErrorContext(error=error, interaction=interaction)

                await self.handle_exception(context)

        self.tree.on_error = on_tree_error

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        error_cache_task: asyncio.Task = self._get_cache_task()
        error_cache_task.add_done_callback(self.handle_task_done)

        try:
            await super().start(token=token, reconnect=reconnect)
        finally:
            error_cache_task.cancel()

            await asyncio.gather(
                error_cache_task,
                return_exceptions=True,
            )

    async def handle_exception(self, error_context: LoggableErrorContext) -> None:
        if isinstance(error_context, AutocompleteErrorContext):
            error_context.log = False  # FUUUUUCK I gotta find a timeout for this or a reason to mute it. Cool the tech exists, but now what.

        if error_context.log:
            if not self._error_cooldown_cache.is_cached(
                keys=(
                        type(error_context).__name__,
                        error_context.error.__class__.__name__,
                )
            ):

                self._error_cooldown_cache.register(
                    keys=(type(error_context).__name__, error_context.error.__class__.__name__,),
                    timeout=10,
                    val=True
                )

                await self.logger.error(error_context)

        if isinstance(error_context, AppCommandErrorContext):
            await error_context.interaction.edit_original_response(embed=error_context.error.as_embed())

    def handle_task_done(self, task: asyncio.Task) -> None:
        """
        Pass a Task into this to handle whenever it ends or crashes.
        Passes crashing exception down to the Logger and Error handler.
        """
        if task.cancelled():
            return

        error: BaseException | None = task.exception()

        if error is None:
            return

        async def handle_exception():
            await self.handle_exception(
                TaskErrorContext(error, task)
            )
            import sys
            print(f'Closing application due to task error in task {task.get_name()}')
            asyncio.get_event_loop().stop()
            sys.exit(1)

        asyncio.create_task(
            handle_exception()
        )

    # endregion

    # noinspection method-may-be-static
    async def user_feedback(self, interaction: Interaction | discord.Message, title: str | None = None, desc: str | None = None,
                            ephemeral: bool = False) -> None:
        """
        Sends the following title and (optional) description in a standardized embed to the user.
        :param interaction: Interaction or Message to reply to.
        :param title: Title of the embed.
        :param desc: Text body of the embed.
        :param ephemeral: If Interaction, ephemeral?
        """
        e = discord.Embed(title=title, description=desc, colour=Colour.blue())
        if isinstance(interaction, Interaction):
            try:
                await interaction.response.send_message(embed=e, ephemeral=ephemeral)
            except discord.InteractionResponded:
                await interaction.edit_original_response(embed=e)  # ephemeral not supported.
        else:
            await interaction.reply(embed=e, mention_author=False)
