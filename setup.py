from setuptools import setup, find_packages

try:
    from pathlib import Path

    this_dir = Path(__file__).parent
    version = (this_dir / 'version.txt').read_text()
except ImportError:
    try:
        with open('version.txt', 'r') as v:
            version = v.read()
    except IOError:
        pass
    except FileNotFoundError:
        pass

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
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    zip_safe=False,
)
