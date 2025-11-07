# MIT License
# Copyright (c) 2025 aeeeeeep

import time
import importlib.metadata
from typing import Set, Optional

from ..targets import Targets, TargetsType
from ..wrappers import ABCWrapper
from .logger import log_info

__version__ = importlib.metadata.version("objwatch")


def log_metainfo_with_format(
    targets: dict,
    filename_targets: Set[str],
    exclude_filename_targets: Set[str],
    wrapper: Optional[ABCWrapper] = None,
) -> None:
    """Log metainfo in formatted view."""

    format_time = time.strftime('%Y-%m-%d %H:%M:%S')
    targets_str = Targets.serialize_targets(targets)

    # Table header with version information
    header = [
        "=" * 80,
        "# ObjWatch Log",
        f"> Version: {__version__}",
        f"> Time:    {format_time}",
    ]

    # Targets section
    targets_section = [
        "\n## Targets:",
        targets_str,
    ]

    # Filename targets section
    filename_targets_section = [
        "\n## Filename Targets:",
    ]
    if filename_targets:
        for target in sorted(filename_targets):
            filename_targets_section.append(f"* {target}")
    else:
        filename_targets_section.append("* None")

    # Exclude filename targets section
    exclude_filename_targets_section = [
        "\n## Exclude Filename Targets:",
    ]
    if exclude_filename_targets:
        for target in sorted(exclude_filename_targets):
            exclude_filename_targets_section.append(f"* {target}")
    else:
        exclude_filename_targets_section.append("* None")

    # Wrapper section
    wrapper_section = [
        "\n## Wrapper:",
    ]
    if wrapper:
        wrapper_section.append(f"* {wrapper.__class__.__name__}")
    else:
        wrapper_section.append("* None")

    # Footer
    footer = ["=" * 80]

    # Combine all sections and log
    log_content = "\n".join(
        header
        + targets_section
        + filename_targets_section
        + exclude_filename_targets_section
        + wrapper_section
        + footer
    )
    log_info(log_content)
