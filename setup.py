#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import setuptools

PATH = 'src/specminers/version.py'
PATH = os.path.join(os.path.dirname(__file__), PATH)
with open(PATH, 'r') as fh:
    exec(fh.read())

setuptools.setup(version=__version__)
