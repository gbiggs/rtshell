#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: rtinject

Implementation of the command to inject a single shot of data into an input
port of a component.

'''

__version__ = '$Revision: $'
# $Source$


from omniORB import any, cdrMarshal, CORBA
from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
from OpenRTM import PORT_OK
from OpenRTM__POA import InPortCdr
import RTC
import SDOPackage
import sys
import time

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def inject_data(cmd_path, full_path, options, data, tree):
    path, port = parse_path(full_path)
    if not port:
        # Need a port to inject to
        print >>sys.stderr, '{0}: Cannot access {1}: Not a port'.format(\
                sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        print >>sys.stderr, '{0}: {1}: Not a port'.format(\
                sys.argv[0], cmd_path)
        return 1

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return tree

    comp = tree.get_node(path)
    if not comp or not comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
component.'.format(sys.argv[0], cmd_path)
        return 1
    port = comp.get_port_by_name(port)
    if not port:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], cmd_path)
        return 1
    if not port.porttype == 'DataInPort':
        print >>sys.stderr, '{0}: Can only inject to DataInPort port \
type.'.format(sys.argv[0])
        return 1

    # Create a dummy connector on the port
    datatype = str(data.__class__).rpartition('.')[2]
    props = []
    props.append(SDOPackage.NameValue('dataport.dataflow_type',
                                      any.to_any('push')))
    props.append(SDOPackage.NameValue('dataport.interface_type',
                                      any.to_any('corba_cdr')))
    props.append(SDOPackage.NameValue('dataport.subscription_type',
                                      any.to_any('flush')))
    props.append(SDOPackage.NameValue('dataport.data_type',
                                      any.to_any(datatype)))
    profile = RTC.ConnectorProfile(path[-1] + '.inject_conn',
                                   path[-1] + '.temp', [port.object], props)
    return_code, profile = port.object.connect(profile)
    port.reparse_connections()
    if return_code != RTC.RTC_OK:
        print >>sys.stderr, '{0}: Failed to create local connection.'.format(\
                sys.argv[0])
        return 1
    # Get the connection's IOR and narrow it to an InPortCdr object
    conn = port.get_connection_by_name(path[-1] + '.inject_conn')
    ior = conn.properties['dataport.corba_cdr.inport_ior']
    object = comp.orb.string_to_object(ior)
    if CORBA.is_nil(object):
        print >>sys.stderr, '{0}: Failed to get inport object.'.format(\
                sys.argv[0])
        return 1
    object = object._narrow(InPortCdr)
    # Inject the data
    cdr = cdrMarshal(any.to_any(data).typecode(), data, True)
    if object.put(cdr) != PORT_OK:
        print >>sys.stderr, '{0}: Failed to inject data.'.format(sys.argv[0])
        return 1
    # Remove the dummy connection
    conn.disconnect()

    return 0


def replace_time(string):
    '''Replaces any occurances with %time% with the system time.'''
    now = time.time()
    sys_time = RTC.Time(int(now), int((now - int(now)) * 1e9))
    return string.format(time=sys_time)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path> <data>

Inject a single shot of data into an input port of a component.

The data must be a valid Python expression, such as "RTC.TimedLong({time}, 42)"
or "RTC.TimedLongSeq(RTC.Time(0, 0), [1, 2, 3])". If the expression contains
the phrase "{time}", it will be replaced with an RTC.Time object containing the
system time.

Warning: This command is insecure. The Python expression is evaluated without
any checks. You should not give access to this command to untrusted people.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')

    if argv:
        sys.argv = argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if len(args) != 2:
        print >>sys.stderr, 'Insufficient arguments.'
        return 1

    cmd_path = args[0]
    full_path = cmd_path_to_full_path(cmd_path)
    data = eval(replace_time(args[1]))

    return inject_data(cmd_path, full_path, options, data, tree)


# vim: tw=79

