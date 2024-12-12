from setuptools import setup, find_packages

setup(
    name='objwatch',
    version='0.1.0',
    description='A Python library to trace and monitor object attributes and method calls.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='aeeeeeep',
    author_email='aeeeeeep@proton.me',
    url='https://github.com/aeeeeeep/objwatch',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'objwatch=objwatch.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    zip_safe=False,
)
