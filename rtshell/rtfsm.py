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

Implementation of the fsm configuration command.

'''

from __future__ import print_function


import optparse
import os
import rtctree.exceptions
import rtctree.path
import rtctree.tree
import rtctree.utils
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def manage_fsm(tgt_raw_path, tgt_full_path, command, argument, options, tree=None):
    path, port = rtctree.path.parse_path(tgt_full_path)
    if port:
        raise rts_exceptions.NotAComponentError(tgt_raw_path)
    if not path[-1]:
        raise rts_exceptions.NotAComponentError(tgt_raw_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(path)
    rtc = tree.get_node(path)
    if rtc.is_zombie:
        raise rts_exceptions.ZombieObjectError(path)
    if not rtc.is_component:
        raise rts_exceptions.NotAComponentError(path)

    fsm = rtc.get_extended_fsm_service()

    if command == 'getstate':
        print(fsm.get_current_state())
    elif command == 'geteventprofiles':
        (ret, struct) = fsm.get_fsm_structure()
        ps = []
        for p in struct.event_profiles:
            ps.append(p.name + ':' + p.data_type)
        print(','.join(ps))
    elif command == 'getstructure':
        (ret, struct) = fsm.get_fsm_structure()
        print(struct.structure)
    elif command == 'seteventprofiles':
        (ret, struct) = fsm.get_fsm_structure()
        struct.event_profiles = argument
        fsm.set_fsm_structure(struct)
    elif command == 'setstructure':
        (ret, struct) = fsm.get_fsm_structure()
        struct.structure = argument
        fsm.set_fsm_structure(struct)

def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <component path> [getstate|get[set]eventprofiles|get[set]structure]
Configure FSM behavior of the component.'''
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

    if len(args) < 2:
        print('{0}: No target component and command '\
            'specified.'.format(sys.argv[0]), file=sys.stderr)
        return 1

    full_path = path.cmd_path_to_full_path(args[0])
    
    command = args[1]
    argument = None
    if command == 'seteventprofiles':
        if len(args) != 3:
            print('{0}: No argument to {1} command '\
                'specified.'.format(sys.argv[0], command), file=sys.stderr)
            return 1
        argument = []
        for p in args[2].split(','):
            argument.append(p.split(':'))
    elif command == 'setstructure':
        if len(args) != 3:
            print('{0}: No argument to {1} command '\
                'specified.'.format(sys.argv[0], command), file=sys.stderr)
            return 1
        with open(args[2], mode = 'r', encoding = 'utf-8') as fh:
            argument = fh.read()
        if not argument:
            print('{0}: Unable to read file {1} specified to {2} command.'\
                .format(sys.argv[0], args[2], command), file=sys.stderr)
            return 1
            
    try:
        manage_fsm(args[0], full_path, command, argument, options, tree=tree)
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(sys.argv[0], e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

