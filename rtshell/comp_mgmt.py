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

Functions for component management.

'''


import OpenRTM_aist
import re
import RTC
import rtctree.tree
import rtctree.utils
import sys

from rtshell import gen_comp
from rtshell import rts_exceptions


def find_comp_in_mgr(name, mgr):
    '''Find a component in a manager.

    @param name The type name of the component to search for.
    @param mgr The manager to which the component is registered.

    '''
    for c in mgr.getComponents():
        if c.getTypeName() == name:
            return c
    raise rts_exceptions.MissingCompError(name)


def get_comp(rtc, tree=None, orb=None):
    '''Get a rtctree.Component object from an rtctree.RTCTree.

    Get the component object by searching the RTCTree for the specified RTC.

    @param rtc Path to the component. This should be in
               the format used by rtctree, i.e. a list of path entries, with
               the first being a /. e.g. ['/', 'localhost', 'comp0.rtc'].
    @param tree An already-populated rtctree.RTCTree object, or None if one
                should be created.
    @param orb An ORB to use if the tree must be created, or None to make one.

    '''
    if not tree:
        tree = rtctree.tree.RTCTree(paths=rtc, orb=orb, filter=[rtc])

    if not tree.has_path(rtc):
        raise rts_exceptions.NoSuchObjectError(rtc)
    comp = tree.get_node(rtc)
    if not comp.is_component:
        raise rts_exceptions.NotAComponentError(rtc)
    return comp


def find_port(rtc, port, tree=None, orb=None):
    '''Get a rtctree.Port object from an rtctree.RTCTree.

    Get the port object by searching the RTCTree for the specified RTC, then
    looking for the specified port on that component.

    @param rtc Path to the component that should have a port. This should be in
               the format used by rtctree, i.e. a list of path entries, with
               the first being a /. e.g. ['/', 'localhost', 'comp0.rtc'].
    @param port Name of the port.
    @param tree An already-populated rtctree.RTCTree object, or None if one
                should be created.
    @param orb An ORB to use if the tree must be created, or None to make one.

    '''
    comp = get_comp(rtc, tree=tree, orb=orb)
    port_obj = comp.get_port_by_name(port)
    if not port_obj:
        raise rts_exceptions.PortNotFoundError(rtc, port)
    return port_obj


def choose_name(base, tree):
    '''Choose a name for the component from a given base.

    The name is chosen such that it does not conflict with other possible
    instances of the base name by appending an index number.

    @param base The base name to append the index to.
    @param tree A populated RTCTree to search for other instances of the
                same type of component.

    '''
    def get_result(node, args):
        return int(regex.match(node.name).group(1))
    def is_gen_comp(node):
        if regex.match(node.name):
            return True
        return False
    regex = re.compile('{0}(\d+)0.rtc'.format(base))
    matches = tree.iterate(get_result, filter=['is_component', is_gen_comp])
    if not matches:
        return base + '0'
    matches.sort()
    return base + '{0}'.format(matches[-1] + 1)


def make_comp(name_base, tree, cons, port_specs, event=None, rate=1.0,
        max=-1, **kwargs):
    name = choose_name(name_base, tree)
    mgr = OpenRTM_aist.Manager.init(1, [sys.argv[0]])
    mgr.setModuleInitProc(gen_comp.make_init(name, cons, port_specs,
        event=event, rate=rate, max=max, **kwargs))
    mgr.activateManager()
    mgr.runManager(True)
    return name, mgr


def delete_comp(mgr, comp):
    '''Delete the component from the manager.'''
    mgr.deleteComponent(comp=comp)


def shutdown(mgr):
    '''Shut down the manager.'''
    mgr.shutdown()
    mgr.join()


def connect(comp, port_specs, tree):
    def find_local_port(name, ports):
        for p in ports:
            if p.get_port_profile().name.split('.')[-1] == name:
                return p
        raise rts_exceptions.PortNotFoundError(comp.getTypeName(), name)

    props = {'dataport.dataflow_type':'push',
            'dataport.interface_type':'corba_cdr',
            'dataport.subscription_type':'flush'}
    ports = comp.get_ports()
    conns = []
    for p in port_specs:
        local_port = find_local_port(p.name, ports)
        for t in p.targets:
            dest_port = find_port(t[0], t[1], tree)
            props['dataport.data_type'] = \
                    dest_port.properties['dataport.data_type']
            prof = RTC.ConnectorProfile(p.name + '_' + t[1],
                    '', [local_port, dest_port.object],
                    rtctree.utils.dict_to_nvlist(props))
            res, connector = local_port.connect(prof)
            if res != RTC.RTC_OK:
                raise rts_exceptions.ConnectFailedError(t[0], t[1])
            conns.append(connector)
    return conns


def disconnect(comp):
    '''Disconnect all connections to @ref comp.

    @param comp An RTObject.

    '''
    ports = comp.get_ports()
    for p in ports:
        p.disconnect_all()


def activate(comp):
    for ec in comp.get_owned_contexts():
        if ec.activate_component(comp.getObjRef()) != RTC.RTC_OK:
            raise rts_exceptions.ActivateError(comp.getTypeName())
    for ec in comp.get_participating_contexts():
        if ec.activate_component(comp.getObjRef()) != RTC.RTC_OK:
            raise rts_exceptions.ActivateError(comp.getTypeName())


def deactivate(comp):
    for ec in comp.get_owned_contexts():
        if ec.deactivate_component(comp.getObjRef()) != RTC.RTC_OK:
            raise rts_exceptions.DeactivateError(comp.getTypeName())
    for ec in comp.get_participating_contexts():
        if ec.deactivate_component(comp.getObjRef()) != RTC.RTC_OK:
            raise rts_exceptions.DeactivateError(comp.getTypeName())

