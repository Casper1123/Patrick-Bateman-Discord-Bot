if __name__ == '__main__':
    import os
    from configuration.token import TokenConfig

    token_cfg_fp = 'config/test_token.json'

    logger_created: bool = False

    if not os.path.exists(token_cfg_fp):
        TokenConfig.build_config(token_cfg_fp)
        print(f'Token config built at {token_cfg_fp}, please edit accordingly.')
        logger_created = True

    # This may create a global_config and close the application
    from data.interfaces.autoreplies import GlobalTextAutoreplyInterface
    from data.interfaces.fact import GlobalAdminFactInterface
    from data.interfaces.moderation import GlobalAdminModerationInterface
    from data.interfaces.other import LocalAdminDataInterface
    from data.interfaces.pref import PreferencesInterface
    from data.interfaces.saying import GlobalAdminSayingInterface
    from configuration.logger import GlobalLoggerConfig, LocalLoggerConfig
    from discorduser.user import BotClient
    from testing.config import TestGlobalLoggerConfig, TestLocalLoggerConfig
    from testing.data.autoreplies import TestAutoreplyDatabase
    from testing.data.fact import TestFactDatabase
    from testing.data.moderation import TestModerationDatabase
    from testing.data.other import TestGeneralDatabase
    from testing.data.pref import TestPreferencesDatabase
    from testing.data.saying import TestSayingDatabase

    if logger_created:
        import sys

        sys.exit(0)

    # Logger config
    global_logger_config: GlobalLoggerConfig = TestGlobalLoggerConfig(output_channel_id=None)
    local_logger_config: LocalLoggerConfig = TestLocalLoggerConfig()

    # Token config
    token_config: TokenConfig = TokenConfig.from_json(token_cfg_fp)

    # DB
    autoreplies: GlobalTextAutoreplyInterface = TestAutoreplyDatabase()
    fact: GlobalAdminFactInterface = TestFactDatabase()
    mod: GlobalAdminModerationInterface = TestModerationDatabase(user_banned=False, banned_guild=False,
                                                                 super_guild=False)
    db: LocalAdminDataInterface = TestGeneralDatabase(test_output_channel_id=None, super_guilds=[])  # Put ids in here!
    pref: PreferencesInterface = TestPreferencesDatabase(text=True, number=True, letter=True)
    saying: GlobalAdminSayingInterface = TestSayingDatabase()

    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    client.run(token=token_config.token)
