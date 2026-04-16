from typing import List
from models import FunctionContext, Incident
from .base import BaseDetector

class EmptyFunctionDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        
        if len(body.strip()) == 0:
            incidents.append(Incident(
                file_name=context.file_name,
                function_name=context.function_name,
                line_num=context.line_num_func,
                line_code=context.line_code_func,
                incident_type="Empty Function",
                description="Function has no logic or statements."
            ))
        return incidents
