import re
from typing import List
from models import FunctionContext, Incident
from utils import get_file_function_types, get_line_num
from .base import BaseDetector

class RedundantVoidCastDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        
        void_funcs, _ = get_file_function_types(context.masked_code)
        
        pattern = r'\(\s*void\s*\)\s*([a-zA-Z_]\w*)\s*\('
        offset = context.brace_start_idx + 1
        
        for match in re.finditer(pattern, body):
            func_name = match.group(1)
            
            if func_name in void_funcs:
                match_start_in_file = offset + match.start()
                line_number = get_line_num(context.original_code, match_start_in_file)
                
                incidents.append(Incident(
                    file_name=context.file_name,
                    function_name=context.function_name,
                    line_num=line_number,
                    line_code=context.line_code_func,
                    incident_type="Redundant Void Cast",
                    description=f"Function '{func_name}' already returns void, so the (void) cast is redundant."
                ))
                
        return incidents
