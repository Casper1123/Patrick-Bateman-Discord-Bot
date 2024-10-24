from __future__ import annotations

import random as _rd

from . import json_tools as _js


class ReplyData:
    def __init__(self, manager: ReplyManager, alias: str, triggers: list[str], replies: list[ReplyDetails]):
        self._manager = manager
        self.alias: str = alias
        self.triggers: list[str] = triggers
        self.replies: list[ReplyDetails] = replies

    def get_reply(self) -> str | None:
        if not self.replies:
            return None

        replies: list[str] = []
        for i in self.replies:
            weight = _rd.randint(1, 100)
            if i.weight >= weight:
                replies.append(i.value)

        if replies:
            return _rd.choice(replies)
        return None

    def get_replies(self) -> list[str]:
        return [i.value for i in self.replies]


class ReplyDetails:
    def __init__(self, value: str, weight: int):
        self.value = value
        self.weight = weight


class ReplyManager:
    def __init__(self, global_filepath: str):
        self._global_filepath: str = global_filepath

    # File Management
    def _get_replies(self, ) -> dict[str] | list[str]:
        return _js.load_json(self._global_filepath)

    def _write_replies(self, replies: dict[str]):
        _js.write_json(self._global_filepath, replies)

    # Global
    # Checks
    def _alias_exists(self, alias: str) -> bool:
        return alias.lower() in self._get_replies().keys()

    def _create_alias(self, alias: str):
        data = self._get_replies()

        data[alias.lower()] = {
            "replies": [],
            "triggers": []
        }

        self._write_replies(data)

    # Add
    def add_alias(self, alias: str):
        if not self._alias_exists(alias):
            self._create_alias(alias)

    def add_reply(self, alias: str, reply: str, weight: int = None):
        if not self._alias_exists(alias):
            self._create_alias(alias)

        if weight is None:
            weight = 100
        elif weight < 0:
            weight = 0
        elif weight > 100:
            weight = 100

        data = self._get_replies()
        if reply not in [i["value"] for i in data[alias.lower()]["replies"]]:
            data[alias.lower()]["replies"].append({
                "value": reply,
                "weight": weight
            })
            self._write_replies(data)

    def add_trigger(self, alias: str, trigger: str):
        if not self._alias_exists(alias):
            self._create_alias(alias)

        data = self._get_replies()
        if trigger not in data[alias.lower()]["triggers"]:
            data[alias.lower()]["triggers"].append(trigger)
            self._write_replies(data)

    # Get
    def get_replies(self, alias: str) -> list[ReplyDetails]:
        if not self._alias_exists(alias):
            self._create_alias(alias)

        data = self._get_replies()
        return [ReplyDetails(i["value"], i["weight"]) for i in data[alias.lower()]["replies"]]

    def get_triggers(self, alias: str) -> list[str]:
        if not self._alias_exists(alias):
            self._create_alias(alias)

        data = self._get_replies()
        return data[alias.lower()]["triggers"]

    def get_aliases(self) -> list[ReplyData]:
        return [
            ReplyData(self, k, v["triggers"], [ReplyDetails(i["value"], i["weight"]) for i in v["replies"]]) for k, v in
            self._get_replies().items()
        ]

    def get_alias(self, alias: str) -> ReplyData:
        if not self._alias_exists(alias):
            self._create_alias(alias)

        data = self._get_replies()
        aliasdata = data[alias.lower()]
        return ReplyData(self, alias.lower(), aliasdata["triggers"],
                         [ReplyDetails(i["value"], i["weight"]) for i in aliasdata["replies"]])

    # Edit
    def edit_reply(self, alias: str, index: int, reply: str = None, weight: int = None):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return
        if not 1 <= index <= len(data[alias.lower()]["replies"]):
            return

        original_reply = data[alias.lower()]["replies"][index - 1].copy()

        data[alias.lower()]["replies"][index - 1] = {
            "value": reply if reply else original_reply["value"],
            "weight": weight if weight else original_reply["weight"]
        }

        self._write_replies(data)

    def edit_alias(self, alias: str, index: int, new_alias: str):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return
        if not 1 <= index <= len(data.keys()):
            return

        data[alias.lower()].copy()
        data[new_alias] = data[alias.lower()].copy()
        del data[alias.lower()]

        self._write_replies(data)

    def edit_trigger(self, alias: str, index: int, trigger: str):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return
        if not 1 <= index <= len(data[alias.lower()]["trigger"]):
            return

        data[alias.lower()]["triggers"][index - 1] = trigger
        self._write_replies(data)

    # Remove
    def remove_reply(self, alias: str, index: int):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return
        if not 1 <= index <= len(data[alias.lower()]["replies"]):
            return

        data[alias.lower()]["replies"].pop(index - 1)
        self._write_replies(data)

    def remove_alias(self, alias: str):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return

        del data[alias.lower()]
        self._write_replies(data)

    def remove_trigger(self, alias: str, index: int):
        data = self._get_replies()

        if alias.lower() not in data.keys():
            return
        if not 1 <= index <= len(data[alias.lower()]["triggers"]):
            return

        data[alias.lower()]["triggers"].pop(index - 1)
        self._write_replies(data)
