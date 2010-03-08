#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: rtmgr

Implementation of the command for controlling managers.

'''

__version__ = '$Revision: $'
# $Source$


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError, FailedToLoadModuleError, \
                               FailedToUnloadModuleError, \
                               FailedToCreateComponentError, \
                               FailedToDeleteComponentError
from rtctree.tree import create_rtctree, InvalidServiceError, \
                         FailedToNarrowRootNamingError, \
                         NonRootPathError
from rtctree.path import parse_path
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def get_manager(cmd_path, full_path, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't configure a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return None

    if not path[-1]:
        # There was a trailing slash - ignore it
        path = path[:-1]

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return None

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return tree, None
    if not object.is_manager:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
manager.'.format(sys.argv[0], cmd_path)
        return tree, None

    return tree, object

def load_module(cmd_path, full_path, module_path, init_func, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    if not mgr:
        return 1

    try:
        mgr.load_module(module_path, init_func)
    except FailedToLoadModuleError:
        print >>sys.stderr, '{0}: Failed to load module {1}'.format(\
                sys.argv[0], module_path)
        return 1

    return 0


def unload_module(cmd_path, full_path, module_path, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    if not mgr:
        return 1

    try:
        mgr.unload_module(module_path)
    except FailedToUnloadModuleError:
        print >>sys.stderr, '{0}: Failed to unload module {1}'.format(\
                sys.argv[0], module_path)
        return 1

    return 0


def create_component(cmd_path, full_path, module_name, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    if not mgr:
        return 1

    try:
        mgr.create_component(module_name)
    except FailedToCreateComponentError:
        print >>sys.stderr, '{0}: Failed to create component from module \
{1}'.format(sys.argv[0], module_name)
        return 1

    return 0


def delete_component(cmd_path, full_path, instance_name, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    if not mgr:
        return 1

    try:
        mgr.delete_component(instance_name)
    except FailedToDeleteComponentError, e:
        print >>sys.stderr, '{0}: Failed to delete component {1}'.format(\
                sys.argv[0], instance_name)
        return 1

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path> <command> [args]
Control a manager, adding and removing shared libraries and components. To
set a mananger's configuration, use rtconf.

A command should be one of:
    load, unload, create, delete

load <file system path> <init function>
Load a shared library (DLL file or .so file) into the manager.

unload <file system path>
Unload a shared library (DLL file or .so file) from the manager.

create <module name>
Create a new component instance from a loaded shared library.
Properties of the new component can be set by specifying them as part of the
module name argument, prefixed by a question mark. For example, to set the
instance name of a new component of type ConsoleIn, use:
    rtmgr manager.mgr create ConsoleIn?instance_name=blag

delete <instance name>
Delete a component instance from the manager, destroying it.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if len(args) > 2:
        cmd_path = args[0]
        cmd = args[1]
        args = args[2:]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = cmd_path_to_full_path(cmd_path)

    if cmd == 'load':
        if len(args) != 2:
            print >>sys.stderr, '{0}: Incorrect number of arguments for load \
command.'.format(sys.argv[0])
            return 1
        return load_module(cmd_path, full_path, args[0], args[1], tree)
    elif cmd == 'unload':
        if len(args) != 1:
            print >>sys.stderr, '{0}: Incorrect number of arguments for \
unload command.'.format(sys.argv[0])
            return 1
        return unload_module(cmd_path, full_path, args[0], tree)
    elif cmd == 'create':
        if len(args) != 1:
            print >>sys.stderr, '{0}: Incorrect number of arguments for \
create command.'.format(sys.argv[0])
            return 1
        return create_component(cmd_path, full_path, args[0], tree)
    elif cmd == 'delete':
        if len(args) != 1:
            print >>sys.stderr, '{0}: Incorrect number of arguments for \
delete command.'.format(sys.argv[0])
            return 1
        return delete_component(cmd_path, full_path, args[0], tree)

    print >>sys.stderr, usage
    return 1


# vim: tw=79

