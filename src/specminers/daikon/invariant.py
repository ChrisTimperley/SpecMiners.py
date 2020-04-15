# -*- coding: utf-8 -*-
"""
This module provides data structures for representing invariants and reading
invariants from a given input stream (e.g., a file or the output of a process).
"""
__all__ = ('Invariant', 'InvariantMap', 'InvariantReader')

from typing import Collection, Dict, Iterator, Mapping, Tuple

from loguru import logger
import attr

from .declarations import Declarations
from .ppt import ProgramPoint
from .loader import LineBuffer


_PPT_DELIMITER = '=' * 75


@attr.s(frozen=True, auto_attribs=True, str=False)
class Invariant:
    """An invariant that has been inferred by Daikon."""
    text: str

    def __str__(self) -> str:
        return self.text


@attr.s(frozen=True, auto_attribs=True, slots=True)
class InvariantMap(Mapping[str, Collection[Invariant]]):
    """Provides a mapping from program points to their likely invariants."""
    _ppt_to_invariants: Mapping[str, Collection[Invariant]]
    size: int

    @classmethod
    def build(cls,
              decls: Declarations,
              ppt_to_invariants: Mapping[str, Collection[Invariant]]
              ) -> 'InvariantMap':
        contents: Mapping[str, Collection[Invariant]] = \
            {name: ppt_to_invariants.get(name, []) for name in decls}
        size = sum(len(contents[name]) for name in contents)
        return InvariantMap(contents, size)

    def __len__(self) -> int:
        return len(self._ppt_to_invariants)

    def __iter__(self) -> Iterator[str]:
        yield from self._ppt_to_invariants

    def __getitem__(self, ppt: str) -> Collection[Invariant]:
        return self._ppt_to_invariants[ppt]


@attr.s(auto_attribs=True)
class InvariantReader:
    """Used to read Daikon invariant descriptions.

    Attributes
    ----------
    declarations: Declarations
        A set of program points for the program that produced the invariants.
    """
    declarations: Declarations

    def from_file(self, filename: str) -> InvariantMap:
        """Reads an invariant map from a provided file."""
        logger.debug(f'reading invariants from file: {filename}')
        with LineBuffer.for_file(filename) as lines:
            invariants = self._from_line_buffer(lines)
        logger.debug(f'read invariants from file: {filename}')
        return invariants

    def from_file_contents(self, contents: str) -> InvariantMap:
        """Reads an invariant map from the contents of a file."""
        lines = LineBuffer.for_file_contents(contents)
        return self._from_line_buffer(lines)

    def _from_line_buffer(self, lines: LineBuffer) -> InvariantMap:
        num_invariants = 0
        ppt_to_invariants: Dict[str, Collection[Invariant]] = {}
        try:
            while True:
                ppt, invariants = self._read_ppt_invariants(lines)
                ppt_to_invariants[ppt.name] = invariants
                num_invariants += len(invariants)
        except StopIteration:
            logger.debug(f'finished reading {num_invariants:d} invariants '
                         'from line stream')
        return InvariantMap.build(self.declarations, ppt_to_invariants)

    def _read_ppt_invariants(self,
                             lines: LineBuffer
                             ) -> Tuple[ProgramPoint, Collection[Invariant]]:
        """Reads the next set of invariants for a program point.

        Raises
        ------
        StopIteration
            If there are no invariants left to process in the line buffer.
        """
        delimiter_line = lines.pop()
        if delimiter_line != _PPT_DELIMITER:
            error = f'expected delimiter line (actual line: {delimiter_line}'
            raise Exception(error)

        ppt_name = lines.pop()
        if ppt_name not in self.declarations:
            error = f'unknown program point: {ppt_name}'
            raise Exception(error)
        ppt: ProgramPoint = self.declarations[ppt_name]

        logger.debug(f'reading invariants for program point [{ppt_name}]')
        invariants = []
        while True:
            if lines.peek() == _PPT_DELIMITER:
                break
            invariant_line = lines.pop()
            invariant = self._read_invariant(invariant_line)
            invariants.append(invariant)
        logger.debug(f'read {len(invariants):d} invariants for '
                     f'program point [{ppt_name}]')

        return ppt, invariants

    def _read_invariant(self, line: str) -> Invariant:
        """Reads an invariant from a given line."""
        return Invariant(text=line)
