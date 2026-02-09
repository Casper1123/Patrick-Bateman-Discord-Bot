from discord import Embed

SUPPORT_SERVER_INVITE: str = 'XNQwUHAbDh'  # storing invite suffix here. If anyone ever forks this, feel free to alter this.
# Explicitly not leaving url in here, for one for scrapers and for two for my mental wellbeing
#   (I'd rather make sure that the return is a Discord URL in case SOMEHOW memory gets fiddled with)
GITHUB_WIKI_URL: str = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki' # todo: config

class CustomDiscordException(Exception):
    """
    Template exception which includes simple visualisation for user-feedback.
    """
    def __init__(self, message: str = None, cause: Exception | None = None, error_type: str | None = None, refer_wiki: bool = False) -> None:
        self.error_type = error_type if error_type else type(self).__name__  # Should work through inheritance, right?
        self.message = message
        self.cause = cause
        self.refer_wiki = refer_wiki
        super().__init__(self.message)
    # note: Exception.__traceback__ exists, go look it up it's kinda silli :)

    def as_embed(self) -> Embed:
        embed = Embed(
            title=self.error_type,
            description=f"**An error has occurred.**\n"
                        f"{
                            'If this issue persists, feel free to report it on '
                            '[the development\'s issues page](<https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/issues>).\n'
                                if not self.refer_wiki else 
                            f'To find out more about this topic, either join [the support Discord](<https://discord.gg/{SUPPORT_SERVER_INVITE}>) or check out the [wiki](<{GITHUB_WIKI_URL}>).',
                        }"
                        f"{f'\n**Error:**\n{self.message}' if self.message else ''}"
                        f"{'\n\n**Caused by:**' + type(self.cause).__name__ + '\n' + str(self.cause) if self.cause else ''}",
        )
        return embed

    def __str__(self) -> str:
        return f'{self.error_type}: {self.message}{f"\nCaused by {self.cause}" if self.cause else ''}'.replace('*', '')