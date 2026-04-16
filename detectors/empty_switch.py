import re
from typing import List
from models import FunctionContext, Incident
from utils import balance_parentheses, get_line_num, get_line_code
from .base import BaseDetector

class EmptySwitchDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        body = context.body_masked
        original_code = context.original_code
        brace_start = context.brace_start_idx
        
        stmt_pattern = r'\bswitch\b\s*\('
        for stmt_match in re.finditer(stmt_pattern, body):
            stmt_idx = body.find('(', stmt_match.start())
            stmt_paren_end = balance_parentheses(body, stmt_idx, '(', ')')
            
            if stmt_paren_end != -1:
                next_char_idx = -1
                for j in range(stmt_paren_end + 1, len(body)):
                    if not body[j].isspace():
                        next_char_idx = j
                        break
                
                if next_char_idx != -1 and body[next_char_idx] == '{':
                    absolute_stmt_start = brace_start + 1 + stmt_match.start()
                    stmt_line_num = get_line_num(original_code, absolute_stmt_start)
                    stmt_line_code = get_line_code(original_code, stmt_line_num)
                    
                    stmt_brace_end = balance_parentheses(body, next_char_idx, '{', '}')
                    if stmt_brace_end != -1:
                        inner_block = body[next_char_idx+1:stmt_brace_end]
                        if len(inner_block.strip()) == 0:
                            incidents.append(Incident(
                                file_name=context.file_name,
                                function_name=context.function_name,
                                line_num=stmt_line_num,
                                line_code=stmt_line_code,
                                incident_type="Empty Switch",
                                description="Found empty switch block."
                            ))
        return incidents
