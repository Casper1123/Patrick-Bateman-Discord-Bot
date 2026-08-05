from typing import get_args

from configuration.logger import GlobalLoggerConfig, LocalLoggerConfig
from configuration.logger.local import loggable as local_loggable
from configuration.logger import loggable


class TestGlobalLoggerConfig(GlobalLoggerConfig):
    def __init__(self):
        otc, al, tc, = {}, {}, {}
        for k in get_args(loggable):
            otc[k] = True
            al[k] = False
            tc[k] = 0 # Values are fine as al[k] being False means it never checks for the channel.
            # Or at least, it should never.
            # Because if it does, it will crash. Good test, huh.

        super().__init__(
            output_to_console=otc,
            actively_logging=al,
            target_channels=tc,
            update_filepath=None # noqa Never used as long as we override all its use cases. Which there is only one.
        )

    def update_config_json(self):
        pass

class TestLocalLoggerConfig(LocalLoggerConfig):
    def __init__(self):
        al = {}
        for k in get_args(local_loggable):
            al[k] = False

        super().__init__(
            actively_logging=al,
            update_filepath=None # noqa
        )

    def update_config_json(self):
        pass