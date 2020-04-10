# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional, Mapping, Sequence, Iterator, Any
from enum import Enum
from collections import OrderedDict
import os
import shlex

import docker
import attr


def escape(val: Any) -> str:
    """Escapes a primitive value for inclusion within a Daikon file."""
    if isinstance(val, str):
        val = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{val}"'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    return val


def escape_if_not_none(val: Any) -> Optional[str]:
    return val if val is None else escape(val)


class PptType(Enum):
    enter = "enter"
    exit = "exit"
    cls = "class"
    subexit = "subexit"
    obj = "object"
    point = "point"


@attr.s(frozen=True, str=False, slots=True)
class VarDecl:
    name: str = attr.ib()
    dec_type: str = attr.ib()
    rep_type: str = attr.ib()
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

    def __str__(self) -> str:
        return '\n'.join(self.lines)


@attr.s(frozen=True, str=False)
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


class Declarations(Mapping[str, ProgramPoint]):
    def __init__(self, points: Sequence[ProgramPoint]) -> None:
        self.__points = OrderedDict((p.name, p) for p in points)

    def __len__(self) -> int:
        return len(self.__points)

    def __getitem__(self, name: str) -> ProgramPoint:
        return self.__points[name]

    def __iter__(self) -> Iterator[str]:
        yield from self.__points

    @property
    def lines(self) -> List[str]:
        ls = ['decl-version 2.0', 'var-comparability none']
        for ppt in self.values():
            ls += ppt.lines
        return ls

    def __str__(self) -> str:
        return '\n'.join(self.lines)

    def save(self, filename: str) -> None:
        with open(filename, 'w') as f:
            f.write(str(self))


@attr.s(frozen=True)
class Daikon:
    client = attr.ib(default=docker.from_env())
    image: str = attr.ib(default='christimperley/daikon')

    def __call__(self, *filenames: str) -> str:
        """Executes the Daikon binary."""
        # TODO ensure given files exists
        assert filenames, "expected one or more filenames."

        ctr_dir = '/tmp/.specminers'
        host_to_ctr_fn = {fn: os.path.join(ctr_dir, os.path.basename(fn))
                          for fn in filenames}
        ctr_filenames = [fn for fn in host_to_ctr_fn.values()]
        volumes = {fn_host: {'bind': fn_ctr, 'mode': 'ro'}
                   for fn_host, fn_ctr in host_to_ctr_fn.items()}

        command = (
            'java daikon.Daikon '
            '--no_show_progress --no_text_output --noversion '
            '-o /tmp/mined.inv.tgz '
            f"{' '.join(shlex.quote(f) for f in ctr_filenames)} "
            '&> /dev/null '
            '&& java daikon.PrintInvariants /tmp/mined.inv.tgz')
        command = f'/bin/bash -c "{command}"'
        output = self.client.containers.run(self.image, command,
                                            volumes=volumes).decode('utf-8')
        return output


if __name__ == '__main__':
    dir_here = os.path.dirname(__file__)
    dir_example = os.path.abspath(os.path.join(dir_here, '../example'))
    daikon = Daikon()
    filenames = [os.path.join(dir_example, 'ardu.decls'),
                 os.path.join(dir_example, 'ardu.dtrace')]
    out = daikon(*filenames)
    print(out)
