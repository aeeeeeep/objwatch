#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON to Log Converter for ObjWatch

This script converts ObjWatch JSON output files to human-readable log format.
"""

import os
import json
import argparse
from typing import Dict, Any, List


class JSONToLogConverter:
    """
    Converts ObjWatch JSON files to human-readable log format.
    """

    @staticmethod
    def _generate_prefix(lineno: int, call_depth: int) -> str:
        """
        Generate a formatted prefix for logging with indentation instead of '  ' characters.

        Args:
            lineno (int): The line number where the event occurred.
            call_depth (int): Current depth of the call stack.

        Returns:
            str: The formatted prefix string with proper indentation.
        """
        # Use 2 spaces per indentation level
        indent = "  " * call_depth
        return f"{lineno:>5} {indent}"

    @staticmethod
    def _format_config(config: Dict[str, Any]) -> str:
        """
        Format configuration section.

        Args:
            config (Dict[str, Any]): Configuration dictionary.

        Returns:
            str: Formatted configuration string.
        """
        lines = ["## Config:"]
        for key, value in config.items():
            if isinstance(value, list):
                lines.append(f"* {key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"* {key}: {value}")
        return "\n".join(lines)

    @staticmethod
    def _process_events(events: List[Dict[str, Any]], call_depth: int = 0) -> List[str]:
        """
        Process events recursively and generate log lines.

        Args:
            events (List[Dict[str, Any]]): List of events to process.
            call_depth (int): Current call depth.

        Returns:
            List[str]: List of generated log lines.
        """
        log_lines = []

        for event in events:
            if event['type'] == 'Function':
                # Handle function run event
                prefix = JSONToLogConverter._generate_prefix(event['run_line'], call_depth)
                run_msg = f"{prefix}run {event['qualified_name']}"
                if 'call_msg' in event:
                    run_msg += f" <- {event['call_msg']}"
                log_lines.append(run_msg)

                # Process nested events
                if 'events' in event and event['events']:
                    nested_lines = JSONToLogConverter._process_events(event['events'], call_depth + 1)
                    log_lines.extend(nested_lines)

                # Handle function end event
                end_prefix = JSONToLogConverter._generate_prefix(event['end_line'] if 'end_line' in event else event['run_line'], call_depth)
                end_msg = f"{end_prefix}end {event['qualified_name']}"
                if 'return_msg' in event:
                    end_msg += f" -> {event['return_msg']}"
                log_lines.append(end_msg)

            elif event['type'] == 'upd':
                # Handle update events
                prefix = JSONToLogConverter._generate_prefix(event['line'], event.get('call_depth', call_depth))
                log_lines.append(f"{prefix}upd {event['name']} {event['old']} -> {event['new']}")

            elif event['type'] in ['apd', 'pop']:
                # Handle collection change events
                prefix = JSONToLogConverter._generate_prefix(event['line'], event.get('call_depth', call_depth))
                event_type = event['type']
                # For apd/pop events, format the message based on available data
                if isinstance(event['old'], dict) and isinstance(event['new'], dict):
                    old_len = event['old'].get('len', '?')
                    new_len = event['new'].get('len', '?')
                    value_type = event['old'].get('type', 'Unknown')
                    log_lines.append(f"{prefix}{event_type} {event['name']} ({value_type})(len){old_len} -> {new_len}")
                else:
                    log_lines.append(f"{prefix}{event_type} {event['name']}")

        return log_lines

    def convert(self, json_path: str, output_path: str) -> None:
        """
        Convert JSON file to log format.

        Args:
            json_path (str): Path to the input JSON file.
            output_path (str): Path to the output log file.
        """
        # Read JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        objwatch_data = data.get('ObjWatch', {})
        runtime_info = objwatch_data.get('runtime_info', {})
        config = objwatch_data.get('config', {})
        events = objwatch_data.get('events', [])

        # Generate log content
        log_lines = []

        log_lines.append("=" * 80)
        log_lines.append("# ObjWatch Log")
        log_lines.append(f"> Version:        {runtime_info.get('version', 'Unknown')}")
        log_lines.append(f"> Start Time:     {runtime_info.get('start_time', 'Unknown')}")
        log_lines.append(f"> System Info:    {runtime_info.get('system_info', 'Unknown')}")
        log_lines.append(f"> Python Version: {runtime_info.get('python_version', 'Unknown')}")
        log_lines.append("")
        # Add config section
        log_lines.append(self._format_config(config))
        log_lines.append("")
        # Skip Targets, Filename Targets, and Exclude Filename Targets sections as requested
        log_lines.append("=" * 80)

        # Process events
        event_log_lines = self._process_events(events)
        log_lines.extend(event_log_lines)

        # Write to log file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_lines))

        print(f"Conversion completed. Log file saved to: {output_path}")


def main():
    """
    Main function to handle command-line arguments and run the converter.
    """
    parser = argparse.ArgumentParser(description='Convert ObjWatch JSON output to human-readable log format')
    parser.add_argument('json_file', help='Path to the input JSON file')
    parser.add_argument('-o', '--output', help='Path to the output log file', default=None)
    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Default output path: replace .json extension with .objwatch
        base_name = os.path.splitext(args.json_file)[0]
        output_path = f"{base_name}.objwatch"

    # Validate input file
    if not os.path.exists(args.json_file):
        print(f"Error: JSON file not found: {args.json_file}")
        return

    # Create converter and run
    converter = JSONToLogConverter()
    converter.convert(args.json_file, output_path)


if __name__ == "__main__":
    main()
