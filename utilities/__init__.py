import json as _json

def load_json(filename: str) -> dict | list:
    with open(f"json_files/{filename}", "r") as cj:
        return _json.load(cj)


def write_json(filepath: str, cj_dict: dict | list[str | float | int], sort_keys: bool = False, indent: int | None = None):
    with open(f"{filepath}", "w") as cj:
        _json.dump(cj_dict, cj, sort_keys=sort_keys, indent=indent)

