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

File: rtprint.py

Implementation of the command to print data sent by a port to the console.

'''

# $Source$


import inspect
import OpenRTM_aist
from optparse import OptionParser, OptionError
import os
import re
import RTC
from rtctree.exceptions import RtcTreeError, FailedToConnectError, \
                               IncompatibleDataPortConnectionPropsError, \
                               WrongPortTypeError, \
                               MismatchedInterfacesError, \
                               MismatchedPolarityError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
import sys
from traceback import print_exception

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


index = 0
port_type = None


def get_our_listener(options, tree=None, orb=None):
    if not tree:
        tree = create_rtctree(paths=['/', 'localhost'], orb=orb)
    if not tree:
        return 1, None

    listener_name = listener_reg_name(index)
    def get_result(node, args):
        return node
    def is_our_listener(node):
        if node.name == listener_name:
            return True
    matches = tree.iterate(get_result, filter=['is_component', is_our_listener])
    if not matches or len(matches) != 1:
        print >>sys.stderr, '{0}: Could not find listener component.'.format(\
                sys.argv[0])
        return 1, None
    return 0, matches[0]


def get_our_listener_port(options, tree=None, orb=None):
    result, comp = get_our_listener(options, tree=tree, orb=orb)
    if result:
        return result, None

    port_obj = comp.get_port_by_name('input')
    if not port_obj:
        print >>sys.stderr, '{0}: Cannot access {0}:input: No such \
port'.format(sys.argv[0], listener_name)
        return 1, None
    return 0, port_obj


def get_comp_obj(cmd_path, path, options, tree=None, orb=None):
    if not tree:
        tree = create_rtctree(paths=path, orb=orb)
    if not tree:
        return 1, (None, None)

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1, (None, None)

    comp = tree.get_node(path)
    if not comp or not comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], cmd_path)
        return 1, None
    return 0, (tree, comp)


def get_port_obj(cmd_path, path, port, options, tree=None, orb=None):
    result, (tree, comp) = get_comp_obj(cmd_path, path, options,
                                        tree=tree, orb=orb)
    if result:
        return result, None
    port_obj = comp.get_port_by_name(port)
    if not port_obj:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], cmd_path)
        return 1, None
    return 0, port_obj


def get_port_type_string(cmd_path, path, port, options, tree=None):
    result, port_obj = get_port_obj(cmd_path, path, port, options, tree=tree)
    if result:
        return result, None
    if not port_obj.porttype == 'DataOutPort':
        print >>sys.stderr, '{0}: Cannot listen to {1}: Not an output \
port'.format(sys.argv[0], cmd_path)
        return 1, None
    return 0, port_obj.properties['dataport.data_type']


def select_index(path, tree=None):
    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return 1, 0

    listener_re = re.compile('{0}(\d+)0.rtc'.format(listener_name_base()))
    def get_result(node, args):
        return int(listener_re.match(node.name).group(1))
    def is_listener(node):
        if listener_re.match(node.name):
            return True
    matches = tree.iterate(get_result, filter=['is_component', is_listener])
    if not matches:
        # No existing listeners, so claim the first spot
        return 0, 0
    matches.sort ()
    return 0, matches[-1] + 1


def find_port_type(type_name):
    types = [member for member in inspect.getmembers (RTC, inspect.isclass) \
                if member[0] == type_name]
    if len(types) == 0:
        return None
    elif len(types) != 1:
        return None
    return types[0][1]


def listener_name_base():
    return 'rtprint_listener'


def listener_name(index):
    return '{0}{1}'.format(listener_name_base(), index)


def listener_reg_name(index):
    return '{0}0.rtc'.format(listener_name(index))


def listener_spec(index):
    return ['implementation_id', listener_name(index),
            'type_name', 'rtprint_listener{0}'.format(index),
            'description', 'Listener component generated by rtprint',
            'version', '1.0',
            'vendor', 'rtcshell',
            'category', 'DataConsumer',
            'activity_type', 'DataFlowComponent',
            'max_instance', '1',
            'language', 'Python',
            'lang_type', 'SCRIPT',
            '']


class Listener(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__ (self, manager)
        self._port_type = port_type

    def onStartup(self, ec_id):
        try:
            self.inport_data = self._port_type(RTC.Time(0, 0), None)
            self.inport = OpenRTM_aist.InPort('input', self.inport_data,
                    OpenRTM_aist.RingBuffer (8))
            self.registerInPort('input', self.inport)
        except:
            print_exception(*sys.exc_info ())
            return RTC.RTC_ERROR
        return RTC.RTC_OK


    def onExecute(self, ec_id):
        try:
            if self.inport.isNew():
                self.inport_data = self.inport.read()
                print '[{0}.{1:09}] {2}'.format(self.inport_data.tm.sec,
                        self.inport_data.tm.nsec, str(self.inport_data.data))
        except:
            print_exception(*sys.exc_info ())
        return RTC.RTC_OK


def ListenerInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=listener_spec(index))
    manager.registerFactory(profile, Listener, OpenRTM_aist.Delete)
    comp = manager.createComponent('{0}'.format(\
            listener_name(index)))


def create_listener_comp(port_string):
    global port_type
    port_type = find_port_type(port_string)
    if port_type == None:
        print >>sys.stderr, '{0}: Port has unknown or ambiguous type: \
{1}'.format(sys.argv[0], port_string)
        return 1, None

    mgr = OpenRTM_aist.Manager.init(1, [sys.argv[0]])
    mgr.setModuleInitProc(ListenerInit)
    mgr.activateManager()
    mgr.runManager(True)
    return 0, mgr


def connect_listener(cmd_path, path, port, options, orb):
    result, source_port = get_port_obj(cmd_path, path, port, options, orb=orb)
    if result:
        return result

    result, dest_port = get_our_listener_port(options, orb=orb)
    if result:
        return result

    try:
        source_port.connect(dest_port)
    except IncompatibleDataPortConnectionPropsError:
        print >>sys.stderr, '{0}: An incompatible data port property or \
property value was given.'.format(sys.argv[0])
        return 1
    except WrongPortTypeError:
        print >>sys.stderr, '{0}: Mismatched port types.'.format(sys.argv[0])
        return 1
    except MismatchedPolarityError:
        print >>sys.stderr, '{0}: Service port polarities do not \
match.'.format(sys.argv[0])
        return 1
    except MismatchedInterfacesError:
        print >>sys.stderr, '{0}: Service port interfaces do not \
match.'.format(sys.argv[0])
        return 1
    except FailedToConnectError:
        print >>sys.stderr, '{0}: Failed to connect.'.format(sys.argv[0])
        return 1
    return 0


def activate_listener(options, orb):
    result, comp = get_our_listener(options, orb=orb)
    if result:
        return result
    comp.activate_in_ec(0)


def listen_to_port(cmd_path, full_path, options, tree=None):
    global index
    path, port = parse_path(full_path)
    if not port:
        # Need a port to connect to
        print >>sys.stderr, '{0}: No port specified'.format(sys.argv[0])
        return 1
    if not path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Bad path'.format(sys.argv[0])
        return 1

    result, port_string = get_port_type_string(cmd_path, path, port, options, tree)
    if result:
        return result
    result, index = select_index(path, tree)
    if result:
        return result
    result, manager = create_listener_comp(port_string)
    if result:
        return result
    result = connect_listener(cmd_path, path, port, options, manager.getORB())
    if result:
        return result
    result = activate_listener(options, manager.getORB())
    if result:
        return result
    try:
        while True:
            raw_input('')
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    manager.shutdown()
    manager.join()

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>:<port>
Print the data being sent by an output port.

''' + RTSH_PATH_USAGE + '''
A connection will be made to the port using the default connection settings
compatible with the port.'''
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if len(args) != 1:
        print >>sys.stderr, usage
        return 1
    else:
        path = args[0]
    full_path = cmd_path_to_full_path(path)

    return listen_to_port(path, full_path, options, tree)


# vim: tw=79

