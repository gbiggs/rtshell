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

rtresurrect library.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.path
import rtctree.tree
import rtsprofile.rts_profile
import sys
import traceback

from rtshell import actions
from rtshell import option_store
import rtshell


def check_required_component_actions(rtsprofile):
    checks = []
    # First perform a sanity check of the system.
    # All required components must be present
    for comp in [c for c in rtsprofile.components if c.is_required]:
        checks.append(actions.CheckForRequiredCompAct('/' + comp.path_uri,
            comp.id, comp.instance_name,
            callbacks=[actions.RequiredActionCB()]))
    return checks


def get_data_conn_props(conn):
    return {'dataport.dataflow_type': str(conn.data_flow_type),
            'dataport.interface_type': str(conn.interface_type),
            'dataport.subscription_type': str(conn.subscription_type),
            'dataport.data_type': str(conn.data_type)}


def clean_props(props):
    '''Clean properties of dangerous values and wrong data types.

    Make sure the properties don't have IORs or similar in them, because
    they will confuse the notify_connect calls.

    Make sure that all keys are not unicode.

    '''
    new_props = {}
    for p in props:
        if p == 'dataport.corba_cdr.inport_ior':
            continue
        if p == 'dataport.corba_cdr.inport_ref':
            continue
        if p == 'dataport.corba_cdr.outport_ior':
            continue
        if p == 'dataport.corba_cdr.outport_ref':
            continue
        new_props[str(p)] = str(props[p])
    return new_props


def data_connection_actions(rtsprofile):
    # The ports on those components in any required connections must also be
    # present.
    checks = []
    make_connections = []
    for conn in rtsprofile.required_data_connections():
        source_comp = rtsprofile.find_comp_by_target(conn.source_data_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_data_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_data_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port = conn.target_data_port.port_name
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        checks.append(actions.CheckForPortAct(source_path, source_port,
            callbacks=[actions.RequiredActionCB()]))
        checks.append(actions.CheckForPortAct(dest_path, dest_port,
            callbacks=[actions.RequiredActionCB()]))
        props = get_data_conn_props(conn)
        props.update(conn.properties)
        props = clean_props(props)
        make_connections.append(actions.ConnectPortsAct(source_path,
            source_port, dest_path, dest_port, str(conn.name),
            str(conn.connector_id), props,
            callbacks=[actions.RequiredActionCB()]))

    # Add the other connections to the list
    for conn in rtsprofile.optional_data_connections():
        source_comp = rtsprofile.find_comp_by_target(conn.source_data_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_data_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_data_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port = conn.target_data_port.port_name
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        props = get_data_conn_props(conn)
        props.update(conn.properties)
        props = clean_props(props)
        make_connections.append(actions.ConnectPortsAct(source_path,
            source_port, dest_path, dest_port, str(conn.name),
            str(conn.connector_id), props))

    return checks, make_connections


def service_connection_actions(rtsprofile):
    # The ports on those components in any required connections must also be
    # present.
    checks = []
    make_connections = []
    for conn in rtsprofile.required_service_connections():
        source_comp = rtsprofile.find_comp_by_target(conn.source_service_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_service_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_service_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port =conn.target_service_port.port_name 
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        checks.append(actions.CheckForPortAct(source_path, source_port,
            callbacks=[actions.RequiredActionCB()]))
        checks.append(actions.CheckForPortAct(dest_path, dest_port,
            callbacks=[actions.RequiredActionCB()]))
        make_connections.append(actions.ConnectPortsAct(source_path,
            source_port, dest_path, dest_port, str(conn.name),
            str(conn.connector_id), {},
            callbacks=[actions.RequiredActionCB()]))

    # Add the other connections to the list
    for conn in rtsprofile.optional_service_connections():
        source_comp = rtsprofile.find_comp_by_target(conn.source_service_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_service_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_service_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port =conn.target_service_port.port_name 
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        make_connections.append(actions.ConnectPortsAct(source_path,
            source_port, dest_path, dest_port, str(conn.name),
            str(conn.connector_id), {}))

    return checks, make_connections


def config_set_actions(rtsprofile):
    set_active = []
    # For each component, if there is an active set, add an action for it
    for comp in rtsprofile.components:
        if comp.active_configuration_set:
            set_active.append(actions.SetActiveConfigSetAct(
                '/' + comp.path_uri, comp.active_configuration_set))

    set_values = []
    for comp in rtsprofile.components:
        for cs in comp.configuration_sets:
            for p in cs.configuration_data:
                set_values.append(actions.SetConfigParamValueAct(
                    '/' + comp.path_uri, cs.id, p.name, p.data))

    return set_values + set_active


def rebuild_system_actions(rtsprofile):
    checks = check_required_component_actions(rtsprofile)
    data_conn_checks, data_connections = data_connection_actions(rtsprofile)
    svc_conn_checks, svc_connections = service_connection_actions(rtsprofile)
    config_actions = config_set_actions(rtsprofile)

    return checks + data_conn_checks + svc_conn_checks + data_connections + \
            svc_connections + config_actions


def resurrect(profile=None, xml=True, dry_run=False, tree=None):
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

    # Build a list of actions to perform that will reconstruct the system
    actions = rebuild_system_actions(rtsp)
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


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <RTSProfile file>
Recreate an RT system using an RTSProfile.'''
    parser = optparse.OptionParser(usage=usage, version=rtshell.RTSH_VERSION)
    parser.add_option('--dry-run', dest='dry_run', action='store_true',
            default=False, help="Print what will be done but don't actually "
            "do anything.  [Default: %default]")
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
        print('OptionError:', e, file=sys.stderr)
        return 1
    option_store.OptionStore().verbose = options.verbose

    if not args:
        profile = None
    elif len(args) == 1:
        profile = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1

    try:
        resurrect(profile=profile, xml=options.xml, dry_run=options.dry_run,
                tree=tree)
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

