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

Unit tests.

'''


import unittest

import rtshell.port_types
import rtshell.modmgr
import rtshell.rts_exceptions

import blorg


class TestUserMods(unittest.TestCase):
    def setUp(self):
        self.mm = rtshell.modmgr.ModuleMgr()

    def test_load_mods(self):
        self.mm.load_mods(['test_mod1','test_mod2'])
        self.assertEqual(len(self.mm.loaded_mod_names), 3)
        self.assert_('test_mod1' in self.mm.loaded_mod_names)
        self.assert_('test_mod2' in self.mm.loaded_mod_names)
        self.assertRaises(ImportError, self.mm.load_mod, 'blurgle')

    def test_load_mods_and_poas(self):
        self.mm.load_mods_and_poas(['test_mod1','test_mod2'])
        self.assertEqual(len(self.mm.loaded_mod_names), 5)
        self.assert_('test_mod1' in self.mm.loaded_mod_names)
        self.assert_('test_mod1__POA' in self.mm.loaded_mod_names)
        self.assert_('test_mod2' in self.mm.loaded_mod_names)
        self.assert_('test_mod2__POA' in self.mm.loaded_mod_names)
        self.assertRaises(ImportError, self.mm.load_mods_and_poas, 'blorg')


class TestEvalConst(unittest.TestCase):
    def setUp(self):
        self.const = 'test_mod1.Dummy(4,2)'
        self.mm = rtshell.modmgr.ModuleMgr()
        self.mm.load_mods(['test_mod1'])

    def test_replace_mod_name(self):
        self.assertEqual(self.mm._repl_mod_name(self.const),
            'self._mods["test_mod1"].mod.Dummy(4,2)')

    def test_replace_time(self):
        const = 'blurgle({time})'
        self.assert_(len(rtshell.modmgr._replace_time(const)) > len(const))

    def test_eval_const(self):
        class Data(object):
            def __init__(self, val):
                self.val = val

        self.assertEqual(self.mm.evaluate('1'), 1)
        self.assertEqual(self.mm.evaluate('list((1, 2, 3))'), [1, 2, 3])


class TestParseTargets(unittest.TestCase):
    def setUp(self):
        self.t1 = '/localhost/my.host_cxt/comp0.rtc:input0.namae#blorg.format'
        self.t2 = '/localhost/my.host_cxt/comp1.rtc:out_put1.namae2'
        self.t3 = '/localhost/my.host_cxt/comp1.rtc:out_put1#blorg.format'
        self.t4 = '/localhost/my.host_cxt/comp0.rtc:input0'
        self.p1 = (['/', 'localhost', 'my.host_cxt', 'comp0.rtc'], 'input0',
                'namae', 'blorg.format', self.t1)
        self.p2 = (['/', 'localhost', 'my.host_cxt', 'comp1.rtc'], 'out_put1',
                'namae2', None, self.t2)
        self.p3 = (['/', 'localhost', 'my.host_cxt', 'comp1.rtc'], 'out_put1',
                None, 'blorg.format', self.t3)
        self.p4 = (['/', 'localhost', 'my.host_cxt', 'comp0.rtc'], 'input0',
                None, None, self.t4)

    def test_parse_targets(self):
        ps = rtshell.port_types.parse_targets(['/localhost/my.host_cxt/comp0.rtc:input0.namae#blorg.format',
            '/localhost/my.host_cxt/comp1.rtc:out_put1.namae2',
            '/localhost/my.host_cxt/comp1.rtc:out_put1#blorg.format',
            '/localhost/my.host_cxt/comp0.rtc:input0'])
        print ps[0]
        self.assertEqual(ps[0], self.p1)
        self.assertEqual(ps[1], self.p2)
        self.assertEqual(ps[2], self.p3)
        self.assertEqual(ps[3], self.p4)
        self.assertRaises(rtshell.rts_exceptions.BadPortSpecError,
                rtshell.port_types.parse_targets, ['this_is_wrong'])
        self.assertRaises(rtshell.rts_exceptions.BadPortSpecError,
                rtshell.port_types.parse_targets, ['/localhost/comp0.rtc'])
        self.assertRaises(rtshell.rts_exceptions.BadPortSpecError,
                rtshell.port_types.parse_targets, [''])


if __name__ == '__main__':
    unittest.main()


# vim: tw=79

