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

Implementation of the command for controlling managers.

'''


import optparse
import os
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import sys

import rtshell
import rtshell.path


def get_manager(cmd_path, full_path, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        # Can't configure a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return None

    if not path[-1]:
        # There was a trailing slash - ignore it
        path = path[:-1]

    if not tree:
        tree = rtctree.tree.create_rtctree(paths=path, filter=[path])
    if not tree:
        return None

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return tree, None
    if object.is_zombie:
        print >>sys.stderr, '{0}: Zombie object.'.format(sys.argv[0])
        return 1
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
    except rtctree.exceptions.FailedToLoadModuleError:
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
    except rtctree.exceptions.FailedToUnloadModuleError:
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
    except rtctree.exceptions.FailedToCreateComponentError:
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
    except rtctree.exceptions.FailedToDeleteComponentError, e:
        print >>sys.stderr, '{0}: Failed to delete component {1}'.format(\
                sys.argv[0], instance_name)
        return 1

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Control a manager, adding and removing shared libraries and components. To
set a mananger's configuration, use rtconf. To view a manager's information,
use rtcat.

If multiple commands are given, they are executed in the order unload, load,
delete, create.

''' + rtshell.RTSH_PATH_USAGE
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--create', dest='mod_name', action='store',
            type='string', default='', help='Create a new component instance '\
            'from the specified loaded module. Properties of the new '\
            'component an be specified after the module name prefixed with a '\
            'question mark. e.g. ConsoleIn?instance_name=blag')
    parser.add_option('-d', '--delete', dest='instance_name', action='store',
            type='string', default='', help='Shut down and delete the '\
            'specified component instance.')
    parser.add_option('-i', '--init-func', dest='init_func', action='store',
            type='string', default='', help='Initialisation function for use '\
            'with the --load option.')
    parser.add_option('-l', '--load', dest='mod_path', action='store',
            type='string', default='', help='Load the module into the '\
            'manager. An initialisation function must be specified using '\
            'the --init-func option.')
    parser.add_option('-u', '--unload', dest='mod_path_u', action='store',
            type='string', default='', help='Unload the module from the '\
            'manager.')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if len(args) != 1:
        print >>sys.stderr, '{0}: No manager specified.'.format(sys.argv[0])
        return 1
    full_path = rtshell.path.cmd_path_to_full_path(args[0])

    if (not options.mod_path_u and not options.mod_path and not
            options.instance_name and not options.mod_name):
        print >>sys.stderr, '{0}: No actions specified.'.format(sys.argv[0])
        print >>sys.stderr, usage
        return 1

    result = 0
    if options.mod_path_u:
        # Unload a module
        loc_result = unload_module(args[0], full_path, options.mod_path_u,
                tree)
        if loc_result != 0:
            result = loc_result
    if options.mod_path:
        # Load a module
        if not options.init_func:
            print >>sys.stderr, '{0}: No initialisation function '\
                    'specified.'.format(sys.argv[0])
            return 1
        loc_result = load_module(args[0], full_path, options.mod_path,
                options.init_func, tree)
        if loc_result != 0:
            result = loc_result
    if options.instance_name:
        # Delete a component
        loc_result = delete_component(args[0], full_path,
                options.instance_name, tree)
        if loc_result != 0:
            result = loc_result
    if options.mod_name:
        # Create a component
        loc_result = create_component(args[0], full_path, options.mod_name,
                tree)
        if loc_result != 0:
            result = loc_result

    return result


# vim: tw=79

