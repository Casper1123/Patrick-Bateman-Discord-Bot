from abc import ABC, abstractmethod

class AbstractDTO(ABC):
    """
    Defines default required behaviour of Data Transfer Objects returned by the Database layer.
    """
    @abstractmethod
    def as_json(self) -> dict[str, int | float | None | str | bool | dict]:
        """
        Returns a JSON representation of the object.
        """
        raise NotImplementedError()

    """
    Leaving this here for later in case I'd like to universally enforce hashing functionality.
    
    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError()
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError()
    """