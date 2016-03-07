#!python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2015
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

Command to show the current value of the current working directory environment
variable.

'''

from __future__ import print_function

import os
import sys


from rtshell.path import ENV_VAR


def main():
    if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        print('Print the name of the current rtshell working directory.',
                file=sys.stderr)
        return 0
    if ENV_VAR in os.environ:
        print(os.environ[ENV_VAR])
    else:
        print('/')
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

