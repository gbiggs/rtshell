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

Implementation of the command to print data sent by ports to the console.

'''

from __future__ import print_function

import optparse
import os.path
import rtctree.tree
import rtctree.utils
import sys
import threading
import time
import traceback
import OpenRTM_aist
import RTC

from rtshell import comp_mgmt
from rtshell import modmgr
from rtshell import path
from rtshell import port_types
from rtshell import rtinject_comp
import rtshell


def write_to_ports(raw_paths, options, tree=None):
    event = threading.Event()

    mm = modmgr.ModuleMgr(verbose=options.verbose, paths=options.paths)
    mm.load_mods_and_poas(options.modules)
    if options.verbose:
        print('Pre-loaded modules: {0}'.format(mm.loaded_mod_names),
                file=sys.stderr)

    if options.const:
        val = mm.evaluate(options.const)
        if options.verbose:
            print('Evaluated value to {0}'.format(val), file=sys.stderr)
    else:
        if options.verbose:
            print('Reading values from stdin.', file=sys.stderr)

    if options.timeout == -1:
        max = options.max
        if options.verbose:
            print('Will run {0} times.'.format(max), file=sys.stderr)
    else:
        max = -1
        if options.verbose:
            print('Will stop after {0}s'.format(options.timeout),
                    file=sys.stderr)

    targets = port_types.parse_targets(raw_paths)
    if not tree:
        paths = [t[0] for t in targets]
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)
    port_specs = port_types.make_port_specs(targets, mm, tree)
    port_types.require_all_output(port_specs)
    if options.verbose:
        print('Port specifications: {0}'.format([str(p) for p in port_specs]),
                file=sys.stderr)

    if options.const:
        comp_name, mgr = comp_mgmt.make_comp('rtinject_writer', tree,
                rtinject_comp.Writer, port_specs, event=event, rate=options.rate,
                max=max, val=val)
    else:
        buffer = []
        mutex = threading.RLock()
        comp_name, mgr = comp_mgmt.make_comp('rtinject_writer', tree,
                rtinject_comp.StdinWriter, port_specs, event=event,
                rate=options.rate, max=max, buf=buffer, mutex=mutex)
    if options.verbose:
        print('Created component {0}'.format(comp_name), file=sys.stderr)
    comp = comp_mgmt.find_comp_in_mgr(comp_name, mgr)
    comp_mgmt.connect(comp, port_specs, tree)
    comp_mgmt.activate(comp)
    if options.const:
        try:
            if options.timeout != -1:
                event.wait(options.timeout)
            elif options.max > -1:
                event.wait()
            else:
                if sys.version_info[0] == 3:
                    input()
                else:
                    raw_input()
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
    else:
        # Read stdin until we receive max number of values or Ctrl-C is hit
        val_cnt = 0
        try:
            while val_cnt < max or max < 0:
                l = sys.stdin.readline()
                if not l:
                    break
                if l[0] == '#':
                    continue
                val = mm.evaluate(l)
                with mutex:
                    buffer.append(val)
                val_cnt += 1
        except KeyboardInterrupt:
            pass
        # Wait until the buffer has been cleared
        while True:
            with mutex:
                if not buffer:
                    break
    comp_mgmt.disconnect(comp)
    comp_mgmt.deactivate(comp)
    tree.give_away_orb()
    del tree
    comp_mgmt.shutdown(mgr)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path1>:<port1> [<path2>:<port2>...]
Write a constant value to one or more ports.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--const', dest='const', action='store',
            type='string', default='',
            help='The constant value to send, as a Python expression. If '
            'not specified, values will be read from standard in.')
    parser.add_option('-m', '--mod', dest='modules', action='append',
            type='string', default=[],
            help='Extra modules to import. If automatic module loading '
            'struggles with your data types, try listing the modules here. '
            'The module and its __POA partner will be imported.')
    parser.add_option('-n', '--number', dest='max', action='store',
            type='int', default='1',
            help='Specify the number of times to write to the port. '
            '[Default: %default]')
    parser.add_option('-p', '--path', dest='paths', action='append',
            type='string', default=[],
            help='Extra module search paths to add to the PYTHONPATH.')
    parser.add_option('-r', '--rate', dest='rate', action='store',
            type='float', default=1.0,
            help='Specify the rate in Hertz at which to emit data. '
            '[Default: %default]')
    parser.add_option('-t', '--timeout', dest='timeout', action='store',
            type='float', default=-1, help='Write data for this many seconds, '
            'then stop. This option overrides --number. [Default: %default]')
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

    if len(args) < 1:
        print(usage, file=sys.stderr)
        return 1

    try:
        write_to_ports([path.cmd_path_to_full_path(p) \
                for p in args], options, tree=tree)
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), e),
                file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


