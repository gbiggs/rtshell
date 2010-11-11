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


import eval_const
import gen_comp

import OpenRTM_aist
import RTC
import select
import sys
import termios
import traceback


###############################################################################
## Writer component for rtinject

class Writer(gen_comp.GenComp):
    def __init__(self, mgr, port_specs, val=None, *args, **kwargs):
        gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)
        self._val = val

    def _behv(self, ec_id):
        for p in self._ports:
            p.port.write(self._val)
        return RTC.RTC_OK, True


###############################################################################
## From-standard-input writer component for rtinject

class StdinWriter(Writer):
    def __init__(self, mgr, port_specs, mods=[], *args, **kwargs):
        Writer.__init__(self, mgr, port_specs, *args, **kwargs)
        self._mods = mods
        self._input = ''
        self._val_buffer = []

    def _behv(self, ec_id):
        try:
            self._read_stdin()
            if self._val_buffer:
                self._val = self._val_buffer.pop(0)
                result = Writer._behv(self, ec_id)
                return result
            else:
                return RTC.RTC_OK, False
        except:
            traceback.print_exc()

    def _read_stdin(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            self._input += sys.stdin.read()
            lines = self._input.split('\n')
            if len(lines) > 1:
                self._process_lines(lines[:-1])
                self._input = lines[-1]

    def _process_lines(self, lines):
        for l in lines:
            self._val_buffer.append(eval_const.eval_const(l, self._mods))

