from abc import ABC, abstractmethod
from typing import List
from models import FunctionContext, Incident

class BaseDetector(ABC):
    """
    The core abstract class representing a strategy. 

    Any incident rule checker must inherit from this class.
    """
    
    @abstractmethod
    def detect(self, context: FunctionContext) -> List[Incident]:
        """
        Receives a function context object (with decomposed body) and returns an array of found incidents.
        """
        pass
