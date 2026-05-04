from .unused_param import UnusedParameterDetector
from .empty_function import EmptyFunctionDetector
from .empty_if import EmptyIfDetector
from .empty_switch import EmptySwitchDetector
from .unused_local_var import UnusedLocalVariableDetector
from .identical_branches import IdenticalBranchesDetector
from .redundant_void_cast import RedundantVoidCastDetector
from .missing_void_cast import MissingVoidCastDetector

def get_all_detectors():
    return [
        EmptyFunctionDetector(),
        UnusedParameterDetector(),
        EmptyIfDetector(),
        EmptySwitchDetector(),
        UnusedLocalVariableDetector(),
        IdenticalBranchesDetector(),
        RedundantVoidCastDetector(),
        MissingVoidCastDetector()
    ]
