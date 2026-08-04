from __future__ import annotations

from Rewrite.configuration.abstract import AbstractJSONConfig
from Rewrite.utilities import write_json, load_json


class TokenConfig(AbstractJSONConfig):
    def to_json(self) -> dict:
        return {
            'main': self.main,
            'test': self.test,
        }

    def __init__(self, path: str, main_token: str, test_token: str):
        super().__init__(path)
        assert isinstance(main_token, str), 'Main token not of type string'
        assert isinstance(test_token, str), 'Test token not of type string'

        self.main = main_token
        self.test = test_token

    @staticmethod
    def build_config(filepath: str):
        defaults: dict[str, str] = {
            'main': 'Put your main token here! It is used in main.py',
            'test': 'Put your test token here! It is used only for feature testing using testing.py',
        }
        write_json(filepath, defaults, sort_keys=False, indent=4)

    @staticmethod
    def from_json(filepath: str) -> TokenConfig:
        cfg = load_json(filepath)
        return TokenConfig(filepath, cfg['main'], cfg['test'])