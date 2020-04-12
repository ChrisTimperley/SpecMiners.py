# -*- coding: utf-8 -*-
__all__ = ('PptType', 'VarDecl', 'ProgramPoint')

from collections import OrderedDict
from typing import Iterator, List, Mapping, Optional, Sequence
import enum

import attr

from .loader import LineBuffer, LineLoader
from .vardecl import VarDecl, VarDeclLoader


class PptType(enum.Enum):
    enter = 'enter'
    exit = 'exit'
    cls = 'class'
    subexit = 'subexit'
    obj = 'object'
    point = 'point'


@attr.s(frozen=True, str=False, slots=True, auto_attribs=True)
class ProgramPoint(Mapping[str, VarDecl]):
    name: str
    variables: 'OrderedDict[str, VarDecl]'
    typ: PptType = attr.ib(default=PptType.point)

    @classmethod
    def build(cls,
              name: str,
              variables: Sequence[VarDecl],
              typ: PptType = PptType.point
              ) -> 'ProgramPoint':
        variable_dict: 'OrderedDict[str, VarDecl]' = OrderedDict()
        for v in variables:
            variable_dict[v.name] = v
        return ProgramPoint(name, variable_dict, typ)

    @property
    def lines(self) -> List[str]:
        ls = [f'ppt {self.name}', 'ppt-type {self.typ.value}']
        for var in self.variables.values():
            ls += var.lines
        return ls

    def __len__(self) -> int:
        """Returns the number of variables within the program point."""
        return len(self.variables)

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the names of the variables in this program
        point."""
        yield from self.variables

    def __getitem__(self, name: str) -> VarDecl:
        """Fetches a given variable declaration by its name."""
        return self.variables[name]

    def __str__(self) -> str:
        return '\n'.join(self.lines)


@attr.s(auto_attribs=True)
class ProgramPointLoader(LineLoader[ProgramPoint]):
    lines: LineBuffer
    name: str
    typ: Optional[PptType] = attr.ib(default=None)
    variables: List[VarDecl] = attr.ib(factory=list)

    def lookup(self, name: str):
        return {'ppt-type': self._read_type,
                'variable': self._read_variable}[name]

    def has_finished(self) -> bool:
        try:
            return self.lines.peek().startswith('ppt ')
        except StopIteration:
            return True

    def _read_type(self, typ: str) -> None:
        self.typ = PptType[typ]

    def _read_variable(self, name: str) -> None:
        variable = VarDeclLoader.from_line_buffer(name=name, lines=self.lines)
        self.variables.append(variable)

    def build(self) -> ProgramPoint:
        assert self.typ
        return ProgramPoint.build(self.name, self.variables, self.typ)
