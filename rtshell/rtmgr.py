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
import os.path
import rtctree.tree
import rtctree.path
import sys

import rtshell
import rts_exceptions
import path


def get_manager(cmd_path, full_path, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotAManagerError(cmd_path)

    if not path[-1]:
        # There was a trailing slash - ignore it
        path = path[:-1]

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    object = tree.get_node(path)
    if not object:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not object.is_manager:
        raise rts_exceptions.NotAManagerError(cmd_path)
    return tree, object

def load_module(cmd_path, full_path, module_path, init_func, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    mgr.load_module(module_path, init_func)


def unload_module(cmd_path, full_path, module_path, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    mgr.unload_module(module_path)


def create_component(cmd_path, full_path, module_name, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    mgr.create_component(module_name)


def delete_component(cmd_path, full_path, instance_name, tree=None):
    tree, mgr = get_manager(cmd_path, full_path, tree)
    mgr.delete_component(instance_name)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Create and remove components with a manager.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--create', dest='mod_name', action='store',
            type='string', default='', help='Create a new component instance '\
            'from the specified loaded module. Properties of the new '\
            'component an be specified after the module name prefixed with a '\
            'question mark. e.g. ConsoleIn?instance_name=bleg')
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
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

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
    full_path = path.cmd_path_to_full_path(args[0])

    if (not options.mod_path_u and not options.mod_path and not
            options.instance_name and not options.mod_name):
        print >>sys.stderr, '{0}: No actions specified.'.format(sys.argv[0])
        print >>sys.stderr, usage
        return 1

    try:
        if options.mod_path_u:
            # Unload a module
            unload_module(args[0], full_path, options.mod_path_u, tree)
        if options.mod_path:
            # Load a module
            if not options.init_func:
                print >>sys.stderr, '{0}: No initialisation function '\
                        'specified.'.format(os.path.basename(sys.argv[0]))
                return 1
            load_module(args[0], full_path, options.mod_path,
                    options.init_func, tree)
        if options.instance_name:
            # Delete a component
            delete_component(args[0], full_path, options.instance_name, tree)
        if options.mod_name:
            # Create a component
            create_component(args[0], full_path, options.mod_name, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

