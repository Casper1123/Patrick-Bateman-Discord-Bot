from typing import Literal, get_args
from Rewrite.configuration.abstract import AbstractJSONConfig

loggable = Literal['general', 'error',
    'local_fact_create', 'local_fact_edit', 'local_fact_delete',
    'local_log_channel_modify',

    'fact_create', 'fact_edit', 'fact_delete', 'fact_modify',
    'ban_user', 'ban_guild',

    'create_alias', 'edit_alias', 'delete_alias',
    'create_trigger', 'edit_trigger', 'delete_trigger',
    'create_reply', 'edit_reply', 'delete_reply',
]

class GlobalLoggerConfig(AbstractJSONConfig):
    def __init__(self, output_to_console: dict[loggable, bool], actively_logging: dict[loggable, bool], target_channels: dict[loggable, int], update_filepath: str):
        """
        Each dict requires exactly all, and no other, of the `loggable` properties to be set, otherwise it will raise an AssertionError.
        :param output_to_console: Should this loggable be printed to console?
        :param actively_logging: Should this loggable be sent into its respective channel?
        :param target_channels: Channel ids for actively logged actions. **WARNING:** If this channel is not found at runtime, the program will terminate with error code `1`.
        :param update_filepath: Target filepath of config file; used for updating values to storage.
        """
        super().__init__(update_filepath)

        # Validation of input
        validation: set[str] = set(get_args(loggable))
        # todo: this can be improved to tell which keys are missing.
        assert set(output_to_console.keys()) == validation, 'output_to_console must contain only and all loggables'
        assert set(actively_logging.keys()) == validation, 'actively_logging must contain only and all loggables'
        assert set(target_channels.keys()) == validation, 'target_channels must contain only and all loggables'

        self.output_to_console: dict[loggable, bool] = output_to_console
        self.actively_logging: dict[loggable, bool] = actively_logging
        self.target_channels: dict[loggable, int] = target_channels

        self.update_filepath: str = update_filepath

    def update_target_channel(self, act: loggable, target_id: int):
        self.target_channels[act] = target_id
        self.update_config_json()

    def to_json(self) -> dict[str, dict[str, ...]]:
        """
        Returns JSON-parsable version of this class instance.
        """
        return {
            'output_to_console': self.output_to_console,
            'actively_logging': self.actively_logging,
            'target_channels': self.target_channels,
        }
