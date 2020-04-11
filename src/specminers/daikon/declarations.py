# -*- coding: utf-8 -*-
__all__ = ('Declarations', 'DeclarationsLoader')

from typing import Iterable, Iterator, List, Mapping, Optional, Sequence
import collections

from loguru import logger
import attr

from .loader import LineBuffer, LineLoader
from .ppt import ProgramPoint, ProgramPointLoader


class Declarations(Mapping[str, ProgramPoint]):
    def __init__(self, points: Sequence[ProgramPoint]) -> None:
        self.__points = collections.OrderedDict((p.name, p) for p in points)

    def __len__(self) -> int:
        """Returns the number of program points."""
        return len(self.__points)

    def __getitem__(self, name: str) -> ProgramPoint:
        """Retrieves a program point with a given name."""
        return self.__points[name]

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the names of the program points."""
        yield from self.__points

    @property
    def lines(self) -> List[str]:
        ls = ['decl-version 2.0', 'var-comparability none']
        for ppt in self.values():
            ls += ppt.lines
        return ls

    def __str__(self) -> str:
        return '\n'.join(self.lines)

    @classmethod
    def load(cls, filename: str) -> 'Declarations':
        logger.trace(f'loading declarations from file: {filename}')
        declarations = DeclarationsLoader.from_file(filename)
        logger.trace(f'loaded {len(declarations)} declarations from file')
        return declarations

    def save(self, filename: str) -> None:
        """Saves the variable declarations to a given file on disk."""
        with open(filename, 'w') as f:
            f.write(str(self))


@attr.s
class DeclarationsLoader(LineLoader[Declarations]):
    lines: LineBuffer = attr.ib()
    ppts: List[ProgramPoint] = attr.ib(factory=list)
    decl_version: Optional[str] = attr.ib(default=None)
    var_comparability: Optional[str] = attr.ib(default=None)
    input_language: Optional[str] = attr.ib(default=None)

    def lookup(self, name: str):
        return {'decl-version': self._read_decl_version,
                'input-language': self._read_input_language,
                'var-comparability': self._read_var_comparability,
                'ppt': self._read_ppt}[name]

    def _read_decl_version(self, decl_version: str) -> None:
        self.decl_version = decl_version
        logger.trace(f'using decl-version: {self.decl_version}')

    def _read_input_language(self, input_language: str) -> None:
        self.input_language = input_language
        logger.trace(f'using input-language: {self.input_language}')

    def _read_var_comparability(self, var_comparability: str) -> None:
        self.var_comparability = var_comparability
        logger.trace(f'using var-comparability: {self.var_comparability}')

    def _read_ppt(self, name: str) -> None:
        ppt = ProgramPointLoader.from_line_buffer(name=name, lines=self.lines)
        self.ppts.append(ppt)

    def build(self) -> Declarations:
        return Declarations(points=self.ppts)
