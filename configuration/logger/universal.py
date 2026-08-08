from typing import Literal, get_args

from configuration.abstract import AbstractJSONConfig

loggable = Literal['general', 'error',
    'local_fact_create', 'local_fact_edit', 'local_fact_delete',
    'local_log_channel_modify',

    'fact_create', 'fact_edit', 'fact_delete', 'fact_modify',
    'ban_user', 'ban_guild',

    'create_alias', 'edit_alias', 'delete_alias',
    'create_trigger', 'edit_trigger', 'delete_trigger',
    'create_reply', 'edit_reply', 'delete_reply',

    'saying_create', 'saying_edit', 'saying_delete',
]

class GlobalLoggerConfig(AbstractJSONConfig):
    def __init__(self, output_to_console: dict[loggable, bool], actively_logging: dict[loggable, bool],
                 target_channels: dict[loggable, int], update_filepath: str):
        """
        Each dict requires exactly all, and no other, of the `loggable` properties to be set, otherwise it will raise a ValueError.
        :param output_to_console: Should this loggable be printed to console?
        :param actively_logging: Should this loggable be sent into its respective channel?
        :param target_channels: Channel ids for actively logged actions. **WARNING:** If this channel is not found at runtime, the program will terminate with error code `1`.
        :param update_filepath: Target filepath of logger file; used for updating values to storage.
        """
        super().__init__(update_filepath)

        # Validation of input
        validation: set[loggable] = set(get_args(loggable))
        output_to_console_keys_set: set[loggable] = set(output_to_console.keys())
        if not output_to_console_keys_set == validation:
            raise ValueError(
                f'output_to_console must contain only and all loggables, currently missing {validation - output_to_console_keys_set} and includes unneeded {output_to_console_keys_set - validation}')

        actively_logging_keys_set: set[loggable] = set(actively_logging.keys())
        if not actively_logging_keys_set == validation:
            raise ValueError(
                f'actively_logging must contain only and all loggables, currently missing {validation - actively_logging_keys_set} and includes unneeded {actively_logging_keys_set - validation}')

        target_channels_keys_set: set[loggable] = set(target_channels.keys())
        if not target_channels_keys_set == validation:
            raise ValueError(
                f'target_channels must contain only and all loggables, currently missing {validation - target_channels_keys_set} and includes unneeded {target_channels_keys_set - validation}')

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
