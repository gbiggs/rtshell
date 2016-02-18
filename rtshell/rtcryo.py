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

rtcryo library.

'''

from __future__ import print_function


import datetime
import optparse
import os.path
import rtctree.tree
import rtctree.path
import rtsprofile
import rtsprofile.rts_profile
import rtsprofile.component
import rtsprofile.config_set
import rtsprofile.exec_context
import rtsprofile.port_connectors
import rtsprofile.ports
import rtsprofile.targets
import sys
import traceback

from rtshell import option_store
import rtshell


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


def make_comp_id(comp):
    return 'RTC:{0}:{1}:{2}:{3}'.format(comp.vendor, comp.category,
                                        comp.type_name, comp.version)


def find_all_used_components(tree):
    # Finds all component nodes in the tree
    def get_node(node, args):
        return node
    def is_in_dir(node):
        if node.parent.is_manager:
            return False
        return True
    return [c for c in tree.iterate(get_node,
                                       filter=['is_component', is_in_dir]) \
              if c.connected_ports]


def find_unique_connectors(tree, components):
    # Finds all unique connections between the components
    data_connectors = []
    seen_svc_connectors = []
    svc_connectors = []
    def in_svc_list(conn):
        for c in svc_connectors:
            if c.connector_id == conn.id:
                return True
        return False

    for comp in components:
        for op in comp.connected_outports:
            for conn in op.connections:
                name = comp.instance_name + '.' + op.name
                source_port = rtsprofile.targets.TargetPort(
                        component_id=make_comp_id(comp),
                        instance_name=comp.instance_name, port_name=name)
                source_port.properties['COMPONENT_PATH_ID'] = \
                        comp.full_path_str[1:]
                # Get the list of ports this connection goes to
                dest_ports = [name for name, p in conn.ports \
                                   if not comp.get_port_by_ref(p.object)]
                if len(dest_ports) == 0:
                    continue
                # Assume the first is the destination and find its component
                path = rtctree.path.parse_path(dest_ports[0])
                dest_comp = tree.get_node(path[0])
                # Now have all the info we need to make the target
                name = dest_comp.instance_name + '.' + path[1]
                dest_port = rtsprofile.targets.TargetPort(
                        component_id=make_comp_id(dest_comp),
                        instance_name=dest_comp.instance_name, port_name=name)
                dest_port.properties['COMPONENT_PATH_ID'] = \
                        dest_comp.full_path_str[1:]
                # Check if the data type is known (see issue 13)
                if 'dataport.data_type' in conn.properties:
                    data_type = conn.properties['dataport.data_type']
                else:
                    data_type = dest_port.port_name
                rts_conn = rtsprofile.port_connectors.DataPortConnector(
                        connector_id=conn.id, name=conn.name,
                        data_type=data_type,
                        interface_type=conn.properties['dataport.interface_type'],
                        data_flow_type=conn.properties['dataport.dataflow_type'],
                        subscription_type=conn.properties['dataport.subscription_type'],
                        source_data_port=source_port,
                        target_data_port=dest_port)
                rts_conn.properties = clean_props(conn.properties)
                data_connectors.append(rts_conn)

        for sp in comp.connected_svcports:
            for conn in sp.connections:
                if in_svc_list(conn):
                    continue;
                seen_svc_connectors.append(conn)
                name = comp.instance_name + '.' + sp.name
                source_port = rtsprofile.targets.TargetPort(
                        component_id=make_comp_id(comp),
                        instance_name=comp.instance_name, port_name=name)
                source_port.properties['COMPONENT_PATH_ID'] = \
                        comp.full_path_str[1:]
                # Get the list of ports this connection goes to
                dest_ports = [name for name, p in conn.ports \
                                   if not comp.get_port_by_ref(p.object)]
                if not dest_ports:
                    # Skip ports with no or unknown connections
                    # (Unknown connections cannot be preserved)
                    # See issue 13
                    continue
                # Assume the first is the destination and find its component
                path = rtctree.path.parse_path(dest_ports[0])
                dest_comp = tree.get_node(path[0])
                # Now have all the info we need to make the target
                name = dest_comp.instance_name + '.' + path[1]
                dest_port = rtsprofile.targets.TargetPort(
                        component_id=make_comp_id(dest_comp),
                        instance_name=dest_comp.instance_name, port_name=name)
                dest_port.properties['COMPONENT_PATH_ID'] = \
                        dest_comp.full_path_str[1:]
                rts_conn = rtsprofile.port_connectors.ServicePortConnector(
                        connector_id=conn.id, name=conn.name,
                        source_service_port=source_port,
                        target_service_port=dest_port)
                rts_conn.properties = clean_props(conn.properties)
                svc_connectors.append(rts_conn)
    return data_connectors, svc_connectors


def tree_comps_to_rts_comps(components):
    rts_comps = []
    for comp in components:
        active_conf_set = comp.active_conf_set_name if comp.active_conf_set \
                                                    else ''
        new_rtsc = rtsprofile.component.Component(id=make_comp_id(comp),
                path_uri=comp.full_path_str[1:],
                active_configuration_set=active_conf_set,
                instance_name=comp.instance_name,
                composite_type=rtsprofile.composite_type.NONE,
                is_required=True)
        for dp in comp.inports:
            new_rtsc.data_ports.append(rtsprofile.ports.DataPort(dp.name))
        for dp in comp.outports:
            new_rtsc.data_ports.append(rtsprofile.ports.DataPort(dp.name))
        for sp in comp.svcports:
            new_rtsc.service_ports.append(rtsprofile.ports.ServicePort(sp.name))
        for cs in comp.conf_sets:
            new_cs = rtsprofile.config_set.ConfigurationSet(id=cs)
            for param in comp.conf_sets[cs].data:
                new_cs.configuration_data.append(
                        rtsprofile.config_set.ConfigurationData(name=param,
                            data=comp.conf_sets[cs].data[param]))
            new_rtsc.configuration_sets.append(new_cs)
        for ec in comp.owned_ecs:
            new_rtsc.execution_contexts.append(
                    rtsprofile.exec_context.ExecutionContext(
                        id=str(ec.handle),
                        kind=ec.kind_as_string(add_colour=False).upper(),
                        rate=ec.rate))
        new_rtsc.properties['IOR'] = \
                comp.nameserver.orb.object_to_string(comp.object)
        rts_comps.append(new_rtsc)
    return rts_comps


def data_conns_to_rts_conns(connectors):
    result = []
    for conn in connectors:
        source_port = rtsprofile.targets.TargetPort()
        dest_port = rtsprofile.targets.TargetPort()
    return result


def freeze_dry(servers, dest='-', xml=True, abstract='', vendor='', sysname='',
        version='', tree=None):
    if not tree:
        tree = rtctree.tree.RTCTree(servers=servers)
    # Run through the tree finding component names and connections to
    # preserve.
    components = find_all_used_components(tree)
    # Create a list of objects for the profile
    rts_components = tree_comps_to_rts_comps(components)
    data_connectors, svc_connectors = find_unique_connectors(tree,
            components)
    # Create an empty RTSProfile and add the information to it
    rtsp = rtsprofile.rts_profile.RtsProfile()
    rtsp.abstract = abstract
    today = datetime.datetime.today()
    today = today.replace(microsecond=0)
    rtsp.creation_date = today.isoformat()
    rtsp.update_date = today.isoformat()
    rtsp.version = rtsprofile.RTSPROFILE_SPEC_VERSION
    rtsp.id = 'RTSystem:{0}:{1}:{2}'.format(vendor, sysname, version)
    rtsp.components = rts_components
    rtsp.data_port_connectors = data_connectors
    rtsp.service_port_connectors = svc_connectors

    if dest == '-':
        # Write XML to stdout
        if xml:
            sys.stdout.write(rtsp.save_to_xml())
        else:
            sys.stdout.write(rtsp.save_to_yaml())
    else:
        # Write to a file
        f = open(dest, 'w')
        if xml:
            f.write(rtsp.save_to_xml())
        else:
            f.write(rtsp.save_to_yaml())
        f.close()


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [name servers]
Record a running RT System in an RTSProfile specification.'''
    parser = optparse.OptionParser(usage=usage, version=rtshell.RTSH_VERSION)
    parser.add_option('-a', '--abstract', dest='abstract', action='store',
            type='string', default='RT System created by rtcryo.',
            help='Brief description of the RT System.')
    parser.add_option('-n', '--system-name', dest='sysname', action='store',
            type='string', default='RTSystem',
            help='Name of the RT System. [Default: %default]')
    parser.add_option('-o', '--output', dest='output', action='store',
            type='string', default='-',
            help='Output file name. [Default: standard out]')
    parser.add_option('-v', '--system-version', dest='version', action='store',
            type='string', default='0',
            help='Version of the RT System. [Default: %default]')
    parser.add_option('-e', '--vendor', dest='vendor', action='store',
            type='string', default='Me',
            help='Vendor of the RT System. [Default: %default]')
    parser.add_option('-x', '--xml', dest='xml', action='store_true',
            default=True, help='Use XML output format. [Default: True]')
    parser.add_option('-y', '--yaml', dest='xml', action='store_false',
            help='Use YAML output format. [Default: False]')
    parser.add_option('--verbose', dest='verbose', action='store_true',
            default=False, help='Verbose output. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError: ', e, file=sys.stderr)
        return 1
    option_store.OptionStore().verbose = options.verbose

    try:
        freeze_dry(args, dest=options.output, xml=options.xml,
                abstract=options.abstract, vendor=options.vendor,
                sysname=options.sysname, version=options.version, tree=tree)
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

