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

Base class for generated-on-demand components.

'''

from __future__ import print_function

import inspect
import OpenRTM_aist
import RTC
import sys
import traceback


###############################################################################
## Port class

class Port(object):
    '''Class to store the objects used for a port.'''
    def __init__(self, data, port, formatter=None, raw_spec=None, *args,
            **kwargs):
        super(Port, self).__init__()
        self._data = data
        self._port = port
        self._formatter = formatter
        self._raw = raw_spec
        members = [m for m in dir(self.data) if not m.startswith('_')]
        if len(members) == 2 and 'tm' in members and \
                'data' in members and self.data.tm.__class__ == RTC.Time:
            self._standard_type = True
        else:
            self._standard_type = False

    @property
    def data(self):
        '''Get the port's data reference.'''
        return self._data

    @property
    def port(self):
        '''Get the port object.'''
        return self._port

    @property
    def formatter(self):
        '''Get the formatter function for the port, if any.'''
        return self._formatter

    @property
    def name(self):
        '''Get the port's name.'''
        return self._port.getName()

    @property
    def raw(self):
        '''Get the raw port spec for this port, if any.'''
        return self._raw

    @property
    def standard_type(self):
        '''Check if the port's data type is an RTC standard type.

        RTC standard types have a tm member (the timestamp) and a data member
        (the data).

        '''
        return self._standard_type

    def read(self):
        '''Read the next value from the port into self.data.'''
        self._data = self._port.read()

    def format(self):
        '''Return a string representation of the value of self.data.

        If self.formatter is not None, that function will be called to create
        the string representation. Otherwise, str() will be used except in the
        cases of data that contains a .tm member of type RTC.Time and a .data
        member. In that case, the time will be pretty-printed, followed by the
        data member, printed using str().

        '''
        if self.formatter:
            return self.formatter(self.data)
        else:
            members = [m for m in dir(self.data) if not m.startswith('_')]
            if len(members) == 2 and 'tm' in members and \
                    'data' in members and self.data.tm.__class__ == RTC.Time:
                return '[{0}.{1:09}] {2}'.format(self.data.tm.sec,
                        self.data.tm.nsec, self.data.data)
            else:
                return str(self.data)


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
            self._ports = {}
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
                self._ports[p.name] = Port(p_data, p_port,
                        formatter=p.formatter, raw_spec=p)
        except:
            print(traceback.format_exc(), file=sys.stderr)
            return RTC.RTC_ERROR
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        # Call the component behaviour
        res = RTC.RTC_OK
        if self._count < self._max or self._max < 0:
            res, executed = self._behv(ec_id)
            if executed > 0:
                self._count += executed
                if self._max > -1 and self._count >= self._max:
                    self._set()
        return res

    def _behv(self, ec_id):
        '''Behaviour function for derived components.

        Deriving classes must implement this function. It will be called by
        onExecute. It must return a tuple of (RTC result code, _behv result
        value). The RTC result code is used to create the result of onExecute;
        if no errors occur, it must be RTC.RTC_OK. The _behv result code is
        used to tell the component if the behaviour was able to execute
        (whether it succeeded or not), for the purposes of execution counting.
        It should be the number of iterations executed.

        '''
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
            '']
        profile = OpenRTM_aist.Properties(defaults_str=spec)
        mgr.registerFactory(profile,
                make_factory(cons, port_specs, event=event, max=max, **kwargs),
                OpenRTM_aist.Delete)
        comp = mgr.createComponent(name +
            '?exec_cxt.periodic.type=PeriodicExecutionContext&'
            'exec_cxt.periodic.rate={0}'.format(rate))
    return init_fun

