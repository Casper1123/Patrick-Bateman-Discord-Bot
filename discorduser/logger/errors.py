import traceback
from pathlib import Path
from typing import Literal, TypeAlias
from abc import ABC, abstractmethod

from discord import Embed, Interaction, Colour
from discord.app_commands import CommandOnCooldown, CommandInvokeError, TransformerError

from piss import InstructionParseError
from utilities.exceptions import CustomDiscordException, ErrorTooltip, RestrictedUseException

UNLOGGED_EXCEPTION_TYPES: list[type] = [
    InstructionParseError,
    CommandOnCooldown,
    RestrictedUseException,
]
# todo: undetailed exception types --> not sending exception warning to user, or just something generic
ErrorSource: TypeAlias = Literal['app_command', 'listener', 'task', 'autocomplete', 'transformer'] # just putting

def _normalize_exception(error: Exception) -> tuple[CustomDiscordException, bool]:
    """
    Normalize given Exception into a CustomDiscordException and tells if should be logged or not.
    :return: tuple[normalized exception, should log]
    """
    # Peel of its skin, if it has some on there.
    # Peel off it's skin.
    if isinstance(error, CommandInvokeError):
        error: Exception = error.original
    elif isinstance(error, TransformerError):
        error: Exception = error.__cause__ # noqa let's just suppress this hihi haha what could go wrong.

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
        error: CustomDiscordException # True by invariant above.
        if type(error) in UNLOGGED_EXCEPTION_TYPES:
            log = False
        else:
            log = error.cause is None or type(error.cause) not in UNLOGGED_EXCEPTION_TYPES
    return error, log

class LoggableErrorContext(ABC):
    def __init__(self, source: ErrorSource, error: Exception):
        self.source = source # So can be decided on this as opposed to isinstance(something, something)

        self.error: CustomDiscordException
        self.log: bool
        self.error, self.log = _normalize_exception(error)

        self._filename: str = '(Error not raised yet?)'
        self._lineno: int | None = 0
        self._name: str = ''

        tb_source: Exception = self.error.cause if isinstance(self.error.cause, Exception) and self.error.cause.__traceback__ else self.error
        if not tb_source.__traceback__:
            return

        tb = traceback.extract_tb(tb_source.__traceback__)[-1]
        def find_project_root(start: Path, max_depth: int = 5) -> Path:
            current = start.resolve()

            for _ in range(max_depth):
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

    @abstractmethod # Abstract to force thought about usage in each particular case.
    def as_embed(self) -> Embed:
        """
        Templated error embed with some basic styling.
        PURELY FOR LOGGING, FOR USER_FEEDBACK USE THE STANDARD CustomDiscordException.as_embed() !!!
        """
        embed: Embed = Embed(
            title=f'[[ ERROR ]] {self.error.error_type}',
            description='', # Left as emptystring on purpose.
            colour=Colour.red()
        )
        if self.error.message:
            embed.description += f'{self.error.message}\n\n'
        return embed

    @abstractmethod
    def as_console(self) -> str:
        """
        Templated console logging string.
        """
        return f'[[ ERROR ]] {self.error.error_type}{f' ({self.error.message})' if self.error.message else ''} from {self.source}:'

class AppCommandErrorContext(LoggableErrorContext):
    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()
        embed.description += (f'Raised by `/{self.interaction.command.qualified_name}`\n'
                              f'In *{self._name}* (`{self._filename}:{self._lineno}`)\n'
                              f'Given parameters: {self.params}')
        if self.error.cause: # noqa want flexibility
            embed.description += (f'\n\n'
                                  f'Caused by: {type(self.error.cause).__name__}\n'
                                  f'{self.error.cause}')
        embed.description += (f'\n\n'
                              f'Raised by: {self.interaction.user.display_name} ({self.interaction.id})')
        embed.set_author(name=self.interaction.user.name, icon_url=self.interaction.user.display_avatar.url)
        return embed

    def as_console(self) -> str:
        return super().as_console() + f'{self.interaction.command.qualified_name} at {self._filename}:{self._lineno} ({self._name}) with parameters {self.params} by user {self.interaction.user.display_name} ({self.interaction.user.id})'

    def __init__(self, error: Exception, interaction: Interaction, ):
        super().__init__('app_command', error)
        self.interaction = interaction
        try:
            self.params = f'[{'; '.join(f'{n} = {v}' for n, v in vars(self.interaction.namespace).items())}]'
        except TypeError:
            self.params = f'[]'

class ListenerErrorContext(LoggableErrorContext):
    def __init__(self, error: Exception, event: str, params: str):
        """
        :param event: Event name
        :param params: String of parameter data to be logged, passed in with the format [PARAM = VALUE; PARAM = VALUE]
        """
        super().__init__('listener', error)
        self.event = event
        self.params = params

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()
        if self.error.message:
            embed.description += f'{self.error.message}\n\n'
        embed.description += (f'Event type *{self.event}*\n'
                              f'In *{self._name}* (`{self._filename}:{self._lineno}`)\n'
                              f'Parameters: {self.params}')
        if self.error.cause:
            embed.description += (f'\n\n'
                                  f'Caused by: {type(self.error.cause).__name__}\n'
                                  f'{self.error.cause}')
        return embed

    def as_console(self) -> str:
        return super().as_console() + f'{self.event} at {self._filename}:{self._lineno} ({self._name}) with parameters {self.params}'

class TaskErrorContext(LoggableErrorContext):
    def __init__(self, error: Exception, task: str):
        super().__init__('task', error)
        self.task = task

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()
        embed.description += (f'In task {self.task}'
                              f'In: *{self._name}* (`{self._filename}:{self._lineno}`)')
        if self.error.cause:
            embed.description += (f'\n\n'
                                  f'Caused by: {type(self.error.cause).__name__}\n'
                                  f'{self.error.cause}')
        return embed

    def as_console(self) -> str:
        return super().as_console() + f'{self.task} at {self._filename}:{self._lineno} ({self._name})'

class AutocompleteErrorContext(LoggableErrorContext):
    # todo: definitely fucking
    def __init__(self, error: Exception, target: str, current: ..., interaction: Interaction):
        """
        :param target: Target parameter name
        :param current: Target parameter value.
        """
        super().__init__('autocomplete', error)
        self.target = target
        try:
            self.current = str(current)
        except: # noqa it's simple enough as is who gives a damn.
            self.current = '[PARSE ERROR]'
        self.interaction = interaction
        try:
            self.params = f'[{'; '.join(f'{n} = {v}' for n, v in vars(self.interaction.namespace).items() if v != target)}]'
        except TypeError: self.params = f'[]'

    def as_embed(self) -> Embed:
        embed: Embed = super().as_embed()
        embed.description += (
            f'Raised by `/{self.interaction.command.qualified_name}`\n'
            f'In: *{self._name}* (`{self._filename}:{self._lineno}`)\n'
            f'Target: {self.target} = {self.current}'
            f'Given parameters: {self.params}')
        if self.error.cause: # noqa dupe cuz want the flexibility
            embed.description += (f'\n\n'
                                  f'Caused by: {type(self.error.cause).__name__}\n'
                                  f'{self.error.cause}')
        embed.description += (f'\n\n'
                              f'Raised by: {self.interaction.user.display_name} ({self.interaction.id})')
        embed.set_author(name=self.interaction.user.name, icon_url=self.interaction.user.display_avatar.url)
        return embed

    def as_console(self) -> str:
        return super().as_console() + f'{self.interaction.command.qualified_name} at {self._filename}:{self._lineno} ({self._name}) with target [{self.target}={self.current}] and parameters {self.params} by user {self.interaction.user.display_name} ({self.interaction.user.id})'

# todo: transformer class.