# Main config, either server specific or global.
class Configuration:
    def __init__(self, global_config_path: str, local_config_directory_path: str):
        # Load global config. Exclude client token.
        ...