import re
from typing import List
from models import FunctionContext, Incident
from .base import BaseDetector

class UnusedParameterDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        
        # If the function is empty, it's already caught by Empty Function. Unused param still technically applies, so we check it anyway.
        for param in context.params:
            if not re.search(r'\b' + re.escape(param) + r'\b', body):
                incidents.append(Incident(
                    file_name=context.file_name,
                    function_name=context.function_name,
                    line_num=context.line_num_func,
                    line_code=context.line_code_func,
                    incident_type="Unused Parameter",
                    description=f"Parameter '{param}' is declared but not used."
                ))
        return incidents
