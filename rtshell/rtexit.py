#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of the command to make a component exit.

'''


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, get_num_columns_and_rows, \
                            get_terminal_size
import RTC
import sys

from rtshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtshell.path import cmd_path_to_full_path


def exit_target(cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't alter a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        print >>sys.stderr, '{0}: {1}: Not an \
object'.format(sys.argv[0], cmd_path)
        return 1

    if not tree:
        tree = create_rtctree(paths=path, filter=[path])
    if not tree:
        return 1

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    object = tree.get_node(path)
    if object.is_zombie:
        print >>sys.stderr, '{0}: Zombie object.'.format(sys.argv[0])
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
component'.format(sys.argv[0], cmd_path)
        return 1

    if object.exit() == RTC.RTC_OK:
        return 0
    return 1


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
Make a component exit, cleaning up its execution contexts and children.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: No component specified.'.format(sys.argv[0])
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = cmd_path_to_full_path(cmd_path)

    return exit_target(cmd_path, full_path, options, tree)


# vim: tw=79

