from asyncio import Task
import traceback
from abc import ABC, abstractmethod, abstractproperty
from pathlib import Path
from typing import Literal, TypeAlias, Any

from discord import Embed, Interaction, Colour, Member, User, Guild
from discord.app_commands import CommandOnCooldown, CommandInvokeError, TransformerError

from piss.old import InstructionParseError
from utilities.exceptions import CustomDiscordException, ErrorTooltip, RestrictedUseException, IncompatibleTargetChannel

UNLOGGED_EXCEPTION_TYPES: tuple[type, ...] = (
    InstructionParseError,
    CommandOnCooldown,
    RestrictedUseException,
    IncompatibleTargetChannel,
)

ErrorSource: TypeAlias = Literal['app_command', 'listener', 'task', 'autocomplete', 'transformer']  # just putting


def _normalize_exception(error: BaseException) -> tuple[CustomDiscordException, bool]:
    """
    Normalize given Exception into a CustomDiscordException and tells if should be logged or not.
    :return: tuple[normalized exception, should log]
    """
    # Peel of its skin, if it has some on there.
    # Peel off it's skin.
    if isinstance(error, CommandInvokeError):
        error: Exception = error.original
    elif isinstance(error, TransformerError) and error.__cause__:
        error: Exception = error.__cause__  # noqa Documentation specifies to do so.

    # Todo: Go through and figure out which exceptions to the CDE-conversion are to be put here, just like CommandOnCooldown
    if isinstance(error, CommandOnCooldown):
        log = type(error) not in UNLOGGED_EXCEPTION_TYPES  # Leave logging to the above or not.
        error: CustomDiscordException = CustomDiscordException(
            message=f'Command on cooldown ({error.cooldown}s), try again in **{error.retry_after}s**.',
            error_type='Command on cooldown.', tooltip=ErrorTooltip.NONE)
    elif not isinstance(error, CustomDiscordException):
        log = type(error) not in UNLOGGED_EXCEPTION_TYPES
        error: CustomDiscordException = CustomDiscordException(cause=error, error_type=type(error).__name__)
    else:
        error: CustomDiscordException  # True by invariant above.
        if type(error) in UNLOGGED_EXCEPTION_TYPES:
            log = False
        else:
            log = error.cause is None or type(error.cause) not in UNLOGGED_EXCEPTION_TYPES
    return error, log

class LoggableErrorContext(ABC):
    def __init__(self, source: ErrorSource, error: BaseException,):
        self.source = source  # So can be decided on this as opposed to isinstance(something, something)

        self.error, self.log = _normalize_exception(error)
        self.error: CustomDiscordException
        self.log: bool

        self._filename: str = '(Error not raised yet?)'
        self._lineno: int | None = 0
        self._name: str = ''

        tb_source: Exception = self.error.cause if isinstance(self.error.cause,
                                                              Exception) and self.error.cause.__traceback__ else self.error
        if not tb_source.__traceback__:
            return

        tb = traceback.extract_tb(tb_source.__traceback__)[-1]

        def find_project_root(start: Path, max_depth: int = 5) -> Path:
            current = start.resolve()

            for _ in range(max_depth):
                # It'll be fine trust
                if (current / "main.py").exists():
                    return current
                if current.parent == current:
                    break
                current = current.parent

            return start.resolve()

        project_root = find_project_root(Path(tb.filename).parent)
        self._filename = str(Path(tb.filename).relative_to(project_root))
        self._lineno = tb.lineno
        self._name = tb.name

    @abstractproperty
    def cmd_context(self) -> str:
        """
        Console: [[ ERROR_SOURCE ERROR ]] error_source {context} raised ...
        """
        return '[NO ERROR CONTEXT GIVEN]'

    @abstractproperty
    def embed_context(self) -> str:
        """
        Mostly the same as console context, but can omit parameters.
        '[Task {taskname}] raised an error.\n
        _fileline stuff'
        """
        return '[NO ERROR CONTEXT GIVEN]'

    def as_embed(self) -> Embed:
        embed: Embed = Embed(
            title=f'[[ {self.source.upper()} ERROR ]]',
            description=
            f'{self.embed_context} raised an error.\n'
            f'`{self._filename}`:*{self._lineno}* {self._name}',
            colour=Colour.red()
        )

        if self.error.message:
            embed.add_field(
                name=f'Error',
                value=f'{f'**{self.error.error_type}**\n' if self.error.error_type != CustomDiscordException.__name__ else ''}'
                      f'{self.error.message}',
                inline=False
            )

        if self.error.cause:
            embed.add_field(
                name=f'Cause',
                value=f'**{type(self.error.cause).__name__}**\n'
                      f'{self.error.cause}',
                inline=False
            )

        return embed

    def as_console(self) -> str:
        """
        Templated console logging string.
        """
        return f'[[ {self.source.upper()} ERROR ]] {self.source} {self.cmd_context} raised {'an error' if not self.error.error_type == CustomDiscordException.__name__ else f'{self.error.error_type}'} at {self._filename}:{self._lineno} ({self._name}){f' ({self.error.message})' if self.error.message else ''}{'' if not self.error.cause else f' caused by {type(self.error.cause).__name__}{f': {self.error.cause}' if str(self.error.cause) else ''}'}'

class LoggableInteractionErrorContext(LoggableErrorContext, ABC):
    def __init__(self, source: ErrorSource, error: Exception, interaction: Interaction):
        super().__init__(source, error)
        self.interaction = interaction

        try:
            self._raw_params: list[tuple[str, Any]] = [(n, v) for n, v in vars(self.interaction.namespace).items()]
        except TypeError:
            self._raw_params = []

        # todo: do some postprocessing s.t. things become parsable based on input seen.

        self.params = f'[{'; '.join(f'{n} = {v}' for n, v in self._raw_params)}]'

        self._include_params_field_in_embed: bool = True

    @property
    def _interaction_cmd_context_helper(self) -> str:
        return f'{f'/{self.interaction.command.qualified_name}' if self.interaction.command else '???'} with params {self.params}'

    @property
    def _interaction_embed_context_helper(self) -> str:
        return f' /{self.interaction.command.qualified_name}' if self.interaction.command else ''

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()

        if isinstance(self.interaction.user, Member):
            embed.set_footer(
                text=f'{self.interaction.user.nick if self.interaction.user.nick else self.interaction.user.display_name} ({self.interaction.user.id})',
                icon_url=self.interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(
                text=f'{self.interaction.user.display_name} ({self.interaction.user.id})',
                icon_url=self.interaction.user.display_avatar.url
            )

        if self._include_params_field_in_embed:
            embed.add_field(
                name='Parameters',
                value='\n'.join(f'{n} = {v}' for n, v in self._raw_params),
                inline=False
            )

        if self.interaction.guild is not None:
            try:
                # noinspection unresolved-references
                embed.set_author(
                    name=f'{self.interaction.guild.name} ({self.interaction.guild.id})',
                    icon_url=self.interaction.guild.icon.url,
                )
            except AttributeError:
                # noinspection unresolved-references
                embed.set_author(
                    name=f'{self.interaction.guild.name} ({self.interaction.guild.id})',
                )

        return embed


class ListenerErrorContext(LoggableErrorContext):
    @property
    def embed_context(self) -> str:
        return f'{self.event} listener'

    @property
    def cmd_context(self) -> str:
        return f'{self.event} with params [{'; '.join(f'{n}={v}' for n, v in self.params)}]'

    def __init__(self, error: Exception, event: str, params: tuple[tuple[str, str], ...], author: User | Member | None = None, guild: Guild | None = None):
        """
        :param event: Event name
        :param params: Tuple of (name, value) pairs.
        :param author: User or Member object to optionally give extra info.
        :param guild: Guild object to optionally give extra info.
        """
        super().__init__('listener', error)
        self.event = event
        self.params = params

        self.author = author
        self.guild = guild

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()

        embed.add_field(
            name='Parameters',
            value='\n'.join(f'{n} = {v}' for n, v in self.params),
            inline=False
        )

        if self.author is not None:
            embed.set_footer(
                text=f'{self.author.display_name} ({self.author.id})',
                icon_url=self.author.display_avatar.url
            )
        if self.guild is not None:
            try:
                # noinspection unresolved-references
                embed.set_author(
                    name=f'{self.guild.name} ({self.guild.id})',
                    icon_url=self.guild.icon.url
                )
            except AttributeError:
                embed.set_author(
                    name=f'{self.guild.name} ({self.guild.id})',
                )

        return embed


class TaskErrorContext(LoggableErrorContext):
    @property
    def embed_context(self) -> str:
        return f'Task {self.task.get_name()}'

    @property
    def cmd_context(self) -> str:
        return f'{self.task.get_name()}'

    def __init__(self, error: BaseException, task: Task):
        super().__init__('task', error)
        self.task: Task = task


class AppCommandErrorContext(LoggableInteractionErrorContext):
    @property
    def embed_context(self) -> str:
        return f'App Command{self._interaction_embed_context_helper}'

    @property
    def cmd_context(self) -> str:
        # for app_command /blablabla
        return self._interaction_cmd_context_helper

    def __init__(self, error: Exception, interaction: Interaction, ):
        super().__init__('app_command', error, interaction)


class AutocompleteErrorContext(LoggableInteractionErrorContext):
    @property
    def embed_context(self) -> str:
        return f'Autocomplete{f' for command {self._interaction_embed_context_helper}' if self._interaction_embed_context_helper else ''}'

    @property
    def cmd_context(self) -> str:
        return f'for command {self._interaction_cmd_context_helper} with target parameter {self.target} ({self.current}) and params {self.params}'

    def __init__(self, error: Exception, target: str, current: Any, interaction: Interaction):
        """
        :param target: Target parameter name
        :param current: Target parameter value.
        """
        super().__init__('autocomplete', error, interaction)
        self.target = target

        try:
            self.current = str(current)
        except:  # noqa it's simple enough as is who gives a damn.
            self.current = '[PARSE ERROR]'

        self._include_params_field_in_embed = False

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()

        embed.add_field(
            name='Parameters',
            inline=False,
            value=f'**Target:**\n'
                  f'{self.target} = {self.current}\n'
                  f'\n'
                  f'**Others:**\n'
                  f'{'\n'.join(f'{n} = {v}' for n, v in self.params)}'
        )

        return embed


class TransformerErrorContext(LoggableInteractionErrorContext):
    @property
    def embed_context(self) -> str:
        return f'Transformer {type(self._original_error.transformer).__name__}{f' for command {self._interaction_embed_context_helper}' if self._interaction_embed_context_helper else ''}'

    @property
    def cmd_context(self) -> str:
        return f'{type(self._original_error.transformer).__name__} with input {self._original_error.value} for command {self._interaction_cmd_context_helper}'

    def __init__(self, error: TransformerError, interaction: Interaction):
        super().__init__('transformer', error, interaction)
        self._original_error: TransformerError = error

        self._include_params_field_in_embed = False

        if type(self.error.cause) == ValueError:
            # This error is returned when invalid input is supplied.
            # Thus, we do not log it.
            self.log = False

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()

        embed.add_field(
            name='Parameters',
            inline=False,
            value=f'**Input:**\n'
                  f'{self._original_error.value}\n'
                  '\n'
                  f'**Others:**\n'
                  f'{'\n'.join(f'{n} = {v}' for n, v in self.params)}'
        )

        return embed