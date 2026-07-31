from typing import Literal, get_args

from abstract import AbstractJSONConfig

loggable = Literal['fact_create', 'fact_edit', 'fact_delete', 'set_log_channel']

class LocalLoggerConfig(AbstractJSONConfig):
    def __init__(self, actively_logging: dict[loggable, bool], update_filepath: str):
        super().__init__(update_filepath)
        validation: set[str] = set(get_args(loggable))
        # todo: this can be improved to tell which keys are missing.
        assert set(actively_logging.keys()) == validation, 'actively_logging must contain only and all loggables'

        self.actively_logging: dict[loggable, bool] = actively_logging

    def to_json(self) -> dict:
        return {
            'local_actively_logging': self.actively_logging
        }