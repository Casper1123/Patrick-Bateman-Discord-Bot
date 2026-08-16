from enum import Enum
from typing import Any

from discord import Embed, Colour, ForumChannel, CategoryChannel, DMChannel, \
    GroupChannel, PartialMessageable

from configuration.global_config import CFG


class ErrorTooltip(Enum):
    NONE = 0
    ISSUE = 1
    WIKI = 2


# Tooltip to description translation. No repeated allocation at local runtime.
_tooltips: dict[ErrorTooltip, str] = {
    ErrorTooltip.NONE: '',
    ErrorTooltip.ISSUE: 'If this issue persists, feel free to report it on '
                        f'[the development\'s issues page](<{CFG.GITHUB_ISSUES_URL}>).',
    ErrorTooltip.WIKI: f'To find out more about this topic, either join [the support Discord](<https://discord.gg/{CFG.SUPPORT_SERVER_INVITE}>) or check out the [wiki](<{CFG.GITHUB_WIKI_URL}>).',
}


class CustomDiscordException(Exception):
    def __init__(self, message: str | None = None, cause: BaseException | None = None, error_type: str | None = None,
                 tooltip: ErrorTooltip = ErrorTooltip.ISSUE) -> None:
        self.error_type: str = error_type if error_type else type(
            self).__name__  # Should work through inheritance, right?
        self.message: str | None = message
        self.cause: BaseException | None = cause
        self.tooltip: ErrorTooltip = tooltip

        super().__init__(self.message)

    def as_embed(self) -> Embed:
        """
        Returns an embed for user-feedback purposes.
        """
        cause = ''
        # todo: remake. Keep in mind it's user-feedback only.
        if self.cause:
            cause = (f'\n'
                     f'\n'
                     f'**Caused by:** {type(self.cause).__name__}\n'
                     f'{self.cause}')

        embed = Embed(
            title=self.error_type,
            description=f"**An error has occurred.**\n"
                        f"{_tooltips[self.tooltip]}"
                        f"{f'\n'
                           f'**Error:**\n'
                           f'{self.message}' if self.message else ''}"
                        f"{cause}",
            colour=Colour.red()
        )
        return embed


# todo: make Literal TypeAlias?
class UseRestriction(Enum):
    NONE = 0,
    GUILD = 1,
    USER = 2,

    FACT_LIMIT = 4
    CHAR_LIMIT = 5


reasons: dict[UseRestriction, str] = {
    UseRestriction.NONE: 'An unlisted internal reason has prevented you from performing this action. Seeing this usually means you\'re an outlier or something went wrong on our side.',
    UseRestriction.GUILD: 'This guild has been restricted from using this feature.',
    UseRestriction.USER: 'You cannot use this feature.',

    UseRestriction.FACT_LIMIT: f'This guild has hit the maximum number of Facts. Remove some to make space, as you may only have {CFG.FACT_COUNT_MAXIMUM}.',
    UseRestriction.CHAR_LIMIT: f'Your input was too long. It was longer than {CFG.FACT_CHAR_LIMIT} characters.',
}


class RestrictedUseException(CustomDiscordException):
    def __init__(self, restriction: UseRestriction):
        super().__init__(message=f'Your action has been interrupted; ' + reasons[restriction],
                         tooltip=ErrorTooltip.NONE)  # todo: write on the wiki what's going on when you see this

    def as_embed(self) -> Embed:
        embed = super().as_embed()
        embed.title = 'Access denied'
        return embed

class IncompatibleTargetChannel(CustomDiscordException):
    def __init__(self, target_channel: ForumChannel | CategoryChannel | DMChannel | GroupChannel | PartialMessageable |None, target: str):
        super().__init__(message=f'Channel id {target_channel.id if target_channel is not None else 'NONE'} with type {type(target_channel)} is not {target}.',
                         tooltip=ErrorTooltip.ISSUE) # Should only be raised in weird edge cases.

    def as_embed(self) -> Embed:
        embed = super().as_embed()
        return embed


class BadTransformerInput(CustomDiscordException):
    def __init__(self, to_from: tuple[type, type], curr: Any, cause: BaseException | None = None, tooltip: ErrorTooltip = ErrorTooltip.NONE):
        super().__init__(message=f'Could not transform {to_from[0].__name__} to {to_from[1].__name__} with given input `{curr}`', cause=cause, tooltip=tooltip)