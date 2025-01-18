# MIT License
# Copyright (c) 2025 aeeeeeep

import re


def strip_line_numbers(log):
    pattern = r'(DEBUG:objwatch:\s*)\d+\s*(\|*\s*.*)'
    stripped_lines = []
    for line in log.splitlines():
        match = re.match(pattern, line)
        if match:
            stripped_line = f"{match.group(1)}{match.group(2)}"
            stripped_lines.append(stripped_line)
        else:
            stripped_lines.append(line)
    return '\n'.join(stripped_lines)


def filter_func_ptr(generated_log):
    return re.sub(r'<function [\w_]+ at 0x[0-9a-fA-F]+>', '<function [FILTERED]>', generated_log)
