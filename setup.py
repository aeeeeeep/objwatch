# MIT License
# Copyright (c) 2025 aeeeeeep

from setuptools import setup, find_packages

try:
    from pathlib import Path

    this_dir = Path(__file__).parent
    version = (this_dir / 'version.txt').read_text()
except (ImportError, FileNotFoundError):
    version = '0.0.0'


def fetch_requirements(path):
    with open(path, 'r') as fd:
        return [r.strip() for r in fd.readlines()]


install_requires = fetch_requirements('requirements/requirements.txt')


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
    install_requires=install_requires,
    packages=find_packages(),
    python_requires=PYTHON_REQUIRES,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)
