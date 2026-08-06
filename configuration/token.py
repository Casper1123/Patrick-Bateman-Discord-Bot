from __future__ import annotations

from configuration.abstract import AbstractJSONConfig
from utilities import write_json, load_json


class TokenConfig(AbstractJSONConfig):
    def to_json(self) -> dict:
        return {
            'token': self.token,
        }

    def __init__(self, path: str, token: str):
        super().__init__(path)
        if not (isinstance(token, str) and not token is None):
            raise TypeError('Token not of type string')

        self.token = token

    @staticmethod
    def build_config(filepath: str):
        defaults: dict[str, ...] = {
            'token': None,
        }
        write_json(filepath, defaults, sort_keys=False, indent=4)

    @staticmethod
    def from_json(filepath: str) -> TokenConfig:
        cfg = load_json(filepath)
        return TokenConfig(filepath, cfg['token'])