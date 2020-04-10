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
    install_requires=[
        'attrs>=17.2.0',
        'typing-extensions>=3.7.2',
        'docker~=3.7.2'
    ],
    packages=['specminers']
)
