import random as _rd

from .json_tools import load_json as _lj, write_json as _wj
from Managers.Exceptions import FactIndexError

class FactsManager:
    def __init__(self, filepath: str):
        self.filepath: str = filepath

    def _get_facts(self) -> dict[str] | list[str]:
        return _lj(self.filepath)

    def _write_facts(self, facts_dict: dict[str]):
        _wj(self.filepath, facts_dict)

    def get_facts(self, guild_id: int | None, seperate: bool = False) -> list[str] or (list[str], list[str]):
        self._check_guild_entry(guild_id)

        facts = self._get_facts()
        global_facts = facts["public"]
        local_facts = facts["private"][str(guild_id)] if guild_id is not None else []

        if seperate:
            return global_facts, local_facts
        return global_facts + local_facts

    def get_fact(self, guild_id: int | None, index: int = None) -> str:
        self._check_guild_entry(guild_id)

        # If index = None, random
        facts = self.get_facts(guild_id)
        if index is None:
            return _rd.choice(facts)

        if not 0 <= index - 1 <= len(facts):
            raise FactIndexError(f"Index {index} is out of range for the list of facts! Check the amount of stored facts to see which indexes are valid.")

        return facts[index-1]

    def add_fact(self, fact: str, guild_id: int = None):
        self._check_guild_entry(guild_id)

        facts = self._get_facts()
        facts["private"][str(guild_id)].append(fact)
        self._write_facts(facts)

    def add_global_fact(self, fact):
        facts = self._get_facts()
        facts["public"].append(fact)
        self._write_facts(facts)

    def _add_guild(self, guild_id: int):
        facts = self._get_facts()
        facts["private"][str(guild_id)] = []
        self._write_facts(facts)

    def _has_private_entry(self, guild_id: int | None) -> bool:
        if guild_id is None:
            return True  # Act as if it does for DM purposes.
        return str(guild_id) in self._get_facts()["private"].keys()

    def _check_guild_entry(self, guild_id: int | None):
        if not self._has_private_entry(guild_id):
            self._add_guild(guild_id)

    def get_index(self, guild_id: int | None, fact: str) -> int | None:
        gl, loc = self.get_facts(guild_id, seperate=True)
        if guild_id is not None:
            return loc.index(fact) + 1 if fact in loc else None
        return gl.index(fact) + 1 if fact in gl else None

    def edit_fact(self, guild_id: int, index: int, new_fact: str):
        facts = self._get_facts()
        local_facts = self.get_facts(guild_id)
        if not 0 <= index - 1 < len(local_facts):
            raise IndexError(
                f"Index {index} is out of range for the list of facts! Check the amount of stored facts to see which indexes are valid.")

        private = index > len(facts["public"])
        if not private:
            facts["public"][index-1] = new_fact
        else:
            index -= len(facts["public"])
            facts["private"][str(guild_id)][index-1] = new_fact
        self._write_facts(facts)

    def remove_fact(self, guild_id: int, index: int):
        facts = self._get_facts()
        local_facts = self.get_facts(guild_id)
        if not 0 <= index - 1 < len(local_facts):
            raise FactIndexError(
                f"Index {index} is out of range for the list of facts! Check the amount of stored facts to see which indexes are valid.")

        private = index > len(facts["public"])
        if not private:
            del facts["public"][index - 1]
        else:
            index -= len(facts["public"])
            del facts["private"][str(guild_id)][index-1]
        self._write_facts(facts)
