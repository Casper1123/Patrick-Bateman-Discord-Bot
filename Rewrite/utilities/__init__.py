import json as _json

def load_json(filename: str) -> dict | list:
    with open(f"json_files/{filename}", "r") as cj:
        return _json.load(cj)


def write_json(filename: str, cj_dict: dict | list[str | float | int], sort_keys: bool = False, indent: int | None = None):
    with open(f"json_files/{filename}", "w") as cj:
        _json.dump(cj_dict, cj, sort_keys=sort_keys, indent=indent)


import tomli_w as _tomli
import tomllib as _tomllib
from datetime import datetime as _datetime, date as _date


def write_toml(path: str, data: dict[str, str | int | float | bool | list | dict | _datetime | _date], multiline: bool = True, indent: int | None = 4):
    with open(path, "wb") as f:
        f.write(_tomli.dumps(data, multiline_strings=multiline, indent=indent).encode())

def load_toml(path: str):
    with open(path, "rb") as f:
        return _tomllib.load(f)


# Configuration file building
def build():
    ...