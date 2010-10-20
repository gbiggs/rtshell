#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of the command to print data sent by a port to the console.

'''


import imp
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
import threading
from traceback import print_exc

from rtshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtshell.path import cmd_path_to_full_path


def get_our_listener(options, index, tree=None, orb=None):
    if not tree:
        tree = create_rtctree(paths=['/', 'localhost'], orb=orb,
                filter=[['/', 'localhost']])
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


def get_our_listener_port(options, index, tree=None, orb=None):
    result, comp = get_our_listener(options, index, tree=tree, orb=orb)
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
        tree = create_rtctree(paths=path, orb=orb, filter=[path])
    if not tree:
        return 1, (None, None)

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1, (None, None)

    comp = tree.get_node(path)
    if not comp or not comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
component'.format(sys.argv[0], cmd_path)
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
        tree = create_rtctree(paths=path, filter=[path])
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


def import_user_mod(mod_name):
    f = None
    m = None
    try:
        f, p, d = imp.find_module(mod_name)
        m = imp.load_module(mod_name, f, p, d)
    except ImportError, e:
        print >>sys.stderr, '{0}: {1}: Error importing module: {2}'.format(\
                sys.argv[0], mod_name, e)
    finally:
        if f:
            f.close()
    return m


def import_user_mods(mod_names):
    mods = [import_user_mod(m) for m in mod_names.split(',')]
    if None in mods:
        return None
    return mods


def find_port_type(type_name, modules):
    for m in modules:
        types = [member for member in inspect.getmembers (m, inspect.isclass) \
                    if member[0] == type_name]
        if len(types) == 0:
            continue
        elif len(types) != 1:
            return None
        else:
            return types[0][1]
    return None


def import_formatter(mod_name):
    mod = import_user_mod(mod_name)
    if not mod:
        return None
    fs = [m for m in inspect.getmembers(mod, inspect.isfunction) \
            if m[0] == 'format']
    if len(fs) == 0:
        print >>sys.stderr, '{0}: {1}: No format function found.'.format(\
                sys.argv[0], mod_name)
        return None
    elif len(fs) != 1:
        print >>sys.stderr, \
                '{0}: {1}: Multiple format functions found.'.format(\
                        sys.argv[0], mod_name)
        return None
    else:
        f = fs[0][1]
        args, varargs, varkw, defaults = inspect.getargspec(f)
        if len(args) != 1 or varargs or varkw or defaults:
            print >>sys.stderr, \
                    '{0}: {1}: Format function has bad signature.'.format(\
                    sys.argv[0], mod_name)
            return None
        return f


class Listener(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, manager, port_type, event, one=False, formatter=None):
        OpenRTM_aist.DataFlowComponentBase.__init__ (self, manager)
        self._port_type = port_type
        self._event = event
        self._one = one
        self._formatter = formatter

    def onInitialize(self):
        try:
            args, varargs, varkw, defaults = \
                    inspect.getargspec(self._port_type.__init__)
            if defaults:
                init_args = tuple([None \
                        for ii in range(len(args) - len(defaults) - 1)])
            else:
                init_args = [None for ii in range(len(args) - 1)]
            self._inport_data = self._port_type(*init_args)
            self._inport = OpenRTM_aist.InPort('input', self._inport_data,
                    OpenRTM_aist.RingBuffer (8))
            self.registerInPort('input', self._inport)
        except:
            print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK


    def onExecute(self, ec_id):
        try:
            if self._inport.isNew():
                self._inport_data = self._inport.read()
                if self._formatter:
                    output = self._formatter(self._inport_data)
                else:
                    output = ''
                    if 'tm' in dir(self._inport_data):
                        output += '[{0}.{1:09}] '.format(\
                                self._inport_data.tm.sec,
                                self._inport_data.tm.nsec)
                    output += '{0}'.format(self._inport_data)
                print output
                if self._one:
                    self._event.set()
        except:
            print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK


def listener_name_base():
    return 'rtprint_listener'


def listener_name(index):
    return '{0}{1}'.format(listener_name_base(), index)


def listener_reg_name(index):
    return '{0}0.rtc'.format(listener_name(index))


def listener_fact(port_type, event, one, formatter):
    def fact_fun(mgr):
        return Listener(mgr, port_type, event, one, formatter)
    return fact_fun


def init_listener(port_type, event, index, one=False, formatter=None):
    def init_fun(mgr):
        spec= ['implementation_id', listener_name(index),
            'type_name', listener_name(index),
            'description', 'Listener component generated by rtprint',
            'version', '3.0',
            'vendor', 'rtshell',
            'category', 'DataConsumer',
            'activity_type', 'DataFlowComponent',
            'max_instance', '1',
            'language', 'Python',
            'lang_type', 'SCRIPT',
            '']
        profile = OpenRTM_aist.Properties(defaults_str=spec)
        mgr.registerFactory(profile,
                listener_fact(port_type, event, one, formatter),
                OpenRTM_aist.Delete)
        comp = mgr.createComponent(listener_name(index))
    return init_fun


def create_listener_comp(port_string, event, index, one=False, user_mods=[],
        formatter=None):
    global port_type
    port_type = find_port_type(port_string, user_mods + [RTC])
    if port_type == None:
        print >>sys.stderr, '{0}: Port has unknown or ambiguous type: \
{1}'.format(sys.argv[0], port_string)
        return 1, None

    mgr = OpenRTM_aist.Manager.init(1, [sys.argv[0]])
    mgr.setModuleInitProc(init_listener(port_type, event, index, one,
        formatter))
    mgr.activateManager()
    mgr.runManager(True)
    return 0, mgr


def connect_listener(cmd_path, path, port, options, index, orb):
    result, source_port = get_port_obj(cmd_path, path, port, options, orb=orb)
    if result:
        return result

    result, dest_port = get_our_listener_port(options, index, orb=orb)
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


def activate_listener(options, index, orb):
    result, comp = get_our_listener(options, index, orb=orb)
    if result:
        return result
    comp.activate_in_ec(0)


def interrupt_waiter(event):
    try:
        raw_input('')
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    event.set()


def listen_to_port(cmd_path, full_path, options, tree=None):
    event = threading.Event()

    path, port = parse_path(full_path)
    if not port:
        # Need a port to connect to
        print >>sys.stderr, '{0}: No port specified'.format(sys.argv[0])
        return 1
    if not path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Bad path'.format(sys.argv[0])
        return 1

    if options.formatter:
        formatter = import_formatter(options.formatter)
        if not formatter:
            return 1
    else:
        formatter = None

    user_mods = import_user_mods(options.type_mods)
    if not user_mods:
        return 1

    result, port_string = get_port_type_string(cmd_path, path, port, options,
            tree)
    if result:
        return result
    result, index = select_index(path, tree)
    if result:
        return result
    result, manager = create_listener_comp(port_string, event, index,
            one=options.one, user_mods=user_mods, formatter=formatter)
    if result:
        return result
    result = connect_listener(cmd_path, path, port, options, index,
            manager.getORB())
    if result:
        return result
    result = activate_listener(options, index, manager.getORB())
    if result:
        return result

    waiter = threading.Thread(target=interrupt_waiter, args=(event,))
    #waiter.start()
    try:
        if options.timeout != -1:
            event.wait(float(options.timeout))
        elif options.one:
            event.wait()
        else:
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
    parser.add_option('-1', '--one', dest='one', action='store_true',
            default=False, help='Exit after receiving one value. \
[Default: %default]')
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('-f', '--formatter', dest='formatter', action='store',
            type='string', default='',
            help='Specify a data printer module. This module must provide a \
function called "formatter" that will format the data. The function will be \
passed the data item and must return a string. The module will be imported, \
so it must be in the PYTHONPATH (such as in the current directory).')
    parser.add_option('-m', '--type-mod', dest='type_mods', action='store',
            type='string', default='',
            help='Specify the module containing the data type. This option \
must be supplied if the data type is not defined in the RTC modules supplied \
with OpenRTM-aist. This module and the __POA module will both be imported.')
    parser.add_option('-t', '--timeout', dest='timeout', action='store',
            type='float', default=-1, help='Print data for this many seconds, \
then stop. Specify -1 for no timeout. [Default: %default]')

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

