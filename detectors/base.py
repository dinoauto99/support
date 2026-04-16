from abc import ABCMeta, abstractmethod
from typing import List
from models import FunctionContext, Incident

class SingletonABCMeta(ABCMeta):
    """Metaclass combining ABCMeta and Singleton to manage a single unique instance."""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseDetector(metaclass=SingletonABCMeta):
    """
    The core abstract class representing a strategy (Singleton applied). 

    Any incident rule checker must inherit from this class.
    """
    
    @abstractmethod
    def detect(self, context: FunctionContext) -> List[Incident]:
        """
        Receives a function context object (with decomposed body) and returns an array of found incidents.
        """
        pass
