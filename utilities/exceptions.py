from enum import Enum

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
            # Traceback walkdown
            assert isinstance(self.cause, Exception), f'cause of type {type(self.cause)}, not exception.'
            tb = self.cause.__traceback__

            while tb.tb_next:
                tb = tb.tb_next

            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            function = frame.f_code.co_name
            line = tb.tb_lineno

            cause += f"\nRaised in {filename}:{line} ({function})"

        embed = Embed(
            title=self.error_type,
            description=f"**An error has occurred.**\n"
                        f"{_tooltips[self.tooltip]}"
                        f"{f'\n**Error:**\n{self.message}' if self.message else ''}"
                        f"{cause}",
            colour=Colour.red()
        )
        return embed

    def __str__(self) -> str:
        return f'{self.error_type}: {self.message}{f"\nCaused by {self.cause}" if self.cause else ''}'.replace('*', '')