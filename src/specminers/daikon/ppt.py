# -*- coding: utf-8 -*-
__all__ = ('PptType', 'VarDecl', 'ProgramPoint')

from typing import Iterator, List, Tuple, Optional, Sequence
import enum

import attr

from .loader import LineBuffer, LineLoader
from .vardecl import VarDecl, VarDeclLoader


class PptType(enum.Enum):
    enter = "enter"
    exit = "exit"
    cls = "class"
    subexit = "subexit"
    obj = "object"
    point = "point"


@attr.s(frozen=True, str=False, slots=True)
class ProgramPoint:
    name: str = attr.ib()
    variables: Tuple[VarDecl, ...] = attr.ib(converter=tuple)
    typ: PptType = attr.ib(default=PptType.point)

    @property
    def lines(self) -> List[str]:
        ls = [f'ppt {self.name}', 'ppt-type {self.typ.value}']
        for var in self.variables:
            ls += var.lines
        return ls

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
        self.typ = typ

    def _read_variable(self, name: str) -> None:
        variable = VarDeclLoader.from_line_buffer(name=name, lines=self.lines)
        self.variables.append(variable)

    def build(self) -> ProgramPoint:
        assert self.typ
        return ProgramPoint(self.name, self.variables, self.typ)
