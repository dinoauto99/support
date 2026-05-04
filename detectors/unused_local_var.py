import re
from typing import List
from models import FunctionContext, Incident
from .base import BaseDetector

class UnusedLocalVariableDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        
        # Match common C type declarations followed by variables
        # Handles basic types, stdint types (_t), and struct/enum/union
        type_pattern = r'\b(?:(?:struct|enum|union)\s+[a-zA-Z_]\w*|int|char|float|double|long|short|unsigned|signed|size_t|bool|_Bool|[a-zA-Z_]\w*_t)\s+([^;]+);'
        
        matches = re.finditer(type_pattern, body)
        for match in matches:
            decl_str = match.group(1)
            # Split by comma to handle cases like `int x, y = 0;`
            parts = decl_str.split(',')
            for part in parts:
                # Remove initialization part e.g., `= 5`
                part = part.split('=')[0]
                # Remove array brackets e.g., `[10]`
                part = part.split('[')[0]
                
                # Extract the identifier (ignoring pointers *)
                part_clean = part.replace('*', ' ').strip()
                var_match = re.search(r'\b([a-zA-Z_]\w*)\s*$', part_clean)
                
                if var_match:
                    var_name = var_match.group(1)
                    
                    # Avoid catching parameters again if they happen to match somehow
                    if var_name in context.params:
                        continue
                        
                    # Count occurrences of the variable in the entire function body
                    # Since it's declared, it will appear at least once. 
                    # If it appears exactly once, it's unused.
                    occurrences = len(re.findall(r'\b' + re.escape(var_name) + r'\b', body))
                    if occurrences == 1:
                        incidents.append(Incident(
                            file_name=context.file_name,
                            function_name=context.function_name,
                            line_num=context.line_num_func,
                            line_code=context.line_code_func,
                            incident_type="Unused Local Variable",
                            description=f"Local variable '{var_name}' is declared but not used."
                        ))
                        
        return incidents
