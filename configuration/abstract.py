from abc import ABC, abstractmethod

from utilities import load_json, write_json


class AbstractJSONConfig(ABC):
    """
    Abstract json-maintainable configuration class.
    Basically just allows updating own data into given json file at path.
    """

    def __init__(self, update_filepath: str):
        self.update_filepath = update_filepath

    @abstractmethod
    def to_json(self) -> dict:
        """
        Returns own data as JSON-parsable dict.
        """
        raise NotImplementedError()

    def update_config_json(self):
        """
        Writes own JSON-data to update filepath.
        """
        js = self.to_json()
        cfg = load_json(self.update_filepath)
        for k, v in js.items():
            cfg[k] = v
        write_json(self.update_filepath, cfg)
