import json as _json


def load_json(filename: str) -> dict | list:
    with open(f"json_files/{filename}", "r") as cj:
        return _json.load(cj)


def write_json(filename: str, cj_dict: dict | list[str | float | int], sort_keys: bool = False):
    with open(f"json_files/{filename}", "w") as cj:
        _json.dump(cj_dict, cj, indent=4, sort_keys=sort_keys)
