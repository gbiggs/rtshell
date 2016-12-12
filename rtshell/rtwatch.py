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

Implementation of the command to watch component events.

'''

from __future__ import print_function

import argparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import RTC
import sys
import traceback
import time
import atexit
from threading import Event

from rtshell import path
from rtshell import rts_exceptions
from rtctree.component import Component
import rtshell

STATUS_CODE_MAP = {
    Component.INACTIVE: 'INACTIVE',
    Component.ACTIVE: 'ACTIVE',
    Component.ERROR: 'ERROR',
    Component.UNKNOWN: 'UNKNOWN',
    Component.CREATED: 'CREATED'
}

EC_EVENT_CODE_MAP = {
    Component.EC_ATTACHED: 'EC_ATTACHED',
    Component.EC_DETACHED: 'EC_DETACHED',
    Component.EC_RATE_CHANGED: 'EC_RATE_CHANGED',
    Component.EC_STARTUP: 'EC_STARTUP',
    Component.EC_SHUTDOWN: 'EC_SHUTDOWN'
}

PORT_EVENT_CODE_MAP = {
    Component.PORT_ADD: 'PORT_ADD',
    Component.PORT_REMOVE: 'PORT_REMOVE',
    Component.PORT_CONNECT: 'PORT_CONNECT',
    Component.PORT_DISCONNECT: 'PORT_DISCONNECT'
}

CONFIG_EVENT_CODE_MAP = {
    Component.CFG_UPDATE_SET: 'CFG_UPDATE_SET',
    Component.CFG_UPDATE_PARAM: 'CFG_UPDATE_PARAM',
    Component.CFG_SET_SET: 'CFG_SET_SET',
    Component.CFG_ADD_SET: 'CFG_ADD_SET',
    Component.CFG_REMOVE_SET: 'CFG_REMOVE_SET',
    Component.CFG_ACTIVATE_SET: 'CFG_ACTIVATE_SET'
}

counter = 0

def rtc_status_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    try:
        sevent = STATUS_CODE_MAP[args[1]]
    except KeyError:
        sevent = 'UNKNOWN(CODE:{0})'.format(args[1])
    print('[{0}] {1} {2}'.format(time.time(), args[0], sevent))
    counter += 1
    event.set()

def component_profile_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    print('[{0}] {1}'.format(time.time(), ', '.join(args[0])))
    counter += 1
    event.set()

def ec_event_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    try:
        eevent = EC_EVENT_CODE_MAP[args[1]]
    except KeyError:
        eevent = 'UNKNOWN(CODE:{0})'.format(args[1])
    print('[{0}] {1} {2}'.format(time.time(), args[0], eevent))
    counter += 1
    event.set()

def port_event_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    try:
        pevent = PORT_EVENT_CODE_MAP[args[1]]
    except KeyError:
        pevent = 'UNKNOWN(CODE:{0})'.format(args[1])
    print('[{0}] {1} {2}'.format(time.time(), args[0], pevent))
    counter += 1
    event.set()

def config_event_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    try:
        cevent = CONFIG_EVENT_CODE_MAP[args[1]]
    except KeyError:
        cevent = 'UNKNOWN(CODE:{0})'.format(args[1])
    print('[{0}] {1} {2}'.format(time.time(), args[0], cevent))
    counter += 1
    event.set()

def heartbeat_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    print('[{0}] {1}'.format(args[1], args[0]))
    counter += 1
    event.set()

def fsm_event_cb(eventkind, args, args2):
    global counter
    event = args2[0]
    print('[{0}] {1} {2}'.format(time.time(), args[0], args[1]))
    counter += 1
    event.set()

filtermap = {
    'RTC_STATUS': ('rtc_status', rtc_status_cb),
    'COMPONENT_PROFILE': ('component_profile', component_profile_cb),
    'EC_EVENT': ('ec_event', ec_event_cb),
    'PORT_EVENT': ('port_event', port_event_cb),
    'CONFIG_EVENT': ('config_event', config_event_cb),
    'FSM_EVENT': ('fsm_event', fsm_event_cb),
    'HEARTBEAT': ('heartbeat', heartbeat_cb),
}

def clean_events(rtcs):
    # Remove all the event hooks that were added
    for i in rtcs:
        i.dynamic = False

def print_logs(paths, options, tree=None):
    global counter
    for p in paths:
        path, port = rtctree.path.parse_path(p[1])
        if port:
            raise rts_exceptions.NotAComponentError(p[0])
        if not path[-1]:
            raise rts_exceptions.NotAComponentError(p[0])
        p.append(path)

    if not tree:
        parsed = [p[2] for p in paths]
        tree = rtctree.tree.RTCTree(paths=parsed, filter=parsed)

    rtcs = []
    event = Event()
    for p in paths:
        if not tree.has_path(p[2]):
            raise rts_exceptions.NoSuchObjectError(p[0])
        rtc = tree.get_node(p[2])
        if rtc.is_zombie:
            raise rts_exceptions.ZombieObjectError(p[0])
        if not rtc.is_component:
            raise rts_exceptions.NotAComponentError(p[0])

        rtc.dynamic = True
        if len(options.filters) == 0 or 'ALL' in options.filters:
            for (k,v) in filtermap.items():
                rtc.add_callback(v[0], v[1], [event])
        else:
            for f in options.filters:
                try:
                    v = filtermap[f]
                    rtc.add_callback(v[0], v[1], [event])
                except KeyError:
                    print('Unknown filter: {0}'.format(f))
        rtcs.append(rtc)

    # Wait for a keyboard interrupt
    counter = 0
    atexit.register(clean_events, rtcs)
    while True:
        if options.number > 0 and counter >= options.number:
            break
        try:
            event.wait()
        except KeyboardInterrupt:
            break
        event.clear()
    clean_events(rtcs)

def main(argv=None, tree=None):
    parser = argparse.ArgumentParser(prog='rtwatch', description='Watch a component event.')
    filterkind = filtermap.keys()
    filterkind.insert(0, 'ALL')
    parser.add_argument('-n', '--number', dest='number', action='store',
            type=int, default=-1,
            help='Number of events to capture. [Default: %(default)s]')
    parser.add_argument('-f', '--filter', dest='filters', action='append',
            type=str, choices=filterkind, default=[],
            help='Event source filters. [Default: ALL]')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %(default)s]')
    parser.add_argument('path', metavar='path', type=str, nargs='+',
            help='Path to component.')

    if argv:
        sys.argv = [sys.argv[0]] + argv

    options = parser.parse_args()

    paths = [[p, path.cmd_path_to_full_path(p)] for p in options.path]

    try:
        print_logs(paths, options, tree)
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


# vim: tw=79

