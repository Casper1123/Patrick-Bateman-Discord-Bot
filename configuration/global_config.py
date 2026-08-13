# File contains a bunch of universally used datapoints.
# Leaving this here, implemented this way, until I find a better solution.
from typing import Any

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

from configuration.abstract import AbstractJSONConfig


class _GlobalConfig(AbstractJSONConfig):
    def __init__(self, path: str, global_admin_serverid: int, reply_weight_upper_bound: int,
                 local_fact_max: int, local_fact_charlimit: int,
                 preview_cd: float, delete_cd: float, edit_cd: float, add_cd: float,
                 channel_pause_duration: int,
                 fact_cd: float,
                 saying_probability: int):
        super().__init__(path)

        if not isinstance(global_admin_serverid, int) or global_admin_serverid is None:
            raise TypeError('global_admin_serverid must be an int')
        if not isinstance(reply_weight_upper_bound, int) or reply_weight_upper_bound is None:
            raise TypeError('reply_weight_upper_bound must be an int')

        if not isinstance(local_fact_max, int) or local_fact_max is None:
            raise TypeError('local_fact_max must be an int')
        if not isinstance(local_fact_charlimit, int) or local_fact_charlimit is None:
            raise TypeError('local_fact_charlimit must be an int')

        if not (isinstance(preview_cd, float) or isinstance(preview_cd, int)) or preview_cd is None:
            raise TypeError('preview_cd must be a float or int')
        if not (isinstance(delete_cd, float) or isinstance(delete_cd, int)) or delete_cd is None:
            raise TypeError('delete_cd must be a float or int')
        if not (isinstance(edit_cd, float) or isinstance(edit_cd, int)) or edit_cd is None:
            raise TypeError('edit_cd must be a float or int')
        if not (isinstance(add_cd, float) or isinstance(add_cd, int)) or add_cd is None:
            raise TypeError('add_cd must be a float or int')

        if not (isinstance(channel_pause_duration, float) or isinstance(channel_pause_duration,
                                                                        int)) or channel_pause_duration is None:
            raise TypeError('channel_pause_duration must be a float or int')

        if not (isinstance(fact_cd, float) or isinstance(fact_cd, int)) or fact_cd is None:
            raise TypeError('fact_cd must be a float or int')
        if not isinstance(saying_probability, int) or saying_probability is None:
            raise TypeError('saying_probability must be an int')

        self.GLOBAL_ADMIN_SERVER_ID: int = global_admin_serverid
        self.REPLY_WEIGHT_UPPER_BOUND: int = reply_weight_upper_bound

        self.FACT_COUNT_MAXIMUM: int = local_fact_max
        self.FACT_CHAR_LIMIT: int = local_fact_charlimit

        self.PREVIEW_COOLDOWN_SECONDS: float = preview_cd
        self.DELETE_COOLDOWN_SECONDS: float = delete_cd
        self.EDIT_COOLDOWN_SECONDS: float = edit_cd
        self.ADD_COOLDOWN_SECONDS: float = add_cd

        self.CHANNEL_PAUSE_DURATION: int = channel_pause_duration

        self.FACT_COOLDOWN: float = fact_cd
        self.SAYING_PROBABILITY: int = saying_probability

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

            'CHANNEL_PAUSE_DURATION': self.CHANNEL_PAUSE_DURATION,

            'FACT_COOLDOWN': self.FACT_COOLDOWN,
            'SAYING_PROBABILITY': self.SAYING_PROBABILITY,
        }

    @staticmethod
    def build_config(path: str):
        from utilities import write_json
        defaults: dict[str, Any] = {
            'GLOBAL_ADMIN_SERVER_ID': None,  # Mandate manually setting this value.
            'REPLY_WEIGHT_UPPER_BOUND': 1024,

            'FACT_COUNT_MAXIMUM': 50,
            'FACT_CHAR_LIMIT': 256,

            'PREVIEW_COOLDOWN_SECONDS': 5.0,
            'DELETE_COOLDOWN_SECONDS': 5.0,
            'EDIT_COOLDOWN_SECONDS': 5.0,
            'ADD_COOLDOWN_SECONDS': 5.0,

            'CHANNEL_PAUSE_DURATION': 60,

            'FACT_COOLDOWN': 1.0,
            'SAYING_PROBABILITY': 300,  # 1 / probability listed here, per message.
        }
        write_json(path, defaults, sort_keys=False, indent=4)

    @staticmethod
    def from_json(path: str) -> '_GlobalConfig':
        from utilities import load_json
        cfg = load_json(path)

        gad_sid = cfg['GLOBAL_ADMIN_SERVER_ID']
        repl_w_up = cfg['REPLY_WEIGHT_UPPER_BOUND']
        fact_count_max = cfg['FACT_COUNT_MAXIMUM']
        fact_char_limit = cfg['FACT_CHAR_LIMIT']
        preview_cd = cfg['PREVIEW_COOLDOWN_SECONDS']
        delete_cd = cfg['DELETE_COOLDOWN_SECONDS']
        edit_cd = cfg['EDIT_COOLDOWN_SECONDS']
        add_cd = cfg['ADD_COOLDOWN_SECONDS']
        channel_pause_duration = cfg['CHANNEL_PAUSE_DURATION']
        fact_cooldown = cfg['FACT_COOLDOWN']
        saying_probability = cfg['SAYING_PROBABILITY']

        return _GlobalConfig(path, gad_sid, repl_w_up, fact_count_max, fact_char_limit, preview_cd, delete_cd, edit_cd,
                             add_cd, channel_pause_duration, fact_cooldown, saying_probability)


import os as _os

_cfg_fp: str = 'config/global.json'

if not _os.path.exists(_cfg_fp):
    _GlobalConfig.build_config(_cfg_fp)
    print(f'Global config built at {_cfg_fp}, please edit accordingly.')
    import sys

    sys.exit(0)

# To be imported by other files.
CFG: _GlobalConfig = _GlobalConfig.from_json(_cfg_fp)
