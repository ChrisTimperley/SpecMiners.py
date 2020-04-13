# -*- coding: utf-8 -*-
__all__ = ('TraceRecord', 'TraceRecordVariable')

from typing import Iterator, Mapping, Optional, Union
import typing

import attr

from ..vardecl import VarDecl

if typing.TYPE_CHECKING:
    from .ppt import ProgramPoint


@attr.s(slots=True, frozen=True, auto_attribs=True)
class TraceRecordVariable:
    variable: VarDecl
    value: Union[str, int, float]
    modified: int = attr.ib(default=0)

    @property
    def name(self) -> str:
        return self.variable.name


@attr.s(slots=True, frozen=True, auto_attribs=True)
class TraceRecord(Mapping[str, TraceRecordVariable]):
    ppt: 'ProgramPoint'
    nonce: Optional[int]
    _values: Mapping[str, Union[str, int, float]]
    _modified: Mapping[str, int]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[str]:
        yield from self.ppt

    def __getitem__(self, variable_name: str) -> TraceRecordVariable:
        variable = self.ppt[variable_name]
        value = self._values[variable_name]
        modified = self._modified[variable_name]
        return TraceRecordVariable(variable, value, modified)
