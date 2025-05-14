import random as _rd
import os as _os

from Managers.Exceptions import FactIndexError
from .json_tools import load_json as _lj, write_json as _wj

class FactsManager:
    def __init__(self, filepath: str):
        self.folderpath: str = filepath

    def _get_facts(self, guild_id: int | None) -> list[str]:
        filepath: str = f"{self.folderpath}/{guild_id if guild_id is not None else 'public'}.json"
        if not _os.path.exists(f"json_files/{filepath}"):
            self._add_guild(guild_id)
            return []
        return _lj(filepath)

    def _write_facts(self, guild_id: int | None, facts_dict: list[str]):
        filepath: str = f"{self.folderpath}/{guild_id if guild_id is not None else 'public'}.json"
        if not _os.path.exists(f"json_files/{filepath}"):
            self._add_guild(guild_id)
            return

        _wj(filepath, facts_dict)  # Todo: check all usages to see if updated parameter values are passed correctly.

    def get_facts(self, guild_id: int | None) -> list[str]:
        facts = self._get_facts(guild_id)
        return facts

    def get_fact(self, guild_id: int | None, index: int = None) -> str:
        facts = self.get_facts(None) + self.get_facts(guild_id) if guild_id is not None else self.get_facts(None)
        if index is None:
            return _rd.choice(facts)

        if not 0 <= index - 1 <= len(facts):
            raise FactIndexError(index)

        return facts[index - 1]

    def add_fact(self, fact: str, guild_id: int = None):
        facts = self._get_facts(guild_id)
        facts.append(fact)
        self._write_facts(guild_id, facts)

    def _add_guild(self, guild_id: int):
        _wj(f"{self.folderpath}/{guild_id if guild_id is not None else 'public'}.json", [])

    def get_index(self, guild_id: int | None, fact: str) -> int | None:
        gl, loc = self.get_facts(None), self.get_facts(guild_id)
        if guild_id is not None:
            return loc.index(fact) + 1 if fact in loc else None
        return gl.index(fact) + 1 if fact in gl else None

    def edit_fact(self, guild_id: int | None, index: int, new_fact: str):
        facts = self.get_facts(guild_id)
        if not 0 <= index - 1 < len(facts):
            raise IndexError(
                f"Index {index} is out of range for the list of facts! Check the amount of stored facts to see which indexes are valid.")
        facts[index - 1] = new_fact
        self._write_facts(guild_id, facts)

    def remove_fact(self, guild_id: int, index: int):
        facts = self._get_facts(guild_id)
        if not 0 <= index - 1 < len(facts):
            raise FactIndexError(index)

        del facts[index - 1]
        self._write_facts(guild_id, facts)
