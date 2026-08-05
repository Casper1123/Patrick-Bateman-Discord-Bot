import os
import sys

from Rewrite.configuration.token import TokenConfig
from Rewrite.data.interfaces.autoreplies import GlobalTextAutorepliesInterface
from Rewrite.data.interfaces.fact import GlobalAdminFactInterface
from Rewrite.data.interfaces.moderation import GlobalAdminModerationInterface
from Rewrite.data.interfaces.other import LocalAdminDataInterface
from Rewrite.data.interfaces.pref import PreferencesInterface
from Rewrite.data.interfaces.saying import GlobalAdminSayingInterface
from Rewrite.discorduser.logger import GlobalLoggerConfig, LocalLoggerConfig
from Rewrite.discorduser.user import BotClient
from Rewrite.testing.config import TestGlobalLoggerConfig, TestLocalLoggerConfig
from Rewrite.testing.data.autoreplies import TestAutoreplyDatabase
from Rewrite.testing.data.fact import TestFactDatabase
from Rewrite.testing.data.moderation import TestModerationDatabase
from Rewrite.testing.data.other import TestGeneralDatabase
from Rewrite.testing.data.pref import TestPreferencesDatabase
from Rewrite.testing.data.saying import TestSayingDatabase

if __name__ == '__main__':
    token_cfg_fp = 'config/tokens.json'

    logger_created: bool = False

    if not os.path.exists(token_cfg_fp):
        TokenConfig.build_config(token_cfg_fp)
        print(f'Token config built at {token_cfg_fp}, please edit accordingly.')
        logger_created = True

    if logger_created:
        sys.exit(0)

    # Logger config
    global_logger_config: GlobalLoggerConfig = TestGlobalLoggerConfig()
    local_logger_config: LocalLoggerConfig = TestLocalLoggerConfig()

    # Token config
    token_config: TokenConfig = TokenConfig.from_json(token_cfg_fp)

    # DB
    autoreplies: GlobalTextAutorepliesInterface = TestAutoreplyDatabase()
    fact: GlobalAdminFactInterface = TestFactDatabase()
    mod: GlobalAdminModerationInterface = TestModerationDatabase(user_banned=False, banned_guild=False, super_guild=False)
    db: LocalAdminDataInterface = TestGeneralDatabase(test_output_channel_id=None, super_guilds=[]) # Put ids in here!
    pref: PreferencesInterface = TestPreferencesDatabase(text=True, number=True, letter=True)
    saying: GlobalAdminSayingInterface = TestSayingDatabase()

    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    client.run(token=token_config.test)