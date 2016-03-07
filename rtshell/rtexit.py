#!/usr/bin/env python2
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

Implementation of the command to make a component exit.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import RTC
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def exit_target(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotAComponentError(cmd_path)

    trailing_slash = False
    if not path[-1]:
        raise rts_exceptions.NotAComponentError(cmd_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)
    if object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not object.is_component:
        raise rts_exceptions.NotAComponentError(cmd_path)

    object.exit()


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Make a component exit.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    if not args:
        # If no path given then can't do anything.
        print('{0}: No component specified.'.format(
                os.path.basename(sys.argv[0])), file=sys.stderr)
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        exit_target(cmd_path, full_path, options, tree)
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), e),
                file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

