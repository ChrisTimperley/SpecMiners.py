# -*- coding: utf-8 -*-
"""
specminers provides a Python wrapper around several popular specification
mining tools.
"""
import os

import docker
import attr


class MiningTool:
    pass


@attr.s(frozen=True)
class Daikon(MiningTool):
    client = attr.ib(default=docker.from_env())
    image: str = attr.ib(default='christimperley/daikon')

    def __call__(self, *filenames: str) -> None:
        # TODO ensure given files exists

        ctr_dir = '/tmp/.specminers'
        host_filenames = filenames
        host_to_ctr_fn = {fn: os.path.join(ctr_dir, os.path.basename(fn))
                          for fn in filenames}
        ctr_filenames = [fn for fn in host_to_ctr_fn.values()]
        volumes = {fn_host: {'bind': fn_ctr, 'mode': 'ro'}
                   for fn_host, fn_ctr in host_to_ctr_fn.items()}

        command = ' '.join(["java", "daikon.Daikon"] + ctr_filenames)
        output = self.client.containers.run(self.image, command,
                                            volumes=volumes)

        # TODO parse output
        print(output)


if __name__ == '__main__':
    daikon = Daikon()
    daikon('cool.dtrace')
