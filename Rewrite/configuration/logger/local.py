from typing import Literal, get_args

from Rewrite.configuration.abstract import AbstractJSONConfig

loggable = Literal['fact_create', 'fact_edit', 'fact_delete', 'set_log_channel']

class LocalLoggerConfig(AbstractJSONConfig):
    def __init__(self, actively_logging: dict[loggable, bool], update_filepath: str):
        super().__init__(update_filepath)
        validation: set[loggable] = set(get_args(loggable))
        assert set(actively_logging.keys()) == validation, f'actively_logging must contain only and all loggables, currently missing {validation - set(actively_logging.keys())} and includes unneeded {set(actively_logging.keys()) - validation}'

        self.actively_logging: dict[loggable, bool] = actively_logging

    def to_json(self) -> dict:
        return {
            'local_actively_logging': self.actively_logging
        }