# -*- coding: utf-8 -*-
__all__ = ('TraceWriter',)

from typing import Any, Dict, IO, Iterator, Union
import contextlib
import os

from loguru import logger
import attr

from .record import TraceRecord
from ..declarations import Declarations
from ..ppt import ProgramPoint


@attr.s(auto_attribs=True)
class TraceWriter:
    """Used to write Daikon trace files.

    Warning
    -------
    This class is not thread-safe.

    Attributes
    ----------
    declarations: Declarations
        The declarations that should be used to compose the trace records.
    output: IO[str]
        The stream to which the trace file contents should be written.
    """
    declarations: Declarations
    output: IO[str]
    _nonces: Dict[str, int] = attr.ib(init=False)
    _num_entries: int = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self._num_entries = 0
        self._nonces = {v: 1 for v in self.declarations}

    @classmethod
    @contextlib.contextmanager
    def for_file(cls,
                 declarations: Declarations,
                 filename: str
                 ) -> Iterator['TraceWriter']:
        logger.debug(f'writing traces to file: {filename}')
        filename = os.path.abspath(filename)
        with open(filename, 'w') as fh:
            yield TraceWriter(declarations, fh)
            fh.flush()
        logger.debug(f'finished writing traces to file: {filename}')

    def add(self, record: TraceRecord) -> None:
        self._num_entries += 1
        w = lambda s: self.output.write(f'{s}\n')
        w('')
        w(record.ppt.name)
        if record.nonce is not None:
            w('this_invocation_nonce')
            w(record.nonce)
        for var in record.values():
            w(var.variable.name)
            w(var.variable.encode(var.value))
            w(var.modified)

    def _create_record(self,
                       ppt_or_name: Union[str, ProgramPoint],
                       **values: Any
                       ) -> TraceRecord:
        """Adds a record to the output."""
        ppt: ProgramPoint
        name: str
        if isinstance(ppt_or_name, ProgramPoint):
            name = ppt_or_name.name
            ppt = ppt_or_name
        else:
            name = ppt_or_name
            ppt = self.declarations[name]

        nonce = self._nonces[name]
        self._nonces[name] += 1
        modified: Dict[str, int] = {v: 0 for v in ppt}

        return TraceRecord(ppt, nonce, values, modified)

    def write(self,
              ppt_or_name: Union[str, ProgramPoint],
              **values: Any
              ) -> None:
        record = self._create_record(ppt_or_name, **values)
        self.add(record)
