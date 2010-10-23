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

Base class for generated-on-demand components.

'''


import inspect
import OpenRTM_aist
import RTC
import sys
import traceback


###############################################################################
## Port class

class Port(object):
    '''Class to store the objects used for a port.'''
    def __init__(self, data, port, *args, **kwargs):
        super(Port, self).__init__()
        self._data = data
        self._port = port

    @property
    def data(self):
        '''Get the port's data reference.'''
        return self._data

    @property
    def port(self):
        '''Get the port object.'''
        return self._port


###############################################################################
## Generated-on-demand component class

class GenComp(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, mgr, port_specs, event=None, max=-1, *args, **kwargs):
        '''Constructor.

        @param mgr Reference to the manager that created this component.
        @param port_spec The port layout of the component. This must be
                         a list of port_types.PortSpec objects.
        @param event An event object that can be .set() to indicate
                     that the component has finished its assigned task
                     and should be shut down.
        @param max The maximum number of times this component should
                   perform its onExecute function before setting the
                   event to request a shutdown. Defaults to -1, for
                   unlimited.

        '''
        OpenRTM_aist.DataFlowComponentBase.__init__(self, mgr)
        self._port_specs = port_specs
        self._event = event
        self._max = max
        self._count = 0

    def onInitialize(self):
        try:
            self._ports = []
            for p in self._port_specs:
                args, varargs, varkw, defaults = \
                inspect.getargspec(p.type.__init__)
                if defaults:
                    init_args = tuple([None \
                            for ii in range(len(args) - len(defaults) - 1)])
                else:
                    init_args = [None for ii in range(len(args) - 1)]
                if p.input:
                    port_con = OpenRTM_aist.InPort
                    port_reg = self.registerInPort
                else:
                    port_con = OpenRTM_aist.OutPort
                    port_reg = self.registerOutPort
                p_data = p.type(*init_args)
                p_port = port_con(p.name, p_data)
                port_reg(p.name, p_port)
                self._ports.append(Port(p_data, p_port))
        except:
            print >>sys.stderr, traceback.format_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        # Call the component behaviour
        try:
            if self._count < self._max or self._max < 0:
                self._behv(ec_id)
                self._count += 1
                if self._count == self._max:
                    self._set()
        except:
            traceback.print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK

    def _behv(self, ec_id):
        pass

    def _set(self):
        '''Call set() on the event object to notify waiters.'''
        if self._event:
            self._event.set()


def make_factory(cons, port_specs, event=None, max=-1, **kwargs):
    def fact_fun(mgr):
        return cons(mgr, port_specs, event=event, max=max, **kwargs)
    return fact_fun


def make_init(name, cons, port_specs, event=None, rate=1.0, max=-1, **kwargs):
    def init_fun(mgr):
        spec= ['implementation_id', name,
            'type_name', name,
            'description', 'rtshell generated-on-demand component.',
            'version', '3.0',
            'vendor', 'rtshell',
            'category', 'Generated',
            'activity_type', 'DataFlowComponent',
            'max_instance', '1',
            'language', 'Python',
            'lang_type', 'SCRIPT',
            'exec_cxt.periodic.type', 'PeriodicExecutionContext',
            'exec_cxt.periodic.rate', '{0}'.format(rate),
            '']
        profile = OpenRTM_aist.Properties(defaults_str=spec)
        mgr.registerFactory(profile,
                make_factory(cons, port_specs, event=event, max=max, **kwargs),
                OpenRTM_aist.Delete)
        comp = mgr.createComponent(name)
    return init_fun

