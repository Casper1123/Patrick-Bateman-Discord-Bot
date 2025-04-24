from discord import app_commands


class ObjectIndexError(app_commands.AppCommandError):
    def __init__(self, index: int, obj_type: str):
        self.message = f"Index {index} is out of range for the list of {obj_type}s. Check the amount of stored {obj_type}s to see which indexes are valid."
        self.index = index
        super().__init__()

    def __str__(self):
        return self.message
    def __int__(self):
        return self.index

class FactIndexError(ObjectIndexError):
    def __init__(self, index: int):
        super().__init__(index, "fact")

class SayingIndexError(ObjectIndexError):
    def __init__(self, index: int):
        super().__init__(index, "saying")
