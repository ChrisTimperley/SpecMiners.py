# -*- coding: utf-8 -*-
import os

import specminers


def main():
    dir_here = os.path.dirname(__file__)
    daikon = specminers.Daikon()
    daikon.install()
    filenames = [os.path.join(dir_here, 'ardu.decls'),
                 os.path.join(dir_here, 'ardu.dtrace')]
    out = daikon(*filenames)
    print(out)


if __name__ == '__main__':
    main()
