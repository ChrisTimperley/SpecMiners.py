# -*- coding: utf-8 -*-
__all__ = ('Daikon',)

import contextlib
import pkg_resources
import os
import shlex

from loguru import logger
import dockerblade
import attr

from ..docker_tool import DockerTool


@attr.s(frozen=True)
class Daikon(DockerTool):
    client: dockerblade.DockerDaemon = \
        attr.ib(default=dockerblade.DockerDaemon())
    IMAGE = 'specminers/daikon'
    _DOCKER_DIRECTORY = os.path.dirname(pkg_resources.resource_filename(__name__, 'Dockerfile'))  # noqa

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
