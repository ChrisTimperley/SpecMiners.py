# -*- coding: utf-8 -*-
"""Provides facilities for reading and writing trace files.

References
----------
* https://plse.cs.washington.edu/daikon/download/doc/developer
"""
from .reader import TraceFileReader
from .record import TraceRecord, TraceRecordVariable
from .writer import TraceWriter
