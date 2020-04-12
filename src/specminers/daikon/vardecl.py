# -*- coding: utf-8 -*-
__all__ = ('VarDecl', 'VarDeclLoader')

from typing import List, Optional, Union

from loguru import logger
import attr

from .helpers import escape_if_not_none
from .loader import LineBuffer, LineLoader

DEC_TYPE_TO_CONVERTER = {
    'float': float,
    'int': int,
    'boolean': bool,
    'java.lang.String': str
}


@attr.s(frozen=True, str=False, slots=True, auto_attribs=True)
class VarDecl:
    name: str
    dec_type: str
    rep_type: str
    comparability: Optional[int] = attr.ib(default=None)
    constant: Optional[str] = \
        attr.ib(default=None, converter=escape_if_not_none)

    @property
    def lines(self) -> List[str]:
        lines = [f'variable {self.name}',
                 '  var-kind variable',
                 f'  dec-type {self.dec_type}',
                 f'  rep-type {self.rep_type}']
        if self.comparability is not None:
            lines.append('  comparability {self.comparability}')
        if self.constant is not None:
            lines.append('  constant {self.constant}')
        return lines

    def convert(self, value_string: str) -> Union[int, str, float]:
        converter = DEC_TYPE_TO_CONVERTER[self.dec_type]
        return converter(value_string)

    def __str__(self) -> str:
        return '\n'.join(self.lines)


@attr.s(auto_attribs=True)
class VarDeclLoader(LineLoader[VarDecl]):
    lines: LineBuffer
    name: str
    kind: Optional[str] = attr.ib(default=None)
    dec_type: Optional[str] = attr.ib(default=None)
    rep_type: Optional[str] = attr.ib(default=None)
    constant: Optional[str] = attr.ib(default=None)
    comparability: Optional[int] = attr.ib(default=None)

    def lookup(self, name: str):
        return {'var-kind': self._read_kind,
                'dec-type': self._read_dec_type,
                'rep-type': self._read_rep_type,
                'flags': self._read_flags,
                'comparability': self._read_comparability,
                'constant': self._read_constant}[name]

    def has_finished(self) -> bool:
        try:
            next_line = self.lines.peek()
        except StopIteration:
            return False
        return not next_line.startswith('  ')

    def read_line(self, line: str) -> None:
        return super().read_line(line[2:])

    def _read_kind(self, kind: str) -> None:
        self.kind = kind

    def _read_dec_type(self, dec_type: str) -> None:
        self.dec_type = dec_type

    def _read_rep_type(self, rep_type: str) -> None:
        self.rep_type = rep_type

    def _read_constant(self, constant: str) -> None:
        self.constant = constant

    def _read_flags(self, *flags: str) -> None:
        logger.warning('flags are currently ignored!')

    def _read_comparability(self, comparability_string: str) -> None:
        self.comparability = int(comparability_string)

    def build(self) -> VarDecl:
        assert self.kind
        assert self.dec_type
        assert self.rep_type
        return VarDecl(name=self.name,
                       dec_type=self.dec_type,
                       rep_type=self.rep_type,
                       comparability=self.comparability,
                       constant=self.constant)
