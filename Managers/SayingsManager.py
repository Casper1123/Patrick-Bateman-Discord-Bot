import random as _rd

from Managers.Exceptions import SayingIndexError
from .json_tools import load_json as _lj, write_json as _wj


class SayingsManager:
    def __init__(self, filepath: str):
        self.filepath: str = filepath

    def get_lines(self) -> list[str]:
        return _lj(self.filepath)

    def _write_lines(self, lines: list[str]):
        _wj(self.filepath, lines)

    def get_line(self, index: int | None) -> str:
        lines: list[str] = self.get_lines()

        if index is None:
            return _rd.choice(lines)

        if not 0 <= index - 1 <= len(lines):
            raise SayingIndexError(index)

        return lines[index - 1]

    def add_line(self, line: str):
        lines = self.get_lines()
        lines.append(line)
        self._write_lines(lines)

    def get_index(self, line: str) -> int | None:
        lines = self.get_lines()
        return lines.index(line) + 1 if line in lines else None

    def edit_line(self, index: int, line: str):
        lines = self.get_lines()
        if not 0 <= index - 1 < len(lines):
            raise SayingIndexError(index)

        lines[index - 1] = line
        self._write_lines(lines)

    def remove_line(self, index: int):
        lines = self.get_lines()

        if not 0 <= index - 1 < len(lines):
            raise SayingIndexError(index)

        del lines[index - 1]
        self._write_lines(lines)

    def get_sayings_words(self) -> list[str]:
        output = []
        lines_lower = [i.lower() for i in self.get_lines()]
        for line in lines_lower:
            for word in line.split():
                if word not in output:
                    output.append(word)

        return output
