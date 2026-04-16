from dataclasses import dataclass
from typing import List

@dataclass
class Incident:
    file_name: str
    function_name: str
    line_num: int
    line_code: str
    incident_type: str
    description: str

    def to_row(self) -> List[str]:
        return [
            f"{self.file_name} - {self.function_name}",
            f"{self.line_num}: {self.line_code}",
            self.incident_type,
            self.description
        ]

@dataclass
class FunctionContext:
    file_name: str
    function_name: str
    original_code: str
    masked_code: str
    
    # Attributes set during parsing
    func_start_idx: int
    params: List[str]
    brace_start_idx: int
    brace_end_idx: int
    line_num_func: int
    line_code_func: str
    
    @property
    def body_masked(self) -> str:
        if self.brace_start_idx != -1 and self.brace_end_idx != -1:
            return self.masked_code[self.brace_start_idx + 1:self.brace_end_idx]
        return ""
