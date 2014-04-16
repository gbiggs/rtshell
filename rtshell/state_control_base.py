#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Base for the scripts that change component state.

'''


import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions
import rtshell


def alter_component_states(action, paths, options, tree=None):
    cmd_paths, fps = zip(*paths)
    pathports = [rtctree.path.parse_path(fp) for fp in fps]
    for ii, p in enumerate(pathports):
        if p[1]:
            raise rts_exceptions.NotAComponentError(cmd_paths[ii])
        if not p[0][-1]:
            raise rts_exceptions.NotAComponentError(cmd_paths[ii])
    paths, ports = zip(*pathports)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)

    for ii, p in enumerate(paths):
        if not tree.has_path(p):
            raise rts_exceptions.NoSuchObjectError(cmd_paths[ii])
        object_ = tree.get_node(p)
        if object_.is_zombie:
            raise rts_exceptions.ZombieObjectError(cmd_paths[ii])
        if not object_.is_component:
            raise rts_exceptions.NotAComponentError(cmd_paths[ii])
        action(object_, options.ec_index)


def base_main(description, action, argv=None, tree=None):
    usage = '''Usage: %prog [options] <path> [<path> ...]
{0}'''.format(description)
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-e', '--exec_context', dest='ec_index', type='int',
            action='store', default=0, help='Index of the execution context '\
            'to change state in. [Default: %default]')
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

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: No components specified.'.format(
                os.path.basename(sys.argv[0]))
        return 1
    paths = [(p, path.cmd_path_to_full_path(p)) for p in args]

    try:
        alter_component_states(action, paths, options, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

