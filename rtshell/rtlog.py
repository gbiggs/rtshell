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
import rtlog_comps
import rtshell
import user_mods


def record_log(raw_paths, options, tree=None):
    event = threading.Event()

    if options.timeout == -1:
        if options.number == 0:
            if options.end != -1:
                print >>sys.stderr, 'Record until {0}.'.format(options.end)
        else:
            print >>sys.stderr, 'Record {0} entries.'.format(options.number)
    else:
        print >>sys.stderr, 'Record for {0}s'.format(options.timeout)

    sources = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [t[0] for s in sources]
        tree = rtctree.tree.create_rtctree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(sources, mods, tree)
    port_types.require_all_input(port_specs)
    if options.verbose:
        print >>sys.stderr, \
                'Port specifications: {0}'.format([str(p) for p in port_specs])

    if not options.filename:
        options.filename = 'rtlog_{0}.rtl'.format(time.time())
    if options.logger == 'simpkl':
        logger = simpkl_log.SimplePickleLog(filename=options.filename,
                mode='w', meta=port_specs, verbose=options.verbose)
    elif options.logger == 'text':
        logger = textlog.TextLogger(filename=options.filename,
                mode='w', verbose=options.verbose)
    else:
        print >>sys.stderr, '{0}: Invalid logger type: {1}',format(sys.argv[0],
                options.logger)
        return 1

    comp_name, mgr = comp_mgmt.make_comp('rtlog_recorder', tree,
            rtlog_comps.Recorder, port_specs, event=event,
            logger=logger, lims_are_ind=options.index, end=options.end)
    if options.verbose:
        print >>sys.stderr, 'Created component {0}'.format(comp_name)
    comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
    comp_mgmt.connect(comp, port_specs, tree)
    comp_mgmt.activate(comp)
    try:
        if options.timeout != -1:
            event.wait(options.timeout)
            comp_mgmt.disconnect(comp)
            comp_mgmt.deactivate(comp)
        else:
            while True:
                raw_input()
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    tree.give_away_orb()
    del tree
    comp_mgmt.shutdown(mgr)
    return 0


def play_log(raw_paths, options, tree=None):
    event = threading.Event()

    if options.timeout == -1:
        if options.number == 0:
            if options.end != -1:
                print >>sys.stderr, 'Play from {0} until {1}.'.format(
                        options.start, options.end)
        else:
            print >>sys.stderr, 'Play {0} entries.'.format(options.number)
    else:
        print >>sys.stderr, 'Play for {0}s'.format(options.timeout)

    targets = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [t[0] for t in targets]
        tree = rtctree.tree.create_rtctree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(targets, mods, tree)
    port_types.require_all_output(port_specs)
    if options.verbose:
        print >>sys.stderr, \
                'Port specifications: {0}'.format([str(p) for p in port_specs])

    comp_name, mgr = comp_mgmt.make_comp('rtlog_player', tree,
            rtlog_comps.Player, port_specs, event=event,
            limits_are_ind=options.index, start=options.start,
            end=options.end_time, num=options.number)
    if options.verbose:
        print >>sys.stderr, 'Created component {0}'.format(comp_name)
    comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
    comp_mgmt.connect(comp, port_specs, tree)
    comp_mgmt.activate(comp)
    try:
        if options.timeout != -1:
            event.wait(options.timeout)
            comp_mgmt.disconnect(comp)
            comp_mgmt.deactivate(comp)
        else:
            while True:
                raw_input()
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    tree.give_away_orb()
    del tree
    comp_mgmt.shutdown(mgr)
    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path1>:<port1> [<path2>:<port2>...]
Record data from output ports, or replay data into input ports.

The default is to record. All specified ports must be output ports. If
replay mode is enabled, all specified ports must be input ports
matching the recorded data's data types.

Options are available to limit the number of items recorded or played
back, change the playback rate, and restrict the played-back items.

''' + rtshell.RTSH_PATH_USAGE + '''
Connections will be made to the ports using the default connection
settings compatible with the port.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-a', '--absolute-times', dest='abs_times',
            action='store_true', default=False,
            help='Times from the logged data are sent as recorded during '\
            'replay, rather than adjusted to the current timeframe. '\
            '[Default: %default]')
    parser.add_option('-e', '--end', dest='end', action='store', type='string',
            default='-1',
            help='Time or entry index to stop recording or playback. Must be '\
                    'within the bounds of the log. Specify -1 to record '\
                    'forever or replay to the end of the log. Use --index to '\
                    'specify that this value is an index. [Default: %default]')
    parser.add_option('-f', '--filename', dest='filename', action='store',
            type='string', default='', help='File name of the log file to '\
                    'record to/playback from. If not specified for '\
                    'recording, a default will be created based on the '\
                    'current time. Must be specified for playback.')
    parser.add_option('-i', '--index', dest='index', action='store_true',
            default=False, help='Interpret the start and end values as entry '\
                    'indices. [Default: %default]')
    parser.add_option('-l', '--logger', dest='logger', action='store',
            type='string', default='simpkl', help='The type of logger to '\
                    'use. The default is the SimplePickle logger. '\
                    'Alternatively, the text logger (specify using "text") '\
                    'may be used. The text logger does not support playback.')
    parser.add_option('-m', '--type-mod', dest='type_mods', action='store',
            type='string', default='',
            help='Specify the module containing the data type. This option '\
                    'must be supplied if the data type is not defined in the '\
                    'RTC modules supplied with OpenRTM-aist. This module and '\
                    'the __POA module will both be imported.')
    parser.add_option('-p', '--play', dest='play', action='store_true',
            default=False, help='Replay mode. [Default: %default]')
    parser.add_option('-r', '--rate', dest='rate', action='store',
            type='float', default=1.0,
            help='Scale the playback speed of the log. [Default: %default]')
    parser.add_option('-s', '--start', dest='start', action='store',
            type='string', default='0.0',
            help='Time or entry index to start playback from. Must be within '\
                    'the bounds of the log. Use --index to specify that this '\
                    'value is an index. [Default: %default]')
    parser.add_option('-t', '--timeout', dest='timeout', action='store',
            type='float', default=-1, help='Record/replay data for this many '\
                    'seconds. Specify -1 for no timeout. This option '\
                    'overrides --number. [Default: %default]')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-x', '--exec-rate', dest='exec_rate', action='store',
            type='float', default=10.0,
            help='Specify the rate in Hertz at which to run the component. '\
                    '[Default: %default]')

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
        if options.play:
            result = replay_log([path.cmd_path_to_full_path(p) for p in args],
                    options, tree)
        else:
            result = record_log([path.cmd_path_to_full_path(p) for p in args],
                    options, tree)
    except Exception, e:
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1
    return result

