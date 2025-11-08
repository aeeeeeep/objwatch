# MIT License
# Copyright (c) 2025 aeeeeeep

import re
import json


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


def compare_json_files(generated_file, golden_file):
    """
    Compare two JSON files, ignoring specific dynamic fields that may vary between runs.
    """
    with open(generated_file, 'r') as f:
        generated_data = json.load(f)

    with open(golden_file, 'r') as f:
        golden_data = json.load(f)

    # Remove dynamic fields from both data structures
    def clean_json_data(data):
        # Clean runtime_info which contains system-specific and time-specific information
        if 'ObjWatch' in data and 'runtime_info' in data['ObjWatch']:
            del data['ObjWatch']['runtime_info']
        return data

    cleaned_generated = clean_json_data(generated_data)
    cleaned_golden = clean_json_data(golden_data)

    # Compare the cleaned data structures
    return cleaned_generated == cleaned_golden
