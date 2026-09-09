import types
from abc import ABC, abstractmethod
from typing import Any, get_origin, get_args, Union

from utilities import load_json, write_json


class AbstractJSONConfig(ABC):
    """
    Abstract json-maintainable configuration class.
    Basically just allows updating own data into given json file at path.
    """

    def __init__(self, update_filepath: str):
        self.update_filepath = update_filepath

    @abstractmethod
    def to_json(self) -> dict:
        """
        Returns own data as JSON-parsable dict.
        """
        raise NotImplementedError()

    def update_config_json(self):
        """
        Writes own JSON-data to update filepath.
        """
        js = self.to_json()
        cfg = load_json(self.update_filepath)
        for k, v in js.items():
            cfg[k] = v
        write_json(self.update_filepath, cfg)

    @staticmethod
    def check_attributes(d: dict[str, Any], wanted: tuple[tuple[str, type, Any], ...]) -> bool:
        """
        Checks input dict d for wanted keys and typechecks corresponding values.
        Mutates d if a key is missing.
        :param d: input dict, will be mutated.
        :param wanted: tuple of (name, target_type (can be generic), default)
        :return: Have new entries been made?
        """

        def matches_type(value: Any, expected: Any) -> bool:
            origin = get_origin(expected)

            # Plain runtime class, e.g. A
            if origin is None:
                return isinstance(value, expected)

            args = get_args(expected)

            if origin is types.UnionType or origin is Union:
                return any(matches_type(value, arg) for arg in args)

            if origin is list:
                return (
                        isinstance(value, list)
                        and all(matches_type(item, args[0]) for item in value)
                )

            if origin is dict:
                key_type, value_type = args
                return (
                        isinstance(value, dict)
                        and all(
                    matches_type(k, key_type)

                    and matches_type(v, value_type)
                    for k, v in value.items()
                )
                )

            try:
                # noinspection bad-argument-type
                return isinstance(value, origin)
            except TypeError:
                return isinstance(value, expected)

        new_entries: bool = False

        for entry in wanted:
            name, target_type, default = entry
            try:
                val = d[name]
            except KeyError:
                print(f'Creating missing entry {name} with default value {default}')
                d[name] = default
                new_entries = True
                continue

            if not matches_type(val, target_type):
                raise TypeError(f'{name} of type {type(val).__name__} does not match {target_type} (or did not match generics)')

        return new_entries