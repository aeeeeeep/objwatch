# MIT License
# Copyright (c) 2025 aeeeeeep

import sys
import subprocess
import os
from pathlib import Path
from setuptools import setup, find_packages


def get_version_with_git() -> str:
    """
    Get package version, appending git commit hash for source installations.

    Returns:
        str: Version string from version.txt, with optional git commit hash
             for source install scenarios.
    """
    try:
        this_dir = Path(__file__).parent
        base_version = (this_dir / 'version.txt').read_text().strip()
    except (ImportError, FileNotFoundError):
        base_version = '0.0.0'

    # Comprehensive detection for source installation scenarios
    def is_source_installation() -> bool:
        """
        Detect if this is a source installation scenario.

        Returns:
            bool: True if this appears to be a source installation.
        """
        # Check direct setup.py commands
        if any(cmd in sys.argv for cmd in ['install', 'develop']):
            return True

        # Check environment variables that indicate pip/build processes
        pip_env_vars = ['PIP_REQ_TRACKER', 'PIP_BUILD_TRACKER', 'PIP_NO_INPUT']
        if any(os.environ.get(var) for var in pip_env_vars):
            return True

        return False

    if is_source_installation():
        try:
            # Get short git commit hash
            git_hash = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'], text=True, stderr=subprocess.DEVNULL, cwd=Path(__file__).parent
            ).strip()
            return f"{base_version}+{git_hash}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not available or not in a git repository
            pass

    return base_version


try:
    version = get_version_with_git()
except Exception:
    version = '0.0.0'


MIN_PYTHON = (3, 8)
MAX_PYTHON = (3, 14)

PYTHON_REQUIRES = f">={MIN_PYTHON[0]}.{MIN_PYTHON[1]},<{MAX_PYTHON[0]}.{MAX_PYTHON[1] + 1}"
PYTHON_CLASSIFIERS = [
    f"Programming Language :: Python :: {MIN_PYTHON[0]}.{m}" for m in range(MIN_PYTHON[1], MAX_PYTHON[1] + 1)
]

BASE_CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
]
CLASSIFIERS = BASE_CLASSIFIERS + PYTHON_CLASSIFIERS

setup(
    name='objwatch',
    version=version,
    description='A Python library to trace and monitor object attributes and method calls.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='aeeeeeep',
    author_email='aeeeeeep@proton.me',
    url='https://github.com/aeeeeeep/objwatch',
    packages=find_packages(),
    python_requires=PYTHON_REQUIRES,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)
