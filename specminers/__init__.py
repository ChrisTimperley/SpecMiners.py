# -*- coding: utf-8 -*-
"""
specminers provides a Python wrapper around several popular specification
mining tools.
"""
import docker
import attr


class MiningTool:
    pass


@attr.s(frozen=True)
class Daikon(MiningTool):
    image: str = attr.ib(default='christimperley/daikon')

    def __call__(self, *filenames: str) -> None:
        # TODO copy each file into the container
        # TODO compose command
        # TODO call command
        # TODO it's probably easier to just create a container per command
        return
