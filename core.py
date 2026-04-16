import re
from typing import List, Dict
from models import FunctionContext, Incident
from utils import extract_params, balance_parentheses, get_line_num, get_line_code, mask_comments_and_strings
from detectors.base import BaseDetector

class CFileAnalyzer:
    def __init__(self, detectors: List[BaseDetector]):
        self.detectors = detectors

    def analyze_file(self, file_path: str, file_name: str, functions_to_check: List[str]) -> List[Incident]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

        masked_code = mask_comments_and_strings(original_code)
        all_incidents = []

        for func_name in functions_to_check:
            context = self._create_context(original_code, masked_code, func_name, file_name)
            if context:
                # Run all registered detectors
                for detector in self.detectors:
                    incidents = detector.detect(context)
                    all_incidents.extend(incidents)
                    
        return all_incidents

    def _create_context(self, original_code: str, masked_code: str, func_name: str, file_name: str) -> FunctionContext:
        pattern = r'\b' + re.escape(func_name) + r'\b\s*\('
        match = re.search(pattern, masked_code)
        
        if not match:
            return None
        
        func_start_idx = match.start()
        paren_start = match.end() - 1
        paren_end = balance_parentheses(masked_code, paren_start, '(', ')')
        
        if paren_end == -1:
            return None
        
        param_str = masked_code[paren_start+1:paren_end]
        params = extract_params(param_str)
        
        brace_start = -1
        for i in range(paren_end + 1, len(masked_code)):
            if masked_code[i] == '{':
                brace_start = i
                break
            elif not masked_code[i].isspace():
                if masked_code[i] == ';':
                    return None
                
        if brace_start == -1:
            return None
            
        brace_end = balance_parentheses(masked_code, brace_start, '{', '}')
        if brace_end == -1:
            return None

        line_num_func = get_line_num(original_code, func_start_idx)
        line_code_func = get_line_code(original_code, line_num_func)

        return FunctionContext(
            file_name=file_name,
            function_name=func_name,
            original_code=original_code,
            masked_code=masked_code,
            func_start_idx=func_start_idx,
            params=params,
            brace_start_idx=brace_start,
            brace_end_idx=brace_end,
            line_num_func=line_num_func,
            line_code_func=line_code_func
        )
