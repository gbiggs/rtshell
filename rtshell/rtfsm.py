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


import argparse
import os
import rtctree.exceptions
import rtctree.path
import rtctree.tree
import rtctree.utils
import rtctree.rtc.RTC
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell

def getstate(fsm, arg):
    result = []
    result.append(fsm.get_current_state())
    return result

def geteventprofiles(fsm, arg):
    result = []
    ret, struct = fsm.get_fsm_structure()
    ps = []
    for p in struct.event_profiles:
        ps.append(p.name + ':' + p.data_type)
    result.append(', '.join(ps))
    return result

def getstructure(fsm, arg):
    result =[]
    ret, struct = fsm.get_fsm_structure()
    result.append(struct.structure)
    return result

def seteventprofiles(fsm, arg):
    ret, struct = fsm.get_fsm_structure()
    struct.event_profiles = []
    for a in arg:
        p = rtctree.rtc.RTC.FsmEventProfile(a[0], a[1])
        struct.event_profiles.append(p)
    fsm.set_fsm_structure(struct)
    return None

def setstructure(fsm, arg):
    ret, struct = fsm.get_fsm_structure()
    struct.structure = arg
    fsm.set_fsm_structure(struct)
    return None

FSM_CMDS = {
    'getstate': getstate,
    'geteventprofiles': geteventprofiles,
    'getstructure': getstructure,
    'seteventprofiles': seteventprofiles,
    'setstructure': setstructure,
}

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

    try:
        cmdfunc = FSM_CMDS[command]
        return cmdfunc(fsm, argument)
    except KeyError:
        raise Exception('unknown command: {0}'.format(command))

def main(argv=None, tree=None):
    cmdkind = FSM_CMDS.keys()
    usage = '''Usage: %prog [options] <component path> [getstate|get[set]eventprofiles|get[set]structure]
Configure FSM behavior of the component.'''
    parser = argparse.ArgumentParser(prog='rtfsm', description='Configure FSM behavior of the component.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %(default)s]')
    parser.add_argument('path', metavar='path', type=str, nargs=1,
            help='Path to component.')
    parser.add_argument('command', metavar='command', type=str, nargs=1,
            choices=cmdkind,
            help='Select from {0}.'.format(', '.join(cmdkind)))
    parser.add_argument('argument', metavar='argument', type=str, nargs='?',
            help=
            'Command "seteventprofiles" takes profiles as the argument (e.g. "toggle:TimedShort,toggle2:TimedString"). ' +
            'Command "setstructure" takes scxml file as the argument.')

    if argv:
        sys.argv = [sys.argv[0]] + argv

    options = parser.parse_args()

    full_path = path.cmd_path_to_full_path(options.path[0])
    
    command = options.command[0]
    argument = None
    if command == 'seteventprofiles':
        if options.argument is None:
            print('{0}: No argument to {1} command '\
                'specified.'.format(sys.argv[0], command), file=sys.stderr)
            return 1
        argument = []
        for p in options.argument.split(','):
            argument.append(p.split(':'))
    elif command == 'setstructure':
        if options.argument is None:
            print('{0}: No argument to {1} command '\
                'specified.'.format(sys.argv[0], command), file=sys.stderr)
            return 1
        with open(options.argument, 'r') as fh:
            argument = fh.read()
        if not argument:
            print('{0}: Unable to read file {1} specified to {2} command.'\
                .format(sys.argv[0], options.argument[0], command), file=sys.stderr)
            return 1
            
    try:
        result = manage_fsm(options.path[0], full_path, command, argument, options, tree=tree)
        if result:
            print('\n'.join(result))
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

