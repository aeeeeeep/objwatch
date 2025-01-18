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


def compare_xml_elements(elem1, elem2):
    if elem1.tag != elem2.tag:
        return False
    if elem1.attrib != elem2.attrib:
        return False
    if (elem1.text or '').strip() != (elem2.text or '').strip():
        return False
    if len(elem1) != len(elem2):
        return False
    return all(compare_xml_elements(c1, c2) for c1, c2 in zip(elem1, elem2))
