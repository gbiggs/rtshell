#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import imp
import OpenRTM_aist
import os
import os.path
import RTC
import sys
import traceback


import MyData, MyData__POA


class C2(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, mgr):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, mgr)
        self._df = './test/c2_rcvd'

    def onInitialize(self):
        try:
            if os.path.exists(self._df):
                os.remove(self._df)

            f, p, d = imp.find_module('MyData')
            self._m = imp.load_module('MyData', f, p, d)
            if f:
                f.close()
            f, p, d = imp.find_module('MyData__POA')
            self._m_poa = imp.load_module('MyData__POA', f, p, d)
            if f:
                f.close()
            self._data_type = self._m.Bleg
            self._in_data = self._data_type(0, 0)
            self._inport = OpenRTM_aist.InPort('input', self._in_data,
                    OpenRTM_aist.RingBuffer(8))
            self.registerInPort('input', self._inport)
        except:
            traceback.print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        try:
            if self._inport.isNew():
                d = self._inport.read()
                with open(self._df, 'a+') as f:
                    f.write('{0}\n'.format(d))
                print(d)
        except:
            traceback.print_exc()
            return RTC.RTC_ERROR
        return RTC.RTC_OK


def comp_fact(opts, port, mods):
    def fact_fun(mgr):
        const = eval_const(opts.const, mods)
        if not const:
            return None
        return C2(mgr, const, port, opts.verbosity)
    return fact_fun


def init(mgr):
    spec = ['implementation_id',    'C2',
        'type_name',                'C2',
        'description',              'Custom data input component',
        'version',                  '1.0',
        'vendor',                   'Geoffrey Biggs, AIST',
        'category',                 'DataProducer',
        'activity_type',            'DataFlowComponent',
        'max_instance',             '999',
        'language',                 'Python',
        'lang_type',                'SCRIPT',
        '']
    profile = OpenRTM_aist.Properties(defaults_str=spec)
    mgr.registerFactory(profile, C2,
            OpenRTM_aist.Delete)

    
def initcreate(mgr):
    init(mgr)
    comp = mgr.createComponent("C2")


def main():
    mgr = OpenRTM_aist.Manager.init(len(sys.argv), sys.argv)
    mgr.setModuleInitProc(initcreate)
    mgr.activateManager()
    mgr.runManager()
    return 0


if __name__ == "__main__":
    sys.exit(main())

