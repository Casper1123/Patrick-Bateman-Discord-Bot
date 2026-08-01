import os
import sys

from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface
from Rewrite.data.interfaces.fact import GlobalAdminFactInterface
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface
from Rewrite.data.interfaces.other import GlobalAdminDataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface
from Rewrite.discorduser.logger import GlobalLogger, GlobalLoggerConfig, LocalLoggerConfig
from Rewrite.discorduser.logger.config import from_json, build_config
from Rewrite.discorduser.logger.local import LocalLogger
from Rewrite.discorduser.user import BotClient

if __name__ == '__main__':
    # Loggers
    ## Logger config
    config_fp = 'configuration/config.json'
    if not os.path.exists(config_fp):
        build_config(config_fp)
        print('Config built, please edit accordingly.')
        sys.exit()

    global_logger_config: GlobalLoggerConfig # TODO: CIRCULAR IMPORT FIX (SOME PARTS REQUIRE CLIENT)
    local_logger_config: LocalLoggerConfig
    global_logger_config, local_logger_config = from_json(config_fp)

    # DB
    autoreplies: GlobalTextAutorepliesInterface = ...
    fact: GlobalAdminFactInterface = ...
    mod: GlobalAdminModerationInterface = ...
    db: GlobalAdminDataInterface = ...
    pref: PreferencesInterface = ...
    saying: GlobalAdminSayingInterface = ...


    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    TOKEN = '' # TODO: TOKEN LOADING
    client.run(token=TOKEN)