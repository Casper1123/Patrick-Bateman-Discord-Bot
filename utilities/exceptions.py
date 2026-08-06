from enum import Enum
import traceback

from discord import Embed, Colour

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
    """
    Template exception which includes simple visualisation for user-feedback.
    """
    def __init__(self, message: str = None, cause: Exception | None = None, error_type: str | None = None, tooltip: ErrorTooltip = ErrorTooltip.ISSUE) -> None:
        self.error_type: str = error_type if error_type else type(self).__name__  # Should work through inheritance, right?
        self.message: str | None = message
        self.cause: Exception | None = cause
        self.tooltip: ErrorTooltip = tooltip

        super().__init__(self.message)

    def as_embed(self) -> Embed:
        cause = ''
        if self.cause:
            cause = (f'\n\n**Caused by:** {type(self.cause).__name__}\n'
                     f'{self.cause}')

        embed = Embed(
            title=self.error_type,
            description=f"**An error has occurred.**\n"
                        f"{_tooltips[self.tooltip]}"
                        f"{f'\n\n**Error:**\n{self.message}' if self.message else ''}"
                        f"{cause}",
            colour=Colour.red()
        )
        return embed

    def __str__(self) -> str:
        return f'{self.error_type}: {self.message}{f"\n**Caused by:**\n{self.cause}" if self.cause else ''}'.replace('*', '')

class UseRestriction(Enum):
    NONE = 0,
    GUILD = 1,
    USER = 2,

    FACT_LIMIT = 4
    CHAR_LIMIT = 5

reasons: dict[UseRestriction, str] = {
        UseRestriction.NONE: 'An unlisted external reason has prevented you from performing this action. Seeing this usually means you\'re an outlier or something went wrong on our side.',
        UseRestriction.GUILD: 'This guild has been restricted from using this feature.',
        UseRestriction.USER: 'You cannot use this feature.',

        UseRestriction.FACT_LIMIT: 'This guild has hit the maximum number of Facts. Remove some to make space.',
        UseRestriction.CHAR_LIMIT: 'Your input was too long.'
    }

class RestrictedUseException(CustomDiscordException):
    def __init__(self, restriction: UseRestriction):
        super().__init__(message=f'Your action has been interrupted; ' + reasons[restriction], tooltip=ErrorTooltip.NONE) # todo: write on the wiki what's going on when you see this

    def as_embed(self) -> Embed:
        embed = super().as_embed()
        embed.title = 'Access denied'
        return embed