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

rtcheck library.

'''

from __future__ import print_function


import optparse
import os
import rtctree.path
import rtctree.tree
import rtsprofile.rts_profile
import sys
import traceback

from rtshell import actions
from rtshell import option_store
from rtshell import rts_exceptions
import rtshell


class SystemNotOKCB(rtshell.actions.BaseCallback):
    '''Callback for a required action.

    Checks the action result and raises @ref RequiredActionFailedError if the
    action failed.

    '''
    def __init__(self, *args, **kwargs):
        super(SystemNotOKCB, self).__init__(*args, **kwargs)
        self._failed = False

    def __call__(self, result, err_msg):
        if err_msg:
            print(err_msg, file=sys.stderr)
        if not result:
            self._failed = True

    def __str__(self):
        return 'Required'

    @property
    def failed(self):
        '''Did any calls to this callback indicate failure?'''
        return self._failed


def get_data_conn_props(conn):
    return {'dataport.dataflow_type': str(conn.data_flow_type),
            'dataport.interface_type': str(conn.interface_type),
            'dataport.subscription_type': str(conn.subscription_type),
            'dataport.data_type': str(conn.data_type)}


def check_comps(rtsprofile, req_cb):
    checks = []
    for comp in [c for c in rtsprofile.components if c.is_required]:
        checks.append(rtshell.actions.CheckForRequiredCompAct('/' +
            comp.path_uri, comp.id, comp.instance_name, callbacks=[req_cb]))
    for comp in [c for c in rtsprofile.components if not c.is_required]:
        checks.append(rtshell.actions.CheckForRequiredCompAct('/' +
            comp.path_uri, comp.id, comp.instance_name))
    return checks


def check_connection(c, rtsprofile, props, cbs):
    s_comp = rtsprofile.find_comp_by_target(c.source_data_port)
    s_path = '/' + s_comp.path_uri
    s_port = c.source_data_port.port_name
    prefix = s_comp.instance_name + '.'
    if s_port.startswith(prefix):
        s_port = s_port[len(prefix):]
    d_comp = rtsprofile.find_comp_by_target(c.target_data_port)
    d_path = '/' + d_comp.path_uri
    d_port = c.target_data_port.port_name
    prefix = d_comp.instance_name + '.'
    if d_port.startswith(prefix):
        d_port = d_port[len(prefix):]
    return rtshell.actions.CheckForConnAct((s_path, s_port), (d_path, d_port),
            str(c.connector_id), props, callbacks=cbs)


def check_connections(rtsprofile, req_cb):
    checks = []
    for c in rtsprofile.required_data_connections():
        props = get_data_conn_props(c)
        checks.append(check_connection(c, rtsprofile, props, [req_cb]))

    for c in rtsprofile.optional_data_connections():
        props = get_data_conn_props(c)
        checks.append(check_connection(c, rtsprofile, props, []))

    for c in rtsprofile.required_service_connections():
        checks.append(check_connection(c, rtsprofile, {} [req_cb]))

    for c in rtsprofile.optional_service_connections():
        checks.append(check_connection(c, rtsprofile, {}, []))

    return checks


def check_configs(rtsprofile, req_cb):
    checks = []
    # Check the correct set is active
    for c in rtsprofile.components:
        if c.active_configuration_set:
            checks.append(rtshell.actions.CheckActiveConfigSetAct('/' +
                c.path_uri, c.active_configuration_set, callbacks=[req_cb]))
        for cs in c.configuration_sets:
            for p in cs.configuration_data:
                checks.append(rtshell.actions.CheckConfigParamAct('/' +
                    c.path_uri, cs.id, p.name, p.data, callbacks=[req_cb]))
    return checks


def check_states(rtsprofile, expected, req_cb):
    checks = []
    for comp in [c for c in rtsprofile.components if c.is_required]:
        for ec in comp.execution_contexts:
            checks.append(rtshell.actions.CheckCompStateAct('/' +
                comp.path_uri, comp.id, comp.instance_name, ec.id, expected,
                callbacks=[req_cb]))
    for comp in [c for c in rtsprofile.components if not c.is_required]:
        for ec in comp.execution_contexts:
            checks.append(rtshell.actions.CheckCompStateAct('/' +
                comp.path_uri, comp.id, comp.instance_name, ec.id, expected))
    return checks


def check(profile=None, xml=True, state='Active', dry_run=False, tree=None):
    # Load the profile
    if profile:
        # Read from a file
        with open(profile) as f:
            if xml:
                rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=f)
            else:
                rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=f)
    else:
        # Read from standard input
        lines = sys.stdin.read()
        if xml:
            rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=lines)
        else:
            rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=lines)

    # Build a list of actions to perform that will check the system
    cb = SystemNotOKCB()
    actions = (check_comps(rtsp, cb) + check_connections(rtsp, cb) +
            check_configs(rtsp, cb) + check_states(rtsp, state, cb))
    if dry_run:
        for a in actions:
            print(a)
    else:
        if not tree:
            # Load the RTC Tree, using the paths from the profile
            tree = rtctree.tree.RTCTree(paths=[rtctree.path.parse_path(
                '/' + c.path_uri)[0] for c in rtsp.components])
        for a in actions:
            a(tree)
    if cb.failed:
        return False
    return True


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <RTSProfile specification file>
Check that the running RT System conforms to an RTSProfile.'''
    parser = optparse.OptionParser(usage=usage, version=rtshell.RTSH_VERSION)
    parser.add_option('--dry-run', dest='dry_run', action='store_true',
            default=False, help="Print what will be done but don't actually '\
            'do anything. [Default: %default]")
    parser.add_option('-s', '--state', dest='state', action='store',
            type='string', default='Active',
            help='The expected state of the RT Components in the system. ' \
            '[Default: %default]')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-x', '--xml', dest='xml', action='store_true',
            default=True, help='Use XML input format. [Default: True]')
    parser.add_option('-y', '--yaml', dest='xml', action='store_false',
            help='Use YAML input format. [Default: False]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError: ', e, file=sys.stderr)
        return 1
    rtshell.option_store.OptionStore().verbose = options.verbose

    if not args:
        profile = None
    elif len(args) == 1:
        profile = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1

    try:
        if not check(profile=profile, xml=options.xml, state=options.state,
                dry_run=options.dry_run, tree=tree):
            return 1
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

