#!/usr/bin/env python2
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2015
    Yosuke Matsusaka and Geoffrey Biggs
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

Implementation of the RT System visualisation command.

'''

from __future__ import print_function

import optparse
import os.path
import rtsprofile.rts_profile
import sys
import traceback

import rtshell


def port_name(s):
    parts = s.split('.')
    if len(parts) == 1:
        return s
    else:
        return parts[-1]


def escape(s):
    return s.replace('.', '_dot_').replace('/', '_slash_').replace('(', '_lpar_').replace(')', '_rpar_')


def get_ports(rtsp):
    in_ports = []
    out_ports = []
    for p in rtsp.service_port_connectors+rtsp.data_port_connectors:
        out_ports.append((p.source_data_port.instance_name,
            port_name(p.source_data_port.port_name)))
        in_ports.append((p.target_data_port.instance_name,
            port_name(p.target_data_port.port_name)))
    return in_ports, out_ports


def make_comp_str(c, in_ports, out_ports):
    in_ports_str = ''
    out_ports_str = ''
    for dp in c.data_ports:
        if (c.instance_name, dp.name) in in_ports:
            in_ports_str += '<{0}>{0}|'.format(port_name(dp.name))
        if (c.instance_name, dp.name) in out_ports:
            out_ports_str += '<{0}>{0}|'.format(port_name(dp.name))
    for sp in c.service_ports:
        if (c.instance_name, sp.name) in in_ports:
            in_ports_str += '<{0}>{0}|'.format(port_name(sp.name))
        if (c.instance_name, sp.name) in out_ports:
            out_ports_str += '<{0}>{0}|'.format(port_name(sp.name))
    label_str = '{{{{{0}}}|{1}|{{{2}}}}}'.format(in_ports_str[:-1], c.instance_name,
            out_ports_str[:-1])
    return '  {0} [label="{1}"];'.format(escape(c.instance_name), label_str)


def make_conn_str(s_port, d_port):
    return '  {0}:{1} -> {2}:{3}'.format(
            escape(s_port.instance_name), port_name(s_port.port_name),
            escape(d_port.instance_name), port_name(d_port.port_name))


def visualise(profile=None, xml=True, tree=None):
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

    result = ['digraph rtsprofile {', '  rankdir=LR;', '  node [shape=Mrecord];']
    in_ports, out_ports = get_ports(rtsp)
    for comp in rtsp.components:
        result.append(make_comp_str(comp, in_ports, out_ports))
    for conn in rtsp.data_port_connectors:
        result.append(make_conn_str(conn.source_data_port,
            conn.target_data_port) + ';')
    for conn in rtsp.service_port_connectors:
        result.append(make_conn_str(conn.source_service_port,
            conn.target_service_port) + ' [arrowhead="odot"];')
    result.append('}')
    return result


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [RTSProfile file]
Visualise RT Systems using dot files.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
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

    if not args:
        profile = None
    elif len(args) == 1:
        profile = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1

    try:
        for l in visualise(profile=profile, xml=options.xml, tree=tree):
            print(l)
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

