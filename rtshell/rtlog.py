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

Implementation of the logging command.

'''


import optparse
import os
import os.path
import rtctree.tree
import rtctree.utils
import sys
import threading
import time
import traceback
import OpenRTM_aist
import RTC

import comp_mgmt
import modmgr
import path
import port_types
import rtlog_comps
import rts_exceptions
import rtshell
import simpkl_log
import text_log


def record_log(raw_paths, options, tree=None):
    event = threading.Event()

    if options.end is not None and options.end < 0:
        raise rts_exceptions.BadEndPointError
    if options.end is None and options.index:
        print >>sys.stderr, '{0}: WARNING: --index has no effect without '\
                '--end'.format(os.path.basename(sys.argv[0]))

    mm = modmgr.ModuleMgr(verbose=options.verbose, paths=options.paths)
    mm.load_mods_and_poas(options.modules)
    if options.verbose:
        print >>sys.stderr, \
                'Pre-loaded modules: {0}'.format(mm.loaded_mod_names)

    if options.timeout is not None:
        print >>sys.stderr, 'Recording for {0}s.'.format(options.timeout)
    else:
        if options.end is not None:
            if options.index:
                print >>sys.stderr, 'Recording {0} entries.'.format(
                        int(options.end))
            else:
                end_str = time.strftime('%Y-%m-%d %H:%M:%S',
                        time.localtime(options.end))
                print >>sys.stderr, 'Recording until {0} ({1}).'.format(
                        end_str, options.end)

    if options.logger == 'simpkl':
        l_type = simpkl_log.SimplePickleLog
    elif options.logger == 'text':
        l_type = text_log.TextLog
    else:
        raise rts_exceptions.BadLogTypeError(options.logger)

    sources = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [s[0] for s in sources]
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(sources, mm, tree)
    port_types.require_all_input(port_specs)
    if options.verbose:
        print >>sys.stderr, \
                'Port specifications: {0}'.format([str(p) for p in port_specs])

    if options.end is None:
        end = -1 # Send -1 as the default
    else:
        end = options.end
    comp_name, mgr = comp_mgmt.make_comp('rtlog_recorder', tree,
            rtlog_comps.Recorder, port_specs, event=event,
            logger_type=l_type, filename=options.filename,
            lims_are_ind=options.index, end=end,
            verbose=options.verbose, rate=options.exec_rate)
    if options.verbose:
        print >>sys.stderr, 'Created component {0}'.format(comp_name)
    try:
        comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
        comp_mgmt.connect(comp, port_specs, tree)
        comp_mgmt.activate(comp)
    except Exception, e:
        #comp_mgmt.shutdown(mgr)
        raise e
    try:
        if options.timeout is not None:
            event.wait(options.timeout)
            comp_mgmt.disconnect(comp)
            comp_mgmt.deactivate(comp)
        elif options.end is not None:
            event.wait()
            comp_mgmt.disconnect(comp)
            comp_mgmt.deactivate(comp)
        else:
            while True:
                raw_input()
            # The manager will catch the Ctrl-C and shut down itself, so don't
            # disconnect/deactivate the component
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    tree.give_away_orb()
    del tree
    comp_mgmt.shutdown(mgr)


def play_log(raw_paths, options, tree=None):
    event = threading.Event()

    if not options.filename:
        raise rts_exceptions.NoLogFileNameError
    if options.start is not None and options.start < 0:
        raise rts_exceptions.BadStartPointError
    if options.end is not None and options.end < 0:
        raise rts_exceptions.BadEndPointError
    if options.end is None and options.start is None and options.index:
        print >>sys.stderr, '{0}: WARNING: --index has no effect without '\
                '--start or --end'.format(os.path.basename(sys.argv[0]))

    mm = modmgr.ModuleMgr(verbose=options.verbose, paths=options.paths)
    mm.load_mods_and_poas(options.modules)
    if options.verbose:
        print >>sys.stderr, \
                'Pre-loaded modules: {0}'.format(mm.loaded_mod_names)

    if options.timeout is not None:
        print >>sys.stderr, 'Playing for {0}s.'.format(options.timeout)
    else:
        if options.end is not None:
            if options.start is not None:
                if options.index:
                    print >>sys.stderr, 'Playing from entry {0} to entry '\
                            '{1}.'.format(int(options.start), int(options.end))
                else:
                    start_str = time.strftime('%Y-%m-%d %H:%M:%S',
                            time.localtime(options.start))
                    end_str = time.strftime('%Y-%m-%d %H:%M:%S',
                            time.localtime(options.end))
                    print >>sys.stderr, 'Playing from {0} ({1}) until {2} '\
                            '({3}).'.format(start_str, options.start, end_str,
                                    options.end)
            else:
                if options.index:
                    print >>sys.stderr, 'Playing {0} entries.'.format(
                            int(options.end))
                else:
                    end_str = time.strftime('%Y-%m-%d %H:%M:%S',
                            time.localtime(options.end))
                    print >>sys.stderr, 'Playing until {0} ({1}).'.format(
                            end_str, options.end)
        elif options.start is not None:
            if options.index:
                print >>sys.stderr, 'Playing from entry {0}.'.format(
                        int(options.start))
            else:
                start_str = time.strftime('%Y-%m-%d %H:%M:%S',
                        time.localtime(options.start))
                print >>sys.stderr, 'Playing from {0} ({1}).'.format(start_str,
                        options.start)

    if options.logger == 'simpkl':
        l_type = simpkl_log.SimplePickleLog
    elif options.logger == 'text':
        raise rts_exceptions.UnsupportedLogTypeError('text', 'playback')
    else:
        raise rts_exceptions.BadLogTypeError(options.logger)

    targets = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [t[0] for t in targets]
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(targets, mm, tree)
    if options.verbose:
        print >>sys.stderr, \
                'Port specifications: {0}'.format([str(p) for p in port_specs])
    port_types.require_all_output(port_specs)

    if options.start is None:
        start = 0 # Send 0 as the default
    else:
        start = options.start
    if options.end is None:
        end = -1 # Send -1 as the default
    else:
        end = options.end
    comp_name, mgr = comp_mgmt.make_comp('rtlog_player', tree,
            rtlog_comps.Player, port_specs, event=event, logger_type=l_type,
            filename=options.filename, lims_are_ind=options.index, start=start,
            end=end, scale_rate=options.rate, abs_times=options.abs_times,
            ignore_times=options.ig_times, verbose=options.verbose,
            rate=options.exec_rate)
    if options.verbose:
        print >>sys.stderr, 'Created component {0}'.format(comp_name)
    comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
    comp_mgmt.connect(comp, port_specs, tree)
    comp_mgmt.activate(comp)
    try:
        if options.timeout is not None:
            event.wait(options.timeout)
            comp_mgmt.disconnect(comp)
            try:
                comp_mgmt.deactivate(comp)
            except rts_exceptions.DeactivateError:
                # Don't care about this because the component will be shut down
                # soon anyway
                pass
        #elif options.end is not None:
        else:
            event.wait()
            comp_mgmt.disconnect(comp)
            try:
                comp_mgmt.deactivate(comp)
            except rts_exceptions.DeactivateError:
                # Don't care about this because the component will be shut down
                # soon anyway
                pass
        #else:
            #while True:
                #raw_input()
            # The manager will catch the Ctrl-C and shut down itself, so don't
            # disconnect/deactivate the component
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    tree.give_away_orb()
    del tree
    comp_mgmt.shutdown(mgr)


def display_info(options):
    if not options.filename:
        raise rts_exceptions.NoLogFileNameError

    if options.logger == 'simpkl':
        l_type = simpkl_log.SimplePickleLog
    elif options.logger == 'text':
        raise rts_exceptions.UnsupportedLogTypeError('text', 'inspection')
    else:
        raise rts_exceptions.BadLogTypeError(options.logger)

    mm = modmgr.ModuleMgr(verbose=options.verbose, paths=options.paths)
    mm.load_mods_and_poas(options.modules)
    if options.verbose:
        print >>sys.stderr, \
                'Pre-loaded modules: {0}'.format(mm.loaded_mod_names)

    statinfo = os.stat(options.filename)
    size = statinfo.st_size
    if size > 1024 * 1024 * 1024: # GiB
        size_str = '{0:.2f}GiB ({1}B)'.format(size / (1024.0 * 1024 * 1024), size)
    elif size > 1024 * 1024: # MiB
        size_str = '{0:.2f}MiB ({1}B)'.format(size / (1024.0 * 1024), size)
    elif size > 1024: # KiB
        size_str = '{0:.2f}KiB ({1}B)'.format(size / 1024.0, size)
    else:
        size_str = '{0}B'.format(size)
    log = l_type(filename=options.filename, mode='r', verbose=options.verbose)

    start_time, port_specs = log.metadata
    start_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
            time.localtime(start_time))
    first_ind, first_time = log.start
    first_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
            time.localtime(first_time.float))
    end_ind, end_time = log.end
    end_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
            time.localtime(end_time.float))

    print 'Name: {0}'.format(options.filename)
    print 'Size: ' + size_str
    print 'Start time: {0} ({1})'.format(start_time_str, start_time)
    print 'First entry time: {0} ({1})'.format(first_time_str, first_time)
    print 'End time: {0} ({1})'.format(end_time_str, end_time)
    print 'Number of entries: {0}'.format(end_ind + 1)
    for ii, p in enumerate(port_specs):
        print 'Channel {0}'.format(ii + 1)
        print '  Name: {0}'.format(p.name)
        print '  Data type: {0} ({1})'.format(p.type_name, p.type)
        print '  Sources:'
        for r in p.raw:
            print '    {0}'.format(r)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path1>:<port1> [<path2>:<port2>...]
Record data from output ports, or replay data into input ports.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-a', '--absolute-times', dest='abs_times',
            action='store_true', default=False,
            help='Times from the logged data are sent as recorded during '
            'replay, rather than adjusted to the current timeframe. '
            '[Default: %default]')
    parser.add_option('-d', '--display-info', dest='display_info',
            action='store_true', default=False, help='Display the log '
            'information and exit.')
    parser.add_option('-e', '--end', dest='end', action='store', type='float',
            default=None,
            help='Time or entry index to stop recording or playback. Must be '
            'within the bounds of the log. Specify -1 to record forever or '
            'replay to the end of the log. Use --index to specify that this '
            'value is an index. [Default: %default]')
    parser.add_option('-f', '--filename', dest='filename', action='store',
            type='string', default='', help='File name of the log file to '
            'record to/playback from. If not specified for recording, a '
            'default will be created based on the current time. Must be '
            'specified for playback.')
    parser.add_option('--path', dest='paths', action='append', type='string',
            default=[], help='Extra module search paths to add to the '
            'PYTHONPATH.')
    parser.add_option('-i', '--index', dest='index', action='store_true',
            default=False, help='Interpret the start and end values as entry '
            'indices. [Default: %default]')
    parser.add_option('-l', '--logger', dest='logger', action='store',
            type='string', default='simpkl', help='The type of logger to '
            'use. The default is the SimplePickle logger. Alternatively, '
            'the text logger (specify using "text") may be used. The text '
            'logger does not support playback.')
    parser.add_option('-m', '--mod', dest='modules', action='append',
            type='string', default=[],
            help='Extra modules to import. If automatic module loading '
            'struggles with your data types, try listing the modules here. '
            'The module and its __POA partner will be imported.')
    parser.add_option('-n', '--ignore-times', dest='ig_times',
            action='store_true', default=False, help='Ignore the log '
            'timestamps and play back a fixed number of entries per '
            'execution. Use --rate to change the number played back per '
            'execution. The value of --rate will be treated as an integer '
            'in this case.')
    parser.add_option('-p', '--play', dest='play', action='store_true',
            default=False, help='Replay mode. [Default: %default]')
    parser.add_option('-r', '--rate', dest='rate', action='store',
            type='float', default=1.0,
            help='Scale the playback speed of the log. [Default: %default]')
    parser.add_option('-s', '--start', dest='start', action='store',
            type='float', default=None,
            help='Time or entry index to start playback from. Must be within '
            'the bounds of the log. Use --index to specify that this value '
            'is an index. [Default: %default]')
    parser.add_option('-t', '--timeout', dest='timeout', action='store',
            type='float', default=None, help='Record/replay data for this '
            'many seconds. This option overrides --start/--end.')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-x', '--exec-rate', dest='exec_rate', action='store',
            type='float', default=100.0,
            help='Specify the rate in Hertz at which to run the component. '
            '[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if len(args) < 1 and not options.display_info:
        print >>sys.stderr, usage
        return 1

    try:
        if options.display_info:
            display_info(options)
        elif options.play:
            play_log([path.cmd_path_to_full_path(p) for p in args],
                    options, tree)
        else:
            record_log([path.cmd_path_to_full_path(p) for p in args],
                    options, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0

