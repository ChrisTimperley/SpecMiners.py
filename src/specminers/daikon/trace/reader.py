# -*- coding: utf-8 -*-
__all__ = ('TraceFileReader',)

from typing import Dict, Iterator, Optional, Union

import attr

from .record import TraceRecord
from ..declarations import Declarations
from ..loader import LineBuffer


@attr.s(slots=True, frozen=True, auto_attribs=True)
class TraceFileReader:
    """Used to read Daikon trace files."""
    declarations: Declarations

    def read_record(self, lines: LineBuffer) -> Iterator[TraceRecord]:
        # empty line marks the start of a new record
        assert not lines.pop()
        ppt_name = lines.pop()
        ppt = self.declarations[ppt_name]
        nonce: Optional[int] = None
        if lines.peek() == 'this_invocation_nonce':
            lines.pop()
            nonce = int(lines.pop())
        values: Dict[str, Union[str, int, float]] = {}
        modified: Dict[str, int] = {}
        for expected_var_name in ppt:
            actual_var_name = lines.pop()
            assert actual_var_name == expected_var_name
            var = ppt[expected_var_name]
            values[actual_var_name] = var.decode(lines.pop())
            modified[actual_var_name] = int(lines.pop())
        yield TraceRecord(ppt, nonce, values, modified)

    def read_line_buffer(self, lines: LineBuffer) -> Iterator[TraceRecord]:
        while not lines.is_empty():
            yield from self.read_record(lines)

    def read_file(self, filename: str) -> Iterator[TraceRecord]:
        with LineBuffer.for_file(filename) as lines:
            yield from self.read_line_buffer(lines)

    def read(self, *filenames: str) -> Iterator[TraceRecord]:
        for filename in filenames:
            yield from self.read_file(filename)
