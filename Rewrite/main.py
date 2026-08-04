import os
import sys

from Rewrite.configuration.token import TokenConfig, build_
from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface
from Rewrite.data.interfaces.fact import GlobalAdminFactInterface
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface
from Rewrite.data.interfaces.other import GlobalAdminDataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface
from Rewrite.discorduser.logger import GlobalLoggerConfig, LocalLoggerConfig
from Rewrite.discorduser.logger.config import from_json, build_config as build_logger_config
from Rewrite.discorduser.user import BotClient

if __name__ == '__main__':
    # Config build
    logger_config_fp = 'config/logger.json'
    token_fp = 'config/tokens.json'

    logger_created: bool = False
    if not os.path.exists(logger_config_fp):
        build_logger_config(logger_config_fp)
        print('Logger config built, please edit accordingly.')
        logger_created = True

    if not os.path.exists(token_fp):
        TokenConfig.build_config(token_fp)
        print('Token config built, please edit accordingly.')
        logger_created = True

    if logger_created:
        sys.exit(0)

    # Logger config
    global_logger_config: GlobalLoggerConfig
    local_logger_config: LocalLoggerConfig
    global_logger_config, local_logger_config = from_json(logger_config_fp)

    # Token config
    token_config: TokenConfig = TokenConfig.from_json(token_fp)

    # DB
    autoreplies: GlobalTextAutorepliesInterface = ...
    fact: GlobalAdminFactInterface = ...
    mod: GlobalAdminModerationInterface = ...
    db: GlobalAdminDataInterface = ...
    pref: PreferencesInterface = ...
    saying: GlobalAdminSayingInterface = ...


    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    client.run(token=token_config.main)