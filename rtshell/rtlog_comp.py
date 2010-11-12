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

Log writing and reading components used by rtlog

'''


import gen_comp
import OpenRTM_aist
import RTC
import sys


###############################################################################
## Log writer component for rtlog

class LogWriter(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, log, text_mode=False,
            err_out=sys.stderr, *args, **kwargs):
        gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)
        self._lf = log

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

    def _log(self, data):
        self._lf.write(ts, data)

    def _log_text(self, port):
        '''Log the port's data in text format.'''
        self._lf.write(port.format())

    def _log_pickle(self, port):
        '''Log the port's data in pickled format.'''
        return self._pickle((port.data))

    def _pickle(self, item):
        '''Pickle an item.'''
        try:
            pickle.dump(item, self._lf, pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError, e:
            print >>self._err_out, 'Error pickling data: {0}'.format(e)
            return False
        return True

