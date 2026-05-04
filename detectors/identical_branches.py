import re
from typing import List
from models import FunctionContext, Incident
from utils import balance_parentheses, get_line_num
from .base import BaseDetector

class IdenticalBranchesDetector(BaseDetector):
    def detect(self, context: FunctionContext) -> List[Incident]:
        incidents = []
        masked = context.masked_code
        orig = context.original_code
        
        start_search = context.brace_start_idx + 1
        end_search = context.brace_end_idx
        
        idx = start_search
        while idx < end_search:
            match = re.search(r'\bif\s*\(', masked[idx:end_search])
            if not match:
                break
                
            if_idx = idx + match.start()
            paren_start = idx + match.end() - 1
            paren_end = balance_parentheses(masked, paren_start, '(', ')')
            
            if paren_end == -1:
                break
                
            brace_start = -1
            for i in range(paren_end + 1, end_search):
                if masked[i] == '{':
                    brace_start = i
                    break
                elif not masked[i].isspace():
                    break
            
            if brace_start == -1:
                idx = paren_end + 1
                continue
                
            brace_end = balance_parentheses(masked, brace_start, '{', '}')
            if brace_end == -1:
                break
                
            blocks = []
            block_content = orig[brace_start + 1: brace_end].strip()
            blocks.append(("if", block_content, get_line_num(orig, if_idx)))
            
            curr_idx = brace_end + 1
            
            while curr_idx < end_search:
                while curr_idx < end_search and masked[curr_idx].isspace():
                    curr_idx += 1
                
                if curr_idx + 4 <= end_search and masked[curr_idx:curr_idx+4] == 'else':
                    curr_idx += 4
                    while curr_idx < end_search and masked[curr_idx].isspace():
                        curr_idx += 1
                        
                    if curr_idx + 2 <= end_search and masked[curr_idx:curr_idx+2] == 'if':
                        curr_idx += 2
                        while curr_idx < end_search and masked[curr_idx] != '(':
                            curr_idx += 1
                        if curr_idx >= end_search: break
                        
                        elif_paren_start = curr_idx
                        elif_paren_end = balance_parentheses(masked, elif_paren_start, '(', ')')
                        if elif_paren_end == -1: break
                        
                        elif_brace_start = -1
                        for i in range(elif_paren_end + 1, end_search):
                            if masked[i] == '{':
                                elif_brace_start = i
                                break
                            elif not masked[i].isspace():
                                break
                        
                        if elif_brace_start == -1:
                            break
                            
                        elif_brace_end = balance_parentheses(masked, elif_brace_start, '{', '}')
                        if elif_brace_end == -1: break
                        
                        elif_block = orig[elif_brace_start + 1: elif_brace_end].strip()
                        blocks.append(("else if", elif_block, get_line_num(orig, elif_paren_start)))
                        curr_idx = elif_brace_end + 1
                    else:
                        else_brace_start = -1
                        for i in range(curr_idx, end_search):
                            if masked[i] == '{':
                                else_brace_start = i
                                break
                            elif not masked[i].isspace():
                                break
                        
                        if else_brace_start == -1:
                            break
                            
                        else_brace_end = balance_parentheses(masked, else_brace_start, '{', '}')
                        if else_brace_end == -1: break
                        
                        else_block = orig[else_brace_start + 1: else_brace_end].strip()
                        blocks.append(("else", else_block, get_line_num(orig, else_brace_start)))
                        curr_idx = else_brace_end + 1
                        break
                else:
                    break
                    
            for i in range(len(blocks)):
                for j in range(i + 1, len(blocks)):
                    norm_i = re.sub(r'\s+', '', blocks[i][1])
                    norm_j = re.sub(r'\s+', '', blocks[j][1])
                    if norm_i == norm_j and len(norm_i) > 0:
                        incidents.append(Incident(
                            file_name=context.file_name,
                            function_name=context.function_name,
                            line_num=blocks[j][2],
                            line_code=context.line_code_func,
                            incident_type="Identical Branches",
                            description=f"Branch '{blocks[j][0]}' has identical processing statements to a previous branch."
                        ))
                        break
            
            idx = curr_idx
            
        return incidents
