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

Reader component used by rtprint

'''


from rtshell import gen_comp

import OpenRTM_aist
import RTC


###############################################################################
## Reader component for rtprint

class Reader(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, *args, **kwargs):
        gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)

    def _behv(self, ec_id):
        execed = 0
        for p in list(self._ports.values()):
            if p.port.isNew():
                execed = 1
                p.read()
                print(p.format())
        return RTC.RTC_OK, execed


if __name__ == '__main__':
    main()



