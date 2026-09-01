if __name__ == '__main__':
    import os
    from configuration.logger import from_json, build_config as build_logger_config
    from configuration.token import TokenConfig

    # Config build
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

    # This may create a global_config and close the application
    from data.interfaces.autoreplies import GlobalTextAutoreplyInterface
    from data.interfaces.fact import GlobalAdminFactInterface
    from data.interfaces.moderation import GlobalAdminModerationInterface
    from data.interfaces.other import LocalAdminDataInterface
    from data.interfaces.pref import PreferencesInterface
    from data.interfaces.saying import GlobalAdminSayingInterface
    from configuration.logger import GlobalLoggerConfig, LocalLoggerConfig

    from discorduser.user import BotClient

    if logger_created:
        import sys

        sys.exit(0)

    # Logger config
    global_logger_config: GlobalLoggerConfig
    local_logger_config: LocalLoggerConfig
    global_logger_config, local_logger_config = from_json(logger_cfg_fp)

    # Token config
    token_config: TokenConfig = TokenConfig.from_json(token_cfg_fp)

    # DB
    autoreplies: GlobalTextAutoreplyInterface = ...
    fact: GlobalAdminFactInterface = ...
    mod: GlobalAdminModerationInterface = ...
    db: LocalAdminDataInterface = ...
    pref: PreferencesInterface = ...
    saying: GlobalAdminSayingInterface = ...

    client = BotClient(global_logger_config, local_logger_config, autoreplies, fact, mod, db, pref, saying)

    # Not supported yet
    print('Exiting as upcoming code is not complete yet.\nThe application cannot run.')
    sys.exit(0)

    import asyncio
    async def main():
        from data.implementation.utilities.abstract import CachedAbstractSQLDatabase
        # Just for an example to myself for later
        dummy: CachedAbstractSQLDatabase

        maintenance_loops = [
            dummy.get_cache_task()
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
    asyncio.run(main())