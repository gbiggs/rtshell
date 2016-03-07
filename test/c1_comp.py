#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import imp
import inspect
import sys
from traceback import print_exc
from time import time
from optparse import OptionParser, OptionError

import OpenRTM_aist
import RTC


class C1(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, mgr):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, mgr)

    def onInitialize(self):
        try:
            f, p, d = imp.find_module('MyData')
            self._m = imp.load_module('MyData', f, p, d)
            if f:
                f.close()
            f, p, d = imp.find_module('MyData__POA')
            self._m_poa = imp.load_module('MyData__POA', f, p, d)
            if f:
                f.close()
            self._data_type = self._m.Bleg
            self._out_data = self._data_type(0, 0)
            self._outport = OpenRTM_aist.OutPort('output', self._out_data,
                    OpenRTM_aist.RingBuffer(8))
            self.registerOutPort('output', self._outport)
            self._count = 0
        except:
            print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        try:
            val = eval('self._m.Bleg(1, {0})'.format(self._count))
            self._outport.write(val)
            self._count += 1
        except:
            print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK


def comp_fact(opts, port, mods):
    def fact_fun(mgr):
        const = eval_const(opts.const, mods)
        if not const:
            return None
        return C1(mgr, const, port, opts.verbosity)
    return fact_fun


def init(mgr):
    spec = ['implementation_id',    'C1',
        'type_name',                'C1',
        'description',              'Custom data type output component.',
        'version',                  '1.0',
        'vendor',                   'Geoffrey Biggs, AIST',
        'category',                 'DataProducer',
        'activity_type',            'DataFlowComponent',
        'max_instance',             '999',
        'language',                 'Python',
        'lang_type',                'SCRIPT',
        '']
    profile = OpenRTM_aist.Properties(defaults_str=spec)
    mgr.registerFactory(profile, C1,
            OpenRTM_aist.Delete)

def initcreate(mgr):
    init(mgr)
    comp = mgr.createComponent("C1")


def main():
    mgr = OpenRTM_aist.Manager.init(len(sys.argv), sys.argv)
    mgr.setModuleInitProc(initcreate)
    mgr.activateManager()
    mgr.runManager()
    return 0


if __name__ == "__main__":
    sys.exit(main())

