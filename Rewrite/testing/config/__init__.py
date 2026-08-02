from typing import get_args

from Rewrite.discorduser.logger import GlobalLoggerConfig, LocalLoggerConfig
from Rewrite.discorduser.logger.config.universal import loggable
from Rewrite.discorduser.logger.config.local import loggable as local_loggable


class TestGlobalLoggerConfig(GlobalLoggerConfig):
    def __init__(self):
        otc, al, tc, = {}, {}, {}
        for k in get_args(loggable):
            otc[k] = True
            al[k] = False
            tc[k] = 0

        super().__init__(
            output_to_console=otc,
            actively_logging=al,
            target_channels=tc,
            update_filepath=None
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
            update_filepath=None
        )

    def update_config_json(self):
        pass