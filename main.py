if __name__ == '__main__':
    import os
    from configuration.logger import from_json, build_config as build_logger_config
    from configuration.token import TokenConfig

    # Config build
    print('Config setup')
    logger_cfg_fp = 'config/logger.json'
    token_cfg_fp = 'config/token.json'

    logger_created: bool = False
    if not os.path.exists(logger_cfg_fp):
        build_logger_config(logger_cfg_fp)
        print(f'Logger config built at {logger_cfg_fp}, please edit accordingly.')
        logger_created = True

    if not os.path.exists(token_cfg_fp):
        TokenConfig.build_config(token_cfg_fp)
        print(f'Token config built at {token_cfg_fp}, please edit accordingly.')
        logger_created = True

    # Imports CFG which may create a global_config and close the application
    from discorduser.user import BotClient

    if logger_created:
        import sys

        sys.exit(0)

    # Logger config
    print('LOGGER config')

    from configuration.logger import GlobalLoggerConfig, LocalLoggerConfig
    global_logger_config: GlobalLoggerConfig
    local_logger_config: LocalLoggerConfig

    global_logger_config, local_logger_config = from_json(logger_cfg_fp)

    # Token config
    print('TOKEN config')
    token_config: TokenConfig = TokenConfig.from_json(token_cfg_fp)

    # DB
    print('Database')
    from data.implementation.autoreplies import AutoreplyDatabase
    from data.implementation.fact import FactDatabase
    from data.implementation.moderation import ModerationDatabase
    from data.implementation.other import GeneralDatabase
    from data.implementation.pref import PreferencesDatabase
    from data.implementation.saying import SayingDatabase

    db_data_path: str = 'data/data/data.sql'
    db_user_path: str = 'data/data/user.sql'

    autoreplies = AutoreplyDatabase(db_data_path)
    fact = FactDatabase(db_data_path)
    mod = ModerationDatabase(db_user_path)
    db = GeneralDatabase(db_user_path)
    pref = PreferencesDatabase(db_user_path)
    saying = SayingDatabase(db_data_path)

    print('Client instance')
    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    import asyncio
    async def main():
        maintenance_loops = [
            # Method on CachedAbstractSQLDatabase
            autoreplies.get_cache_task(),
            fact.get_cache_task(),
            mod.get_cache_task(),
            db.get_cache_task(),
            pref.get_cache_task(),
            saying.get_cache_task(),
        ]

        for loop in maintenance_loops:
            loop.add_done_callback(client.handle_task_done)

        # Run the client, and then clean up after. Raise any leftover exceptions.
        try:
            await client.start(token=token_config.token)
        finally:
            for task in maintenance_loops:
                task.cancel()

            await asyncio.gather(
                *maintenance_loops,
                return_exceptions=True,
            )

    print('Starting')
    asyncio.run(main())