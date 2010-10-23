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

Writer component used by rtinject

'''


import gen_comp
import OpenRTM_aist
import RTC

import traceback


###############################################################################
## Writer component for rtinject

class Writer(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, val=None, *args, **kwargs):
        try:
            gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)
            self._val = val
        except:
            traceback.print_exc()

    def _behv(self, ec_id):
        try:
            for p in self._ports:
                p.port.write(self._val)
        except:
            traceback.print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK

