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

Unit tests.

'''


import unittest

import rtshell.eval_const
import rtshell.rts_exceptions
import rtshell.port_types
import rtshell.user_mods

import blorg


class TestUserMods(unittest.TestCase):
    def test_load_mods(self):
        mods = rtshell.user_mods.load_mods('test_mod1,test_mod2')
        self.assertEqual(len(mods), 2)
        self.assertEqual(mods[0].name, 'test_mod1')
        self.assertEqual(type(mods[0].mod), type(rtshell.user_mods))
        self.assertEqual(mods[1].name, 'test_mod2')
        self.assertEqual(type(mods[1].mod), type(rtshell.user_mods))
        self.assertRaises(ImportError, rtshell.user_mods.load_mods, 'blurgle')

    def test_load_mods_and_poas(self):
        mods = rtshell.user_mods.load_mods_and_poas('test_mod1,test_mod2')
        self.assertEqual(len(mods), 4)
        self.assertEqual(mods[0].name, 'test_mod1')
        self.assertEqual(type(mods[0].mod), type(rtshell.user_mods))
        self.assertEqual(mods[1].name, 'test_mod1__POA')
        self.assertEqual(type(mods[1].mod), type(rtshell.user_mods))
        self.assertRaises(ImportError, rtshell.user_mods.load_mods_and_poas,
                'blorg')


class TestEvalConst(unittest.TestCase):
    def setUp(self):
        self.mods = [rtshell.user_mods.Module('test_mod1')]
        self.const = 'test_mod1.Dummy(4,2)'

    def test_replace_mod_name(self):
        self.assertEqual(rtshell.eval_const.replace_mod_name(self.const,
            self.mods), 'mods[0].mod.Dummy(4,2)')

    def test_replace_time(self):
        const = 'blurgle({time})'
        self.assert_(len(rtshell.eval_const.replace_time(const)) > len(const))

    def test_eval_const(self):
        class Data(object):
            def __init__(self, val):
                self.val = val

        self.assertEqual(rtshell.eval_const.eval_const('1', self.mods), 1)
        self.assertEqual(rtshell.eval_const.eval_const('list((1, 2, 3))',
            self.mods), [1, 2, 3])


class TestParseTargets(unittest.TestCase):
    def setUp(self):
        self.p1 = (['/', 'localhost', 'my.host_cxt', 'comp0.rtc'], 'input0',
                'namae', 'blorg.format')
        self.p2 = (['/', 'localhost', 'my.host_cxt', 'comp1.rtc'], 'out_put1',
                'namae2', None)
        self.p3 = (['/', 'localhost', 'my.host_cxt', 'comp1.rtc'], 'out_put1',
                None, 'blorg.format')
        self.p4 = (['/', 'localhost', 'my.host_cxt', 'comp0.rtc'], 'input0',
                None, None)

    def test_parse_targets(self):
        ps = rtshell.port_types.parse_targets(['/localhost/my.host_cxt/comp0.rtc:input0.namae#blorg.format',
            '/localhost/my.host_cxt/comp1.rtc:out_put1.namae2',
            '/localhost/my.host_cxt/comp1.rtc:out_put1#blorg.format',
            '/localhost/my.host_cxt/comp0.rtc:input0'])
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

