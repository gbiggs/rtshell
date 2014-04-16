#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Reader component used by rtprint

'''


import gen_comp
import OpenRTM_aist
import RTC


###############################################################################
## Reader component for rtprint

class Reader(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, *args, **kwargs):
        gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)

    def _behv(self, ec_id):
        execed = 0
        for p in self._ports.values():
            if p.port.isNew():
                execed = 1
                p.read()
                print p.format()
        return RTC.RTC_OK, execed

