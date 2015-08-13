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

Writer component used by rtinject

'''


from rtshell import gen_comp

import OpenRTM_aist
import RTC
import sys


###############################################################################
## Writer component for rtinject

class Writer(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, val=None, *args, **kwargs):
        gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)
        self._val = val

    def _behv(self, ec_id):
        for p in list(self._ports.values()):
            p.port.write(self._val)
        return RTC.RTC_OK, 1


###############################################################################
## From-standard-input writer component for rtinject

class StdinWriter(Writer):
    def __init__(self, mgr, port_specs, buf=None, mutex=None, *args,
            **kwargs):
        Writer.__init__(self, mgr, port_specs, *args, **kwargs)
        if buf is None:
            raise ValueError('buf cannot be None.')
        if mutex is None:
            raise ValueError('mutex cannot be None.')
        self._val_buffer = buf
        self._mutex = mutex

    def _behv(self, ec_id):
        with self._mutex:
            if self._val_buffer:
                self._val = self._val_buffer.pop(0)
                result = Writer._behv(self, ec_id)
                return result
            else:
                return RTC.RTC_OK, 0

