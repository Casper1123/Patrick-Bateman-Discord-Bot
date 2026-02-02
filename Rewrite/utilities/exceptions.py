from discord import Embed

from Rewrite.variables_parser import Instruction


def exception_as_embed(err: Exception) -> Embed:
    embed = Embed(
        title="An error has occurred.",
        description=f"If this issue persists, feel free to report it on [the issues page](<https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/issues>).\n"
                    f"\n"
                    f"**{type(err)}:**\n"
                    f"{err.__str__()}",
    )
    return embed

class CustomDiscordException(Exception):
    """
    Template exception which includes simple visualisation for user-feedback.
    """
    def __init__(self, message: str = None, cause: Exception | None = None, error_type: str | None = None) -> None:
        self.error_type = error_type if error_type else type(self).__name__  # Should work through inheritance, right?
        self.message = message
        self.cause = cause
        super().__init__(self.message)

    def as_embed(self) -> Embed:
        embed = Embed(
            title=self.error_type,
            description=f"**An error has occurred.**\n"
                        f"If this issue persists, feel free to report it on [the development's issues page](<https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/issues>).\n"
                        f"{f'\n**Error:**\n{self.message}' if self.message else ''}"
                        f"{'\n\n**Caused by:**' + type(self.cause).__name__ + '\n' + str(self.cause) if self.cause else ''}",
        )
        return embed

    def __str__(self) -> str:
        return f'{self.error_type}: {self.message} caused by {self.cause}'