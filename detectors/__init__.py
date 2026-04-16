from .base import SingletonABCMeta
from .unused_param import UnusedParameterDetector
from .empty_function import EmptyFunctionDetector
from .empty_if import EmptyIfDetector
from .empty_switch import EmptySwitchDetector

class DetectorRegistry(metaclass=SingletonABCMeta):
    """
    A Registry adopting the Singleton pattern to manage the list of detectors.
    No matter how many times it gets instantiated in Main, it will always reuse memory.
    """
    def __init__(self):
        # Ensure the detector list is only initialized once
        if not hasattr(self, 'detectors'):
            self.detectors = [
                EmptyFunctionDetector(),
                UnusedParameterDetector(),
                EmptyIfDetector(),
                EmptySwitchDetector()
            ]

def get_all_detectors():
    return DetectorRegistry().detectors
