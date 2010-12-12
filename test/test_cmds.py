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

Tests for the commands.

'''


import os
import os.path
import subprocess
import sys
import time
import unittest


COMP_LIB_PATH='/usr/local/share/OpenRTM-aist/examples/rtcs'


class RTCLaunchFailedError(Exception):
    pass


def call_process(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = p.communicate()
    output = (output[0].strip(), output[1].strip())
    return_code = p.returncode
    return output[0], output[1], return_code


def start_process(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return p


def find_omninames():
    # If on Windows, ...
    # Else use ps
    procs, stderr, ret_code = call_process(['ps', '-e'])
    for p in procs.split('\n'):
        if 'omniNames' in p:
            return p.split()[0]
    return None


def launch_comp(name):
    p = start_process([os.path.join('./test', name), '-f', './test/rtc.conf'])
    p.poll()
    if p.returncode is not None:
        raise RTCLaunchFailedError
    return p


def stop_comp(p):
    p.terminate()
    p.wait()


def start_ns():
    # Check if omniNames is running
    pid = find_omninames()
    if pid:
        # Return none to indicate the name server is not under our control
        return None
    else:
        # Start omniNames and return the PID
        return start_process('rtm-naming')


def stop_ns(p):
    if p:
        call_process(['killall', 'omniNames'])


def wait_for_comp(comp, state='Inactive', tries=40, res=0.05):
    while tries > 0:
        stdout, stderr, ret = call_process(['rtls', '-l',
            os.path.join('/localhost/local.host_cxt', comp)])
        if stdout != '':
            if stdout.split()[0] == state:
                return
        tries -= 1
        time.sleep(res)
    raise RTCLaunchFailedError


def make_zombie(comp='zombie_comp'):
    c = launch_comp(comp)
    wait_for_comp('Zombie0.rtc')
    c.kill()
    c.wait()


def clean_zombies():
    call_process(['rtdel', '-z'])


def launch_manager(tries=40, res=0.05):
    p = start_process(['rtcd', '-d', '-f', './test/rtc.conf'])
    while tries > 0:
        stdout, stderr, ret = call_process(['rtls',
            '/localhost/local.host_cxt/manager.mgr'])
        if stdout == '' and stderr == '':
            return p
        tries -= 1
        time.sleep(res)
    raise RTCLaunchFailedError


def stop_manager(mgr):
    mgr.terminate()
    mgr.wait()


def test_notacomp(tester, cmd, obj):
    stdout, stderr, ret = call_process(['./{0}'.format(cmd),
        '/localhost/local.host_cxt/{0}'.format(obj)])
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Not a component: /localhost/local.host_cxt/{1}'.format(cmd, obj))
    tester.assertEqual(ret, 1)


def test_noobject(tester, cmd, obj):
    stdout, stderr, ret = call_process(['./{0}'.format(cmd),
        '/localhost/local.host_cxt/{0}'.format(obj)])
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: No such object: /localhost/local.host_cxt/{1}'.format(cmd, obj))
    tester.assertEqual(ret, 1)


def test_zombie(tester, cmd, obj):
    stdout, stderr, ret = call_process(['./{0}'.format(cmd),
        '/localhost/local.host_cxt/{0}'.format(obj)])
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Zombie object: /localhost/local.host_cxt/{1}'.format(cmd, obj))
    tester.assertEqual(ret, 1)


def test_portnotfound(tester, cmd, obj):
    stdout, stderr, ret = call_process(['./{0}'.format(cmd),
        '/localhost/local.host_cxt/{0}'.format(obj)])
    tester.assertEqual(stdout, '')
    tester.assertEqual(stderr,
        '{0}: Port not found: /localhost/local.host_cxt/{1}'.format(cmd, obj))
    tester.assertEqual(ret, 1)


#class rtactTests(unittest.TestCase):
class rtactTests():
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        wait_for_comp('Std0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtact',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Active')

    def test_context(self):
        test_notacomp(self, 'rtact', '')

    def test_manager(self):
        test_notacomp(self, 'rtact', 'manager.mgr')

    def test_port(self):
        test_notacomp(self, 'rtact', 'Std0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, 'rtact', 'Std0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_no_object(self):
        test_noobject(self, 'rtact', 'NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, 'rtact', 'Zombie0.rtc')


def rtact_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtactTests)


#class rtdeactTests(unittest.TestCase):
class rtdeactTests():
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        call_process(['rtact', '/localhost/local.host_cxt/Std0.rtc'])
        wait_for_comp('Std0.rtc', state='Active')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtdeact',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_context(self):
        test_notacomp(self, 'rtdeact', '')

    def test_manager(self):
        test_notacomp(self, 'rtdeact', 'manager.mgr')

    def test_port(self):
        test_notacomp(self, 'rtdeact', 'Std0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, 'rtdeact', 'Std0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assertEqual(stdout.split()[1], 'Active')

    def test_no_object(self):
        test_noobject(self, 'rtdeact', 'NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, 'rtdeact', 'Zombie0.rtc')


def rtdeact_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtdeactTests)


#class rtresetTests(unittest.TestCase):
class rtresetTests():
    def setUp(self):
        self._ns = start_ns()
        self._err = launch_comp('err_comp')
        make_zombie()
        self._mgr = launch_manager()
        call_process(['rtact', '/localhost/local.host_cxt/Err0.rtc'])
        wait_for_comp('Err0.rtc', state='Error')

    def tearDown(self):
        stop_comp(self._err)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtreset',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout.split()[1], 'Inactive')

    def test_context(self):
        test_notacomp(self, 'rtreset', '')

    def test_manager(self):
        test_notacomp(self, 'rtreset', 'manager.mgr')

    def test_port(self):
        test_notacomp(self, 'rtreset', 'Err0.rtc:in')

    def test_trailing_slash(self):
        test_notacomp(self, 'rtreset', 'Err0.rtc/')
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Err0.rtc'])
        self.assertEqual(stdout.split()[1], 'Error')

    def test_no_object(self):
        test_noobject(self, 'rtreset', 'NotAComp0.rtc')

    def test_zombie_object(self):
        test_zombie(self, 'rtreset', 'Zombie0.rtc')


def rtreset_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtresetTests)


#class rtcatTests(unittest.TestCase):
class rtcatTests():
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        make_zombie()
        self._mgr = launch_manager()
        wait_for_comp('Std0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        clean_zombies()
        stop_manager(self._mgr)
        stop_ns(self._ns)

    def test_context(self):
        test_noobject(self, 'rtcat', '')

    def test_no_object(self):
        test_noobject(self, 'rtcat', 'NotAComp0.rtc')

    def test_no_object_port(self):
        test_noobject(self, 'rtcat', 'NotAComp0.rtc:notaport')

    def test_rtc(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc'])
        self.assert_(stdout.startswith('Std0.rtc'))
        self.assert_('Inactive' in stdout)
        self.assert_('Category' in stdout)
        self.assert_('Execution Context' in stdout)
        self.assert_('DataInPort: in' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_manager(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/manager.mgr'])
        self.assert_(stdout.startswith('Name: manager'))
        self.assert_('Modules:' in stdout)
        self.assert_('Loaded modules:' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_port(self):
        stdout, stderr, ret = call_process(['./rtcat',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assertEqual(stdout, '+DataInPort: in')
        stdout, stderr, ret = call_process(['./rtcat', '-l',
            '/localhost/local.host_cxt/Std0.rtc:in'])
        self.assert_(stdout.startswith('-DataInPort: in'))
        self.assert_('dataport.data_type' in stdout)
        self.assert_('TimedLong' in stdout)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_port_not_rtc(self):
        test_notacomp(self, 'rtcat', 'manager.mgr:in')

    def test_port_trailing_slash(self):
        test_noobject(self, 'rtcat', 'Std0.rtc:in/')

    def test_bad_port(self):
        test_portnotfound(self, 'rtcat', 'Std0.rtc:out')

    def test_rtc_trailing_slash(self):
        test_noobject(self, 'rtcat', 'Std0.rtc/')

    def test_zombie_object(self):
        test_zombie(self, 'rtcat', 'Zombie0.rtc')


def rtcat_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcatTests)


#class rtcheckTests(unittest.TestCase):
class rtcheckTests():
    def setUp(self):
        self._ns = start_ns()
        self._std = launch_comp('std_comp')
        self._output = launch_comp('output_comp')
        wait_for_comp('Std0.rtc')
        wait_for_comp('Output0.rtc')

    def tearDown(self):
        stop_comp(self._std)
        stop_comp(self._output)
        stop_ns(self._ns)

    def test_noprobs(self):
        call_process(['rtresurrect', './test/sys.rts'])
        call_process(['rtstart', './test/sys.rts'])
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rts'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_not_activated(self):
        call_process(['rtresurrect', './test/sys.rts'])
        call_process(['rtstart', './test/sys.rts'])
        call_process(['rtdeact', '/localhost/local.host_cxt/Std0.rtc'])
        wait_for_comp('Std0.rtc', state='Inactive')
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rts'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)

    def test_not_connected(self):
        call_process(['rtresurrect', './test/sys.rts'])
        call_process(['rtstart', './test/sys.rts'])
        call_process(['rtdis', '/localhost/local.host_cxt/Std0.rtc'])
        stdout, stderr, ret = call_process(['./rtcheck', './test/sys.rts'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)


def rtcheck_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcheckTests)


class rtcompTests(unittest.TestCase):
#class rtcompTests():
    def setUp(self):
        self._ns = start_ns()
        self._mgr = launch_manager()
        self._load_mgr()

    def tearDown(self):
        stop_manager(self._mgr)
        stop_ns(self._ns)


    def _load_mgr(self):
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Controller.so'), '-i',
            'ControllerInit', '-c', 'Controller'])
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Sensor.so'), '-i',
            'SensorInit', '-c', 'Sensor'])
        self.assertEqual(ret, 0)
        stdout, stderr, ret = call_process(['./rtmgr',
            '/localhost/local.host_cxt/manager.mgr', '-l',
            os.path.join(COMP_LIB_PATH, 'Motor.so'), '-i',
            'MotorInit', '-c', 'Motor'])
        self.assertEqual(ret, 0)

    def test_success(self):
        stdout, stderr, ret = call_process(['./rtcomp',
            '/localhost/local.host_cxt/manager.mgr', '-c',
            '/localhost/local.host_cxt/Controller0.rtc', '-p',
            '/localhost/local.host_cxt/Sensor0.rtc:in', '-p',
            '/localhost/local.host_cxt/Motor0.rtc:out'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._assert_comp_exists('CompositeRTC.rtc')

    def test_set_name(self):
        stdout, stderr, ret = call_process(['./rtcomp',
            '/localhost/local.host_cxt/manager.mgr', '-c',
            '/localhost/local.host_cxt/Controller0.rtc', '-p',
            '/localhost/local.host_cxt/Sensor0.rtc:in', '-p',
            '/localhost/local.host_cxt/Motor0.rtc:out', '-n',
            'Blurgle'])
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)
        self._assert_comp_exists('Blurgle.rtc')

    def _assert_comp_exists(self, name):
        wait_for_comp(name)
        stdout, stderr, ret = call_process(['./rtls',
            '/localhost/local.host_cxt/{0}'.format(name)])
        self.assertEqual(stdout, name)
        self.assertEqual(stderr, '')
        self.assertEqual(ret, 0)


def rtcomp_suite():
    return unittest.TestLoader().loadTestsFromTestCase(rtcompTests)


def suite():
    return unittest.TestSuite([rtact_suite(), rtdeact_suite(),
        rtreset_suite(), rtcat_suite(), rtcheck_suite(), rtcomp_suite()])


if __name__ == '__main__':
    if len(sys.argv) == 2:
        COMP_LIB_PATH = sys.argv[1]
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    unittest.main()

