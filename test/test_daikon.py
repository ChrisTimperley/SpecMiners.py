# -*- coding: utf-8 -*-
import pytest

import os

import specminers


DIR_HERE = os.path.dirname(__file__)
DIR_EXAMPLES = os.path.join(DIR_HERE, 'examples')


def test_daikon():
    daikon = specminers.Daikon()
    filenames = [os.path.join(DIR_EXAMPLES, 'ardu.decls'),
                 os.path.join(DIR_EXAMPLES, 'ardu.dtrace')]
    out = daikon(*filenames)
