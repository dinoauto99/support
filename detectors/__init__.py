from .unused_param import UnusedParameterDetector
from .empty_function import EmptyFunctionDetector
from .empty_if import EmptyIfDetector
from .empty_switch import EmptySwitchDetector

def get_all_detectors():
    return [
        EmptyFunctionDetector(),
        UnusedParameterDetector(),
        EmptyIfDetector(),
        EmptySwitchDetector()
    ]
