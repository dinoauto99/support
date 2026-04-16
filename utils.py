import re
from typing import List

def mask_comments_and_strings(code: str) -> str:
    """
    Replaces comments and strings with spaces to preserve line numbers and string length characters.
    """
    out = []
    state = 'NORMAL'
    i = 0
    n = len(code)
    while i < n:
        if state == 'NORMAL':
            if i + 1 < n and code[i:i+2] == '//':
                out.append('  ')
                state = 'LINE_COMMENT'
                i += 2
            elif i + 1 < n and code[i:i+2] == '/*':
                out.append('  ')
                state = 'BLOCK_COMMENT'
                i += 2
            elif code[i] == '"':
                out.append(' ')
                state = 'STRING'
                i += 1
            elif code[i] == "'":
                out.append(' ')
                state = 'CHAR'
                i += 1
            else:
                out.append(code[i])
                i += 1
        elif state == 'LINE_COMMENT':
            if code[i] == '\n':
                state = 'NORMAL'
                out.append('\n')
            else:
                out.append(' ')
            i += 1
        elif state == 'BLOCK_COMMENT':
            if i + 1 < n and code[i:i+2] == '*/':
                out.append('  ')
                state = 'NORMAL'
                i += 2
            elif code[i] == '\n':
                out.append('\n')
                i += 1
            else:
                out.append(' ')
                i += 1
        elif state == 'STRING':
            if i + 1 < n and code[i] == '\\':
                out.append('  ')
                i += 2
            elif code[i] == '"':
                out.append(' ')
                state = 'NORMAL'
                i += 1
            elif code[i] == '\n':
                out.append('\n')
                i += 1
            else:
                out.append(' ')
                i += 1
        elif state == 'CHAR':
            if i + 1 < n and code[i] == '\\':
                out.append('  ')
                i += 2
            elif code[i] == "'":
                out.append(' ')
                state = 'NORMAL'
                i += 1
            elif code[i] == '\n':
                out.append('\n')
                i += 1
            else:
                out.append(' ')
                i += 1
    return "".join(out)

def get_line_num(code: str, index: int) -> int:
    return code.count('\n', 0, index) + 1

def get_line_code(code: str, line_num: int) -> str:
    lines = code.split('\n')
    if 0 < line_num <= len(lines):
        return lines[line_num - 1].strip()
    return ""

def balance_parentheses(code: str, start_index: int, open_char='(', close_char=')') -> int:
    count = 0
    for i in range(start_index, len(code)):
        if code[i] == open_char:
            count += 1
        elif code[i] == close_char:
            count -= 1
            if count == 0:
                return i
    return -1

def extract_params(param_str: str) -> List[str]:
    params = []
    if not param_str or param_str.strip() == "void":
        return params
    
    parts = param_str.split(',')
    for part in parts:
        part = part.strip()
        matches = re.findall(r'\b[a-zA-Z_]\w*\b', part)
        if matches:
            param_name = matches[-1]
            if param_name not in ["const", "volatile", "restrict"]:
                params.append(param_name)
    return params
