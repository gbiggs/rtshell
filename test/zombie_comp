#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# -*- Python -*-


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

Simple output component for tests.

'''


import OpenRTM_aist
import RTC
import sys


class ZombieComp(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

    def onInitialize(self):
        self._data = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._outport = OpenRTM_aist.OutPort('out', self._data)
        self.addOutPort('out', self._outport)
        self._count = 0
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        if self._inport.isNew():
            print(self._inport.read().data)
        return RTC.RTC_OK


comp_spec = ['implementation_id', 'Zombie',
        'type_name', 'Zombie',
        'description', 'Standard component',
        'version', '1.0',
        'vendor', 'Geoffrey Biggs',
        'category', 'Test',
        'activity_type', 'DataFlowComponent',
        'max_instance', '2',
        'language', 'Python',
        'lang_type', 'script',
        '']


def CompInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=comp_spec)
    manager.registerFactory(profile, ZombieComp, OpenRTM_aist.Delete)


def ModuleInit(manager):
    CompInit(manager)
    manager.createComponent('Zombie')


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(ModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == '__main__':
    main()

