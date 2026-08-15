from utilities.exceptions import CustomDiscordException, ErrorTooltip


class InstructionParseError(CustomDiscordException):
    def __init__(self, bad_var: str, reason: str | None = None, tooltip: ErrorTooltip = ErrorTooltip.WIKI):
        self.bad_var: str = bad_var
        self.reason: str | None = reason
        super().__init__(message=f'Could not parse **{bad_var}**{f"\n**Reason:**\n{reason}" if reason else ""}',
                         tooltip=tooltip)