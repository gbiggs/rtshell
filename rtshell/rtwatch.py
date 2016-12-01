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

import optparse
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

from rtshell import path
from rtshell import rts_exceptions
import rtshell

counter = 0

def rtc_status_cb(event, args, args2):
    global counter
    sevent = args[1]
    if sevent == rtctree.component.Component.INACTIVE:
        sevent = 'INACTIVE'
    elif sevent == rtctree.component.Component.ACTIVE:
        sevent = 'ACTIVE'
    elif sevent == rtctree.component.Component.ERROR:
        sevent = 'ERROR'
    elif sevent == rtctree.component.Component.UNKNOWN:
        sevent = 'UNKNOWN'
    elif sevent == rtctree.component.Component.CREATED:
        sevent = 'CREATED'
    print('[{0}] {1} {2}'.format(time.time(), args[0], sevent))
    counter += 1

def component_profile_cb(event, args, args2):
    global counter
    print('[{0}] {1}'.format(time.time(), ','.join(args[0])))
    counter += 1

def ec_event_cb(event, args, args2):
    global counter
    eevent = args[1]
    if eevent == rtctree.component.Component.EC_ATTACHED:
        eevent = 'EC_ATTACHED'
    elif eevent == rtctree.component.Component.EC_DETACHED:
        eevent = 'EC_DETACHED'
    elif eevent == rtctree.component.Component.EC_RATE_CHANGED:
        eevent = 'EC_RATE_CHANGED'
    elif eevent == rtctree.component.Component.EC_STARTUP:
        eevent = 'EC_STARTUP'
    elif eevent == rtctree.component.Component.EC_SHUTDOWN:
        eevent = 'EC_SHUTDOWN'
    print('[{0}] {1} {2}'.format(time.time(), args[0], eevent))
    counter += 1

def port_event_cb(event, args, args2):
    global counter
    pevent = args[1]
    if pevent == rtctree.component.Component.PORT_ADD:
        pevent = 'PORT_ADD'
    elif pevent == rtctree.component.Component.PORT_REMOVE:
        pevent = 'PORT_REMOVE'
    elif pevent == rtctree.component.Component.PORT_CONNECT:
        pevent = 'PORT_CONNECT'
    elif pevent == rtctree.component.Component.PORT_DISCONNECT:
        pevent = 'PORT_DISCONNECT'
    print('[{0}] {1} {2}'.format(time.time(), args[0], pevent))
    counter += 1

def config_event_cb(event, args, args2):
    global counter
    cevent = args[1]
    if cevent == rtctree.component.Component.CFG_UPDATE_SET:
        cevent = 'CFG_UPDATE_SET'
    elif cevent == rtctree.component.Component.CFG_UPDATE_PARAM:
        cevent = 'CFG_UPDATE_PARAM'
    elif cevent == rtctree.component.Component.CFG_SET_SET:
        cevent = 'CFG_SET_SET'
    elif cevent == rtctree.component.Component.CFG_ADD_SET:
        cevent = 'CFG_ADD_SET'
    elif cevent == rtctree.component.Component.CFG_REMOVE_SET:
        cevent = 'CFG_REMOVE_SET'
    elif cevent == rtctree.component.Component.CFG_ACTIVATE_SET:
        cevent = 'CFG_ACTIVATE_SET'
    print('[{0}] {1} {2}'.format(time.time(), args[0], cevent))
    counter += 1

def heartbeat_cb(event, args, args2):
    global counter
    print('[{0}] {1}'.format(args[1], args[0]))
    counter += 1

def fsm_event_cb(event, args, args2):
    global counter
    print('[{0}] {1} {2}'.format(time.time(), args[0], args[1]))
    counter += 1

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
                rtc.add_callback(v[0], v[1])
        else:
            for f in options.filters:
                try:
                    v = filtermap[f]
                    rtc.add_callback(v[0], v[1])
                except KeyError:
                    print('Unknown filter: {0}'.format(f))
        rtcs.append(rtc)

    # Wait for a keyboard interrupt
    counter = 0
    atexit.register(clean_events, rtcs)
    while True:
        if options.number > 0 and counter >= options.number:
            break
        time.sleep(0.5)
    clean_events(rtcs)

def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path 1> [path 2...]
Watch a component event.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-n', '--number', dest='number', action='store',
            type='int', default=-1,
            help='Number of event to capture. [Default: %default]')
    parser.add_option('-f', '--filter', dest='filters', action='append',
            type='string', default=[],
            help='Event source filters. [Default: ALL]')
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

    if not args:
        # If no paths given then can't do anything.
        print('{0}: No component specified.'.format(
                os.path.basename(sys.argv[0])), file=sys.stderr)
        return 1
    paths = [[p, path.cmd_path_to_full_path(p)] for p in args]

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

