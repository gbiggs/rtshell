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

Create a command to change the current working directory environment variable.

'''


#!/usr/bin/env python

import os
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions


if sys.platform == 'win32':
    SET_CMD = 'set'
    EQUALS = '='
    QUOTE = ''
elif 'SHELL' in os.environ and 'csh' in os.environ['SHELL']:
    SET_CMD = 'setenv'
    EQUALS = ' '
    QUOTE = '"'
else:
    SET_CMD = 'export'
    EQUALS = '='
    QUOTE = '"'


def make_cmd_line(path):
    return '{0} {1}{2}{3}{4}{3}'.format(SET_CMD, path.ENV_VAR, EQUALS,
            QUOTE, path)


def cd(cmd_path, full_path):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotADirectoryError(cmd_path)
    if not path[-1]:
        # Remove trailing slash part
        path = path[:-1]
    tree = rtctree.tree.create_rtctree(paths=path)
    if not tree.has_path(path):
        raise rts_exceptions.NotADirectoryError(cmd_path)
    if not tree.is_directory(path):
        raise rts_exceptions.NotADirectoryError(cmd_path)
    print make_cmd_line(full_path)


def main(argv=None, tree=None):
    if argv:
        sys.argv = [sys.argv[0]] + argv
    if len(sys.argv) < 2:
        # Change to the root dir
        print '{0} {1}{3}{2}/{2}'.format(SET_CMD, ENV_VAR, QUOTE, EQUALS)
        return 0

    # Take the first argument only
    cmd_path = sys.argv[1]

    try:
        if cmd_path == '.' or cmd_path == './':
            # Special case for '.': do nothing
            if ENV_VAR in os.environ:
                print make_cmd_line(os.environ[ENV_VAR])
                return 0
            else:
                print make_cmd_line('/')
                return 0
        elif cmd_path == '..' or cmd_path == '../':
            # Special case for '..': go up one directory
            if ENV_VAR in os.environ and os.environ[ENV_VAR] and \
                    os.environ[ENV_VAR] != '/':
                parent = os.environ[ENV_VAR][:os.environ[ENV_VAR].rstrip('/').rfind('/')]
                if not parent:
                    parent = '/'
                print make_cmd_line(parent)
                return 0
            else:
                print make_cmd_line('/')
                return 0
        else:
            full_path = path.cmd_path_to_full_path(cmd_path)
            cd(cmd_path, full_path)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1


# vim: tw=79

