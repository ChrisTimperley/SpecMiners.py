# -*- coding: utf-8 -*-
import os
import shlex

import docker
import attr


@attr.s(frozen=True)
class Daikon:
    client = attr.ib(default=docker.from_env())
    image: str = attr.ib(default='christimperley/daikon')

    def __call__(self, *filenames: str) -> str:
        """Executes the Daikon binary."""
        # TODO ensure given files exists
        assert filenames, "expected one or more filenames."

        ctr_dir = '/tmp/.specminers'
        host_filenames = filenames
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
