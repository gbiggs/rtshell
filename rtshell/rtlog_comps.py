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

Log recording and playing components used by rtlog

'''


import OpenRTM_aist
import RTC
import sys

import gen_comp
import ilog


###############################################################################
## Recorder component for rtlog

class LogWriter(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, filename='', lims_are_ind=False,
            end=-1, *args, **kwargs):
        if lims_are_ind:
            max = end
            self._end = -1
        else:
            max = -1
            self._end = end
        gen_comp.GenComp.__init__(self, mgr, port_specs, max=max, *args,
                **kwargs)
        self._fn = filename

    def on_activated(self, ec_id):
        # Add activated time to meta data
        # Add port spec to meta data (include names)
        # Make file name from activated time
        # Create log, record meta data

    def on_deactivated(self, ec_id):
        # Finalise and close log

    def _behv(self, ec_id):
        execed = False
        result = RTC.RTC_OK
        for p in self._ports:
            if p.port.isNew():
                execed = True
                p.read()
                if not self._log(p):
                    result = RTC.RTC_ERROR
        return result, execed

    def _log(self, port):
        if port.standard_type:
            ts = 
            data_time = port.data.tm
        else:
            pass
        self._l.write(data)

