# -*- coding: utf-8 -*-
"""
This module provides an interface for interacting with Daikon and
reading/writing Daikon's .decl and .dtrace files.
"""
from typing import List, Tuple, Optional, Mapping, Sequence, Iterator, Any
from enum import Enum
from collections import OrderedDict
import contextlib
import pkg_resources
import os
import shlex

from loguru import logger
import docker
import dockerblade
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

    def save(self, filename: str) -> None:
        """Saves the variable declarations to a given file on disk."""
        with open(filename, 'w') as f:
            f.write(str(self))


@attr.s(frozen=True)
class Daikon:
    client: dockerblade.DockerDaemon = \
        attr.ib(default=dockerblade.DockerDaemon())
    IMAGE = 'specminers/daikon'
    _DOCKER_DIRECTORY = os.path.dirname(pkg_resources.resource_filename(__name__, 'Dockerfile'))  # noqa

    @classmethod
    def install(cls, force_reinstall: bool = False) -> None:
        """Ensures that this tool is installed.

        Parameters
        ----------
        force_reinstall: bool
            If :code:`True`, the image for this tool will be rebuilt
            regardless of whether or not it already exists.
        """
        if cls.is_installed() and not force_reinstall:
            return
        with contextlib.closing(docker.from_env()) as docker_client:
            logger.debug(f'building tool image [{cls.IMAGE}]')
            image, _ = docker_client.images.build(path=cls._DOCKER_DIRECTORY,
                                                  tag=cls.IMAGE,
                                                  pull=True)
            logger.debug(f'built tool image [{cls.IMAGE}]')

    @classmethod
    def is_installed(cls) -> bool:
        """Checks whether this tool is installed."""
        with contextlib.closing(docker.from_env()) as docker_client:
            try:
                docker_client.images.get(cls.IMAGE)
            except docker.errors.ImageNotFound:
                return False
            return True

    def __call__(self, *filenames: str) -> str:
        """Executes the Daikon binary.

        Raises
        ------
        ValueError
            If no filenames are provided as input.
        FileNotFoundError
            If a given input file cannot be found.
        RuntimeError
            If the image for the tool has not been installed.
        """
        if not self.is_installed():
            message = f'image for tool is not installed [{self.IMAGE}]'
            raise RuntimeError(message)

        logger.debug(f"running Daikon on files: {', '.join(filenames)}")
        if not filenames:
            raise ValueError('expected one or more filenames as input')

        # ensure that all paths are absolute
        filenames = tuple(os.path.abspath(filename) for filename in filenames)

        for filename in filenames:
            if not os.path.isfile(filename):
                raise FileNotFoundError(filename)

        ctr_dir = '/tmp/.specminers'
        host_to_ctr_fn = {fn: os.path.join(ctr_dir, os.path.basename(fn))
                          for fn in filenames}
        ctr_filenames = [fn for fn in host_to_ctr_fn.values()]
        volumes = {fn_host: {'bind': fn_ctr, 'mode': 'ro'}
                   for fn_host, fn_ctr in host_to_ctr_fn.items()}

        # launch container
        with contextlib.ExitStack() as stack:
            container = self.client.provision(self.IMAGE, volumes=volumes)
            shell = container.shell('/bin/sh')
            stack.callback(container.remove)

            # generate invariants
            command = ('java daikon.Daikon '
                       '--no_show_progress --no_text_output --noversion '
                       '-o /tmp/mined.inv.tgz '
                       f"{' '.join(shlex.quote(f) for f in ctr_filenames)}")
            shell.check_call(command)

            # read invariants
            command = 'java daikon.PrintInvariants /tmp/mined.inv.tgz'
            output = shell.check_output(command)

        logger.debug(f"daikon output:\n{output}")
        return output


if __name__ == '__main__':
    dir_here = os.path.dirname(__file__)
    dir_example = os.path.abspath(os.path.join(dir_here, '../../../example'))
    Daikon.install()
    daikon = Daikon()
    filenames = [os.path.join(dir_example, 'ardu.decls'),
                 os.path.join(dir_example, 'ardu.dtrace')]
    out = daikon(*filenames)
    print(out)
