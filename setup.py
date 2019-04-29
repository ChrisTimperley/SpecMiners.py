#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup


PACKAGE_NAME = 'specminers'
VERSION = '0.0.1'

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    python_requires='>=3.5',
    description='Python bindings for several popular specification mining tools',
    author='Chris Timperley',
    author_email='christimperley@googlemail.com',
    url='https://github.com/ChrisTimperley/SpecMiners.py',
    license='mit',
    install_requires=[
        'attrs>=17.2.0',
        'typing-extensions>=3.7.2',
        'docker~=3.7.2'
    ],
    packages=['specminers'],
    keywords=['specification', 'invariants', 'mining', 'daikon', 'texada'],
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
