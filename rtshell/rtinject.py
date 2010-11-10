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

Implementation of the command to print data sent by ports to the console.

'''


import OpenRTM_aist
import optparse
import RTC
import rtctree.tree
import rtctree.utils
import sys
import threading
import time
import traceback

import comp_mgmt
import eval_const
import path
import port_types
import rtinject_comp
import rtshell
import user_mods


def write_to_ports(raw_paths, options, tree=None):
    event = threading.Event()

    mods = user_mods.load_mods_and_poas(options.type_mods) + \
            [user_mods.PreloadedModule('RTC', RTC)]
    if options.verbose:
        print >>sys.stderr, \
                'Loaded modules: {0}'.format([str(m) for m in mods])
    val = eval_const.eval_const(options.const, mods)
    if options.verbose:
        print >>sys.stderr, 'Evaluated constant to {0}'.format(val)
    if options.timeout == -1:
        max = options.max
        if options.verbose:
            print >>sys.stderr, 'Will run {0} times.'.format(max)
    else:
        max = -1
        if options.verbose:
            print >>sys.stderr, 'Will stop after {0}s'.format(options.timeout)

    targets = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [t[0] for t in targets]
        tree = rtctree.tree.create_rtctree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(targets, mods, tree)
    port_types.require_all_output(port_specs)
    if options.verbose:
        print >>sys.stderr, \
                'Port specifications: {0}'.format([str(p) for p in port_specs])

    comp_name, mgr = comp_mgmt.make_comp('rtinject_writer', tree,
            rtinject_comp.Writer, port_specs, event=event, rate=options.rate,
            max=max, val=val)
    if options.verbose:
        print >>sys.stderr, 'Created component {0}'.format(comp_name)
    comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
    comp_mgmt.connect(comp, port_specs, tree)
    comp_mgmt.activate(comp)
    try:
        if options.timeout != -1:
            event.wait(options.timeout)
        else:
            event.wait()
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    tree.give_away_orb()
    del tree
    comp_mgmt.disconnect(comp)
    comp_mgmt.deactivate(comp)
    comp_mgmt.shutdown(mgr)
    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path1>:<port1> [<path2>:<port2>...]
Write a constant value to one or more ports.

By default, the value is written once. Options are available to write a set
number of times, or write regularly for a specified length of time.

''' + rtshell.RTSH_PATH_USAGE + '''
A connection will be made to the port using the default connection settings
compatible with the port.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--const', dest='const', action='store',
            type='string', default='',
            help='The constant value to send, as a Python expression. \
Required.')
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('-m', '--type-mod', dest='type_mods', action='store',
            type='string', default='',
            help='Specify the module containing the data type. This option \
must be supplied if the data type is not defined in the RTC modules supplied \
with OpenRTM-aist. This module and the __POA module will both be imported.')
    parser.add_option('-n', '--number', dest='max', action='store',
            type='int', default='1',
            help='Specify the number of times to write to the port. \
[Default: %default]')
    parser.add_option('-r', '--rate', dest='rate', action='store',
            type='float', default=1.0,
            help='Specify the rate in Hertz at which to emit data. \
[Default: %default]')
    parser.add_option('-t', '--timeout', dest='timeout', action='store',
            type='float', default=-1, help='Write data for this many seconds, \
then stop. Specify -1 for no timeout. This option overrides --number. \
[Default: %default]')
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

    if len(args) < 1:
        print >>sys.stderr, usage
        return 1

    try:
        write_to_ports([path.cmd_path_to_full_path(p) \
                for p in args], options, tree=tree)
    except Exception, e:
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1
    return 0

