#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manuals:
* https://setuptools.readthedocs.io/en/latest/setuptools.html
* https://docs.python.org/3/distutils/
* https://www.digitalocean.com/community/tutorials/how-to-package-and-distribute-python-applications
"""
import argparse
import io
import os
import sys

from setuptools import find_packages, setup

# Parse own args
parser = argparse.ArgumentParser()
parser.add_argument('--embedded', action='store_true')
args, unknown_args = parser.parse_known_args()
sys.argv = [sys.argv[0]] + unknown_args

# Define parameters
is_embedded = args.embedded

# Package meta-data.
NAME = 'toggl2tempo'
DESCRIPTION = 'Desktop application to sync work logs between Toggl and JIRA Tempo.'
URL = 'https://github.com/OttensPavel/toggl2tempo'
EMAIL = 'ottenspa@gmail.com'
AUTHOR = 'Pavel Ottens'
REQUIRES_PYTHON = '>=3.8.0'

# What packages are required for this module to be executed?
REQUIRED = [
    "jsonschema >=2.5.1,<3.0",
    "PyQt5 >=5.13.2",
    "python-dateutil >=2.6.0",
    "pytz >= 2021.1",
    "requests >= 2.12.4,<3.0",
    "sip >=5.1.1",
    "tzlocal >=2.1,<3.0",
    "loguru >=0.7.2,<0.8.0",
]

here = os.path.abspath(os.path.dirname(__file__))

# Read version
with io.open(os.path.join(here, 'version'), encoding='ascii') as f:
    version = f.read()

# Import the README and use it as the long-description.
with io.open(os.path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Entry points
ENTRY_POINTS = {} if is_embedded else \
    {
        "console_scripts": [
            "toggl2tempo_debug = j2toggl_ui:start_ui",
        ],
        "gui_scripts": [
            "toggl2tempo = j2toggl_ui:start_ui",
        ]
    }

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    install_requires=REQUIRED,
    entry_points=ENTRY_POINTS,
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10'
    ]
)
