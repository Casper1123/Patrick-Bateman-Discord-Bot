from discord import app_commands


class FactIndexError(app_commands.AppCommandError):
    def __init__(self, message: str):
        self.message = message
        super().__init__()

    def __str__(self):
        return self.message
