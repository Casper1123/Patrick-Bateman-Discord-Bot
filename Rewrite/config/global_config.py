# File contains a bunch of universally used datapoints.
# Leaving this here, implemented this way, until I find a better solution.

# Local
    # Url to where information on PISS-debugger output can be found.
_DEBUGGER_OUTPUT_WIKI_URL: str = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'
_SUPPORT_SERVER_INVITE: str = 'XNQwUHAbDh'  # storing invite suffix here. If anyone ever forks this, feel free to alter this.
# Explicitly not leaving url in here, for one for scrapers and for two for my mental wellbeing
#   (I'd rather make sure that the return is a Discord URL in case SOMEHOW memory gets fiddled with)
_GITHUB_ISSUES_URL: str = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/issues'
_GITHUB_WIKI_URL: str = 'https://github.com/Casper1123/Patrick-Bateman-Discord-Bot/wiki'

# Just used everywhere, wanna be consistent.
_EPHEMERAL_DESCRIPTION: str = 'Hide this command from other users.'


# Made to run when imported to ensure that it's created.
# Has some more local and variable stuff, but permanent stuff that I want synced with Git will be included above and assigned to the class itself.

from Rewrite.configuration.abstract import AbstractJSONConfig
class _GlobalConfig(AbstractJSONConfig):
    def __init__(self, path: str, global_admin_serverid: int, reply_weight_upper_bound: int,
                 local_fact_max: int, local_fact_charlimit: int,
                 preview_cd: float, delete_cd: float, edit_cd: float, add_cd: float,
                 fact_cd: float,
                 saying_probability: int):
        super().__init__(path)

        assert isinstance(global_admin_serverid, int)
        assert isinstance(reply_weight_upper_bound, int)

        assert isinstance(local_fact_max, int)
        assert isinstance(local_fact_charlimit, int)

        assert isinstance(preview_cd, float) or isinstance(preview_cd, int)
        assert isinstance(delete_cd, float) or isinstance(delete_cd, int)
        assert isinstance(edit_cd, float) or isinstance(edit_cd, int)
        assert isinstance(add_cd, float) or isinstance(add_cd, int)

        assert isinstance(fact_cd, float) or isinstance(fact_cd, int)
        assert isinstance(saying_probability, int)

        self.GLOBAL_ADMIN_SERVER_ID: int = global_admin_serverid
        self.REPLY_WEIGHT_UPPER_BOUND: int = reply_weight_upper_bound

        self.FACT_COUNT_MAXIMUM: int = local_fact_max
        self.FACT_CHAR_LIMIT: int = local_fact_charlimit

        self.PREVIEW_COOLDOWN_SECONDS: float = preview_cd
        self.DELETE_COOLDOWN_SECONDS: float = delete_cd
        self.EDIT_COOLDOWN_SECONDS: float = edit_cd
        self.ADD_COOLDOWN_SECONDS: float = add_cd

        self.FACT_COOLDOWN: float = fact_cd
        self.SAYING_PROBABILIY: int = saying_probability

        # Git synced permanent.
        self.DEBUGGER_OUTPUT_WIKI_URL = _DEBUGGER_OUTPUT_WIKI_URL
        self.SUPPORT_SERVER_INVITE = _SUPPORT_SERVER_INVITE
        self.GITHUB_ISSUES_URL = _GITHUB_ISSUES_URL
        self.GITHUB_WIKI_URL = _GITHUB_WIKI_URL
        self.EPHEMERAL_DESCRIPTION = _EPHEMERAL_DESCRIPTION


    def to_json(self) -> dict:
        return {
            'GLOBAL_ADMIN_SERVER_ID': self.GLOBAL_ADMIN_SERVER_ID,
            'REPLY_WEIGHT_UPPER_BOUND': self.REPLY_WEIGHT_UPPER_BOUND,

            'FACT_COUNT_MAXIMUM': self.FACT_COUNT_MAXIMUM,
            'FACT_CHAR_LIMIT': self.FACT_CHAR_LIMIT,

            'PREVIEW_COOLDOWN_SECONDS': self.PREVIEW_COOLDOWN_SECONDS,
            'DELETE_COOLDOWN_SECONDS': self.DELETE_COOLDOWN_SECONDS,
            'EDIT_COOLDOWN_SECONDS': self.EDIT_COOLDOWN_SECONDS,
            'ADD_COOLDOWN_SECONDS': self.ADD_COOLDOWN_SECONDS,

            'FACT_COOLDOWN': self.FACT_COOLDOWN,
            'SAYING_PROBABILIY': self.SAYING_PROBABILIY,
        }

    @staticmethod
    def build_config(path: str):
        from Rewrite.utilities import write_json
        defaults: dict[str, ...] = {
            'GLOBAL_ADMIN_SERVER_ID': None, # Mandate manually setting this value.
            'REPLY_WEIGHT_UPPER_BOUND': 1024,

            'FACT_COUNT_MAXIMUM': 50,
            'FACT_CHAR_LIMIT': 256,

            'PREVIEW_COOLDOWN_SECONDS': 5.0,
            'DELETE_COOLDOWN_SECONDS': 5.0,
            'EDIT_COOLDOWN_SECONDS': 5.0,
            'ADD_COOLDOWN_SECONDS': 5.0,

            'FACT_COOLDOWN': 1.0,
            'SAYING_PROBABILIY': 300, # 1 / probability listed here, per message.
        }
        write_json(path, defaults, sort_keys=False, indent=4)

    @staticmethod
    def from_json(path: str) -> '_GlobalConfig':
        from Rewrite.utilities import load_json
        cfg = load_json(path)
        # Values
        GAD_SID = cfg['GLOBAL_ADMIN_SERVER_ID']
        REPL_W_UP = cfg['REPLY_WEIGHT_UPPER_BOUND']
        FACT_COUNT_MAX = cfg['FACT_COUNT_MAXIMUM']
        FACT_CHAR_LIMIT = cfg['FACT_CHAR_LIMIT']
        PREVIEW_CD = cfg['PREVIEW_COOLDOWN_SECONDS']
        DELETE_CD = cfg['DELETE_COOLDOWN_SECONDS']
        EDIT_CD = cfg['EDIT_COOLDOWN_SECONDS']
        ADD_CD = cfg['ADD_COOLDOWN_SECONDS']
        FACT_COOLDOWN = cfg['FACT_COOLDOWN']
        SAYING_PROBABILIY = cfg['SAYING_PROBABILIY']

        return _GlobalConfig(path, GAD_SID, REPL_W_UP, FACT_COUNT_MAX, FACT_CHAR_LIMIT, PREVIEW_CD, DELETE_CD, EDIT_CD, ADD_CD, FACT_COOLDOWN, SAYING_PROBABILIY)

import os as _os

_cfg_fp: str = 'config/global.json'

if not _os.path.exists(_cfg_fp):
    _GlobalConfig.build_config(_cfg_fp)
    print(f'Global config built at {_cfg_fp}, please edit accordingly.')
    import sys
    sys.exit(0)

# To be imported by other files.
CFG: _GlobalConfig = _GlobalConfig.from_json(_cfg_fp)