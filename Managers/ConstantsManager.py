from .FactsManager import FactsManager
from .ReplyManager import ReplyManager
from .SayingsManager import SayingsManager
from .json_tools import load_json


class ConstantsManager:
    def __init__(self):
        constants = load_json("constants.json")
        self._bot_token: str = constants["token"]
        self.facts_manager: FactsManager = FactsManager("facts")
        self.reply_manager: ReplyManager = ReplyManager("autoreplies.json")
        self.sayings: SayingsManager = SayingsManager("sayings.json")

        self.global_edits_server_ids: list[int] = constants["global_edits_server_id"]
        self.super_server_ids: list[int] = constants["super_server_ids"]
