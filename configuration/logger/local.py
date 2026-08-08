from typing import Literal, get_args, TypeAlias

from configuration.abstract import AbstractJSONConfig

loggable: TypeAlias = Literal['fact_create', 'fact_edit', 'fact_delete', 'set_log_channel']


class LocalLoggerConfig(AbstractJSONConfig):
    def __init__(self, actively_logging: dict[loggable, bool], update_filepath: str):
        super().__init__(update_filepath)
        validation: set[loggable] = set(get_args(loggable))
        set_keys: set[loggable] = set(actively_logging.keys())
        if not set_keys == validation:
            raise ValueError(
                f'actively_logging must contain only and all loggables, currently missing {validation - set_keys} and includes unneeded {set_keys - validation}')

        self.actively_logging: dict[loggable, bool] = actively_logging

    def to_json(self) -> dict:
        return {
            'local_actively_logging': self.actively_logging
        }
