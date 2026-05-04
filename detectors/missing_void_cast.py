import re
from typing import List
from models import FunctionContext, Incident
from utils import get_file_function_types, get_line_num
from .base import BaseDetector

class MissingVoidCastDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        
        _, non_void_funcs = get_file_function_types(context.masked_code)
        
        pattern = r'\b([a-zA-Z_]\w*)\s*\('
        offset = context.brace_start_idx + 1
        
        keywords_to_ignore = {'if', 'while', 'for', 'switch', 'return', 'sizeof'}
        
        for match in re.finditer(pattern, body):
            func_name = match.group(1)
            
            if func_name in non_void_funcs and func_name not in keywords_to_ignore:
                start_idx = match.start()
                
                prev_char = ''
                i = start_idx - 1
                while i >= 0 and body[i].isspace():
                    i -= 1
                
                if i >= 0:
                    prev_char = body[i]
                
                prev_chunk = "".join(body[:start_idx].split())
                if prev_chunk.endswith("(void)"):
                    continue 
                    
                if prev_char in [';', '{', '}'] or prev_char == '':
                    match_start_in_file = offset + match.start()
                    line_number = get_line_num(context.original_code, match_start_in_file)
                    
                    incidents.append(Incident(
                        file_name=context.file_name,
                        function_name=context.function_name,
                        line_num=line_number,
                        line_code=context.line_code_func,
                        incident_type="Missing Void Cast",
                        description=f"Function '{func_name}' returns a value, but it is called as a standalone statement without a (void) cast."
                    ))
                    
        return incidents
