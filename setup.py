#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import re
from pathlib import Path
from setuptools import setup

here = Path(__file__).resolve().parent
name = re.sub(r'-.*', '', here.stem)
readme = here.joinpath('README.md').read_text()

setup(
    name=name,
    version='1.2',
    description='Improved simple time scheduler based on standard sched',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/bulletmark/{}'.format(name),
    author='Mark Blakeney',
    author_email='mark@irsaere.net',
    keywords='sched scheduler timer periodic cron crontab',
    license='GPLv3',
    py_modules=[name],
    python_requires='>=3.4',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        ('share/doc/{}'.format(name), ['README.md']),
    ],
)
