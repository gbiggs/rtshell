#!/usr/bin/env python2
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

Unit tests for the log classes

'''

from __future__ import print_function

import os
import os.path
import sys
import unittest

import rtshell.ilog
import rtshell.simpkl_log


METADATA=[1, 'lot', 'of', ('meta', 'data')]
TIMESTAMPS=[0.2, 0.5, 1, 1.3, 1.7, 2.001, 3.2, 3.3, 3.4, 5.3]
DATA=['Val1', 'Value2', 'Entry 3', 'Data block 4', 'Value 5', 'Entry6',
        'Data 7', 'Val8', 'Entry 9', 'Val 10']


VERBOSITY=False


#class WriteBase(unittest.TestCase):
class WriteBase():
    def setUp(self):
        self.log = rtshell.simpkl_log.SimplePickleLog(filename='test.log',
                mode='w', meta=METADATA, verbose=VERBOSITY)

    def tearDown(self):
        self.log.close()
        if os.path.isfile(os.path.join(os.getcwd(), 'test.log')):
            os.remove(os.path.join(os.getcwd(), 'test.log'))


class ReadBase(unittest.TestCase):
    def setUp(self):
        self.write_test_log()
        self.log = rtshell.simpkl_log.SimplePickleLog(filename='test.log',
                mode='r', meta=METADATA, verbose=VERBOSITY)

    def tearDown(self):
        self.log.close()
        if os.path.isfile(os.path.join(os.getcwd(), 'test.log')):
            os.remove(os.path.join(os.getcwd(), 'test.log'))

    def write_test_log(self):
        log = rtshell.simpkl_log.SimplePickleLog(filename='test.log', mode='w',
                meta=METADATA, verbose=VERBOSITY)
        for t, d in zip(TIMESTAMPS, DATA):
            log.write(t, d)
        log.close()


class WriteTests(WriteBase):
    def test_write(self):
        if VERBOSITY:
            print('===== write =====', file=sys.stderr)
        for t, d in zip(TIMESTAMPS, DATA):
            self.log.write(t, d)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)


class ReadTests(ReadBase):
    def test_read_whole_log(self):
        if VERBOSITY:
            print('===== read_whole_log =====', file=sys.stderr)
        for ii in range(10):
            entry = self.log.read()
            if not entry:
                # End of log
                self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
            else:
                ind, ts, d = entry[0]
                self.assertEqual(ind, ii)
                self.assertEqual(ts, TIMESTAMPS[ii])
                self.assertEqual(d, DATA[ii])
                if not self.log.eof:
                    self.assertEqual(self.log.pos, (ii + 1, TIMESTAMPS[ii + 1]))
                else:
                    self.assertEqual(self.log.pos, (ii + 1, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_start_at_start(self):
        if VERBOSITY:
            print('===== get_start_at_start =====', file=sys.stderr)
        self.assertEqual(self.log.start, (0, TIMESTAMPS[0]))
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_start_at_mid(self):
        if VERBOSITY:
            print('===== get_start_at_mid =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.start, (0, TIMESTAMPS[0]))
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 5)
        self.assertEqual(ts, TIMESTAMPS[5])
        self.assertEqual(d, DATA[5])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_start_at_eof(self):
        if VERBOSITY:
            print('===== get_start_at_eof =====', file=sys.stderr)
        for ii in range(11):
            self.log.read()
        self.assertEqual(self.log.start, (0, TIMESTAMPS[0]))
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual(self.log.read(), [])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_end_at_start(self):
        if VERBOSITY:
            print('===== get_end_at_start =====', file=sys.stderr)
        self.assertEqual(self.log.end, (9, TIMESTAMPS[-1]))
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_end_at_mid(self):
        if VERBOSITY:
            print('===== get_end_at_mid =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.end, (9, TIMESTAMPS[-1]))
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 5)
        self.assertEqual(ts, TIMESTAMPS[5])
        self.assertEqual(d, DATA[5])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_end_at_eof(self):
        if VERBOSITY:
            print('===== get_end_at_eof =====', file=sys.stderr)
        for ii in range(11):
            self.log.read()
        self.assertEqual(self.log.end, (9, TIMESTAMPS[9]))
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual(self.log.read(), [])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_eof(self):
        if VERBOSITY:
            print('===== read_eof =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assert_(self.log.eof)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual(self.log.read(), [])
        self.assert_(self.log.eof)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_start_start(self):
        if VERBOSITY:
            print('===== read_num_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.assertEqual([], self.log.read(number=0))
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_start_mid(self):
        if VERBOSITY:
            print('===== read_num_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(number=4)
        self.assertEqual(4, len(d))
        for ii in range(4):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (4, TIMESTAMPS[4]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_start_end(self):
        if VERBOSITY:
            print('===== read_num_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(number=10)
        self.assertEqual(10, len(d))
        for ii in range(10):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_start_eof(self):
        if VERBOSITY:
            print('===== read_num_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(number=11)
        self.assertEqual(10, len(d))
        for ii in range(10):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_mid_start(self):
        if VERBOSITY:
            print('===== read_num_mid_start =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        self.assertRaises(ValueError, self.log.read, number=-1)
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_mid_mid(self):
        if VERBOSITY:
            print('===== read_num_mid_mid =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(number=4)
        self.assertEqual(4, len(d))
        for ii in range(4):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (7, TIMESTAMPS[7]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_mid_end(self):
        if VERBOSITY:
            print('===== read_num_mid_end =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(number=7)
        self.assertEqual(7, len(d))
        for ii in range(7):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_mid_eof(self):
        if VERBOSITY:
            print('===== read_num_mid_eof =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(number=8)
        self.assertEqual(7, len(d))
        for ii in range(7):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_num_end_eof(self):
        if VERBOSITY:
            print('===== read_num_end_eof =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read(number=2))
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_start_start(self):
        if VERBOSITY:
            print('===== read_ts_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.assertEqual([], self.log.read(timestamp=0.1))
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(timestamp=0.2)
        self.assertEqual(d[0][0], 0)
        self.assertEqual(d[0][1], TIMESTAMPS[0])
        self.assertEqual(d[0][2], DATA[0])
        self.assertEqual(self.log.pos, (1, TIMESTAMPS[1]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_start_mid(self):
        if VERBOSITY:
            print('===== read_ts_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(timestamp=1.3)
        self.assertEqual(4, len(d))
        for ii in range(4):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (4, TIMESTAMPS[4]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_start_mid_between(self):
        if VERBOSITY:
            print('===== read_ts_start_mid_between =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(timestamp=1.45)
        self.assertEqual(4, len(d))
        for ii in range(4):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (4, TIMESTAMPS[4]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_start_end(self):
        if VERBOSITY:
            print('===== read_ts_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(timestamp=5.3)
        self.assertEqual(10, len(d))
        for ii in range(10):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_start_eof(self):
        if VERBOSITY:
            print('===== read_ts_start_mid =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        d = self.log.read(timestamp=5.4)
        self.assertEqual(10, len(d))
        for ii in range(10):
            self.assertEqual(d[ii][0], ii)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii])
            self.assertEqual(d[ii][2], DATA[ii])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_mid_start(self):
        if VERBOSITY:
            print('===== read_ts_mid_start =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        self.assertRaises(ValueError, self.log.read, timestamp=-1)
        self.assertEqual([], self.log.read(timestamp=0.1))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_mid_mid(self):
        if VERBOSITY:
            print('===== read_ts_mid_mid =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(timestamp=3.25)
        self.assertEqual(4, len(d))
        for ii in range(4):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (7, TIMESTAMPS[7]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_mid_end(self):
        if VERBOSITY:
            print('===== read_ts_mid_end =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(timestamp=5.3)
        self.assertEqual(7, len(d))
        for ii in range(7):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_mid_eof(self):
        if VERBOSITY:
            print('===== read_ts_mid_eof =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        d = self.log.read(timestamp=5.4)
        self.assertEqual(7, len(d))
        for ii in range(7):
            self.assertEqual(d[ii][0], ii + 3)
            self.assertEqual(d[ii][1], TIMESTAMPS[ii + 3])
            self.assertEqual(d[ii][2], DATA[ii + 3])
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_read_ts_end_eof(self):
        if VERBOSITY:
            print('===== read_ts_end_eof =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.assertEqual([], self.log.read(timestamp=5.4))
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_backup_start(self):
        if VERBOSITY:
            print('===== backup_start =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log._backup_one()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assertEqual(self.log.pos, (1, TIMESTAMPS[1]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_backup_to_start(self):
        if VERBOSITY:
            print('===== backup_to_start =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.read()
        self.assertEqual(self.log.pos, (1, TIMESTAMPS[1]))
        self.log._backup_one()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.log.read()
        self.log._backup_one()
        self.log._backup_one()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assertEqual(self.log.pos, (1, TIMESTAMPS[1]))
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_backup_mid(self):
        if VERBOSITY:
            print('===== backup_mid =====', file=sys.stderr)
        for ii in range(3):
            self.log.read()
        self.assertEqual(self.log.pos, (3, TIMESTAMPS[3]))
        self.log._backup_one()
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_backup_end(self):
        if VERBOSITY:
            print('===== backup_end =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log._backup_one()
        self.assertEqual(self.log.pos, (8, TIMESTAMPS[8]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 8)
        self.assertEqual(ts, TIMESTAMPS[8])
        self.assertEqual(d, DATA[8])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_backup_eof(self):
        if VERBOSITY:
            print('===== backup_eof =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log._backup_one()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_rewind_at_start(self):
        if VERBOSITY:
            print('===== rewind_at_start =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.rewind()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_rewind_at_mid(self):
        if VERBOSITY:
            print('===== rewind_at_mid =====', file=sys.stderr)
        for ii in range(4):
            self.log.read()
        self.assertEqual(self.log.pos, (4, TIMESTAMPS[4]))
        self.log.rewind()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_rewind_at_end(self):
        if VERBOSITY:
            print('===== rewind_at_mid =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.rewind()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_rewind_at_eof(self):
        if VERBOSITY:
            print('===== rewind_at_mid =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assert_(self.log.eof)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.log.rewind()
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_start_ind(self):
        if VERBOSITY:
            print('===== seek_start_start_ind =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(index=0)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_mid_ind(self):
        if VERBOSITY:
            print('===== seek_start_mid_ind =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(index=2)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_end_ind(self):
        if VERBOSITY:
            print('===== seek_start_end_ind =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(index=9)
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_eof_ind(self):
        if VERBOSITY:
            print('===== seek_start_eof_ind =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(index=11)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_start_ind(self):
        if VERBOSITY:
            print('===== seek_mid_start_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=0)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_rewind_ind(self):
        if VERBOSITY:
            print('===== seek_mid_rewind_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=2)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_mid_ind(self):
        if VERBOSITY:
            print('===== seek_mid_mid_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=5)
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 5)
        self.assertEqual(ts, TIMESTAMPS[5])
        self.assertEqual(d, DATA[5])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_ff_ind(self):
        if VERBOSITY:
            print('===== seek_mid_ff_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=7)
        self.assertEqual(self.log.pos, (7, TIMESTAMPS[7]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 7)
        self.assertEqual(ts, TIMESTAMPS[7])
        self.assertEqual(d, DATA[7])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_end_ind(self):
        if VERBOSITY:
            print('===== seek_mid_end_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=9)
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_eof_ind(self):
        if VERBOSITY:
            print('===== seek_mid_eof_ind =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(index=10)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_start_ind(self):
        if VERBOSITY:
            print('===== seek_end_start_ind =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(index=0)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_mid_ind(self):
        if VERBOSITY:
            print('===== seek_end_mid_ind =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(index=2)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_end_ind(self):
        if VERBOSITY:
            print('===== seek_end_end_ind =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(index=9)
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_eof_ind(self):
        if VERBOSITY:
            print('===== seek_end_eof_ind =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(index=10)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_start_ind(self):
        if VERBOSITY:
            print('===== seek_eof_start_ind =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(index=0)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_mid_ind(self):
        if VERBOSITY:
            print('===== seek_eof_mid_ind =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(index=2)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_end_ind(self):
        if VERBOSITY:
            print('===== seek_eof_end_ind =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(index=9)
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_eof_ind(self):
        if VERBOSITY:
            print('===== seek_eof_eof_ind =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(index=10)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_before_start_ts(self):
        if VERBOSITY:
            print('===== seek_start_before_start_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[0] - 1)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_start_ts(self):
        if VERBOSITY:
            print('===== seek_start_start_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[0])
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_before_mid_ts(self):
        if VERBOSITY:
            print('===== seek_start_before_mid_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[2] - \
                (TIMESTAMPS[2] - TIMESTAMPS[1]) * 0.6)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_mid_ts(self):
        if VERBOSITY:
            print('===== seek_start_mid_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[2])
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_end_ts(self):
        if VERBOSITY:
            print('===== seek_start_end_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[9])
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_start_eof_ts(self):
        if VERBOSITY:
            print('===== seek_start_eof_ts =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        self.log.seek(timestamp=TIMESTAMPS[9] + 1)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_before_start_ts(self):
        if VERBOSITY:
            print('===== seek_mid_before_start_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[0] - 1)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_start_ts(self):
        if VERBOSITY:
            print('===== seek_mid_start_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[0])
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_rewind_ts(self):
        if VERBOSITY:
            print('===== seek_mid_rewind_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[2])
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_before_mid_ts(self):
        if VERBOSITY:
            print('===== seek_mid_before_mid_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[2] - \
                (TIMESTAMPS[2] - TIMESTAMPS[1]) * 0.6)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_mid_ts(self):
        if VERBOSITY:
            print('===== seek_mid_mid_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[5])
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 5)
        self.assertEqual(ts, TIMESTAMPS[5])
        self.assertEqual(d, DATA[5])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_after_mid_ts(self):
        if VERBOSITY:
            print('===== seek_mid_after_mid_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[7] - \
                (TIMESTAMPS[7] - TIMESTAMPS[6]) * 0.6)
        self.assertEqual(self.log.pos, (7, TIMESTAMPS[7]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 7)
        self.assertEqual(ts, TIMESTAMPS[7])
        self.assertEqual(d, DATA[7])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_ff_ts(self):
        if VERBOSITY:
            print('===== seek_mid_ff_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[7])
        self.assertEqual(self.log.pos, (7, TIMESTAMPS[7]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 7)
        self.assertEqual(ts, TIMESTAMPS[7])
        self.assertEqual(d, DATA[7])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_end_ts(self):
        if VERBOSITY:
            print('===== seek_mid_end_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[9])
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_mid_eof_ts(self):
        if VERBOSITY:
            print('===== seek_mid_eof_ts =====', file=sys.stderr)
        for ii in range(5):
            self.log.read()
        self.assertEqual(self.log.pos, (5, TIMESTAMPS[5]))
        self.log.seek(timestamp=TIMESTAMPS[9] + 1)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_start_ts(self):
        if VERBOSITY:
            print('===== seek_end_start_ts =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(timestamp=TIMESTAMPS[0])
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_before_mid_ts(self):
        if VERBOSITY:
            print('===== seek_end_before_mid_ts =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(timestamp=TIMESTAMPS[2] - \
                (TIMESTAMPS[2] - TIMESTAMPS[1]) * 0.6)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_mid_ts(self):
        if VERBOSITY:
            print('===== seek_end_mid_ts =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(timestamp=TIMESTAMPS[2])
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_end_ts(self):
        if VERBOSITY:
            print('===== seek_end_end_ts =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(timestamp=TIMESTAMPS[9])
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_end_eof_ts(self):
        if VERBOSITY:
            print('===== seek_end_eof_ts =====', file=sys.stderr)
        for ii in range(9):
            self.log.read()
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.log.seek(timestamp=TIMESTAMPS[9] + 1)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_start_ts(self):
        if VERBOSITY:
            print('===== seek_eof_start_ts =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[9]))
        self.assert_(self.log.eof)
        self.log.seek(timestamp=TIMESTAMPS[0])
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 0)
        self.assertEqual(ts, TIMESTAMPS[0])
        self.assertEqual(d, DATA[0])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_before_mid_ts(self):
        if VERBOSITY:
            print('===== seek_eof_before_mid_ts =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(timestamp=TIMESTAMPS[2] - \
                (TIMESTAMPS[2] - TIMESTAMPS[1]) * 0.6)
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_mid_ts(self):
        if VERBOSITY:
            print('===== seek_eof_mid_ts =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(timestamp=TIMESTAMPS[2])
        self.assertEqual(self.log.pos, (2, TIMESTAMPS[2]))
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 2)
        self.assertEqual(ts, TIMESTAMPS[2])
        self.assertEqual(d, DATA[2])
        self.assert_(not self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_end_ts(self):
        if VERBOSITY:
            print('===== seek_eof_end_ts =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(timestamp=TIMESTAMPS[9])
        self.assertEqual(self.log.pos, (9, TIMESTAMPS[9]))
        self.assert_(not self.log.eof)
        ind, ts, d = self.log.read()[0]
        self.assertEqual(ind, 9)
        self.assertEqual(ts, TIMESTAMPS[9])
        self.assertEqual(d, DATA[9])
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_seek_eof_eof_ts(self):
        if VERBOSITY:
            print('===== seek_eof_eof_ts =====', file=sys.stderr)
        for ii in range(10):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.seek(timestamp=TIMESTAMPS[9] + 1)
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assertEqual([], self.log.read())
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_get_cur_pos(self):
        if VERBOSITY:
            print('===== get_cur_pos =====', file=sys.stderr)
        self.assertEqual(self.log.pos, (0, TIMESTAMPS[0]))
        for ii in range(4):
            self.log.read()
        self.assertEqual(self.log.pos, (4, TIMESTAMPS[4]))
        for ii in range(6):
            self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        self.log.read()
        self.assertEqual(self.log.pos, (10, TIMESTAMPS[-1]))
        self.assert_(self.log.eof)
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)



class OtherTests(unittest.TestCase):
    def setUp(self):
        self.write_test_log()

    def tearDown(self):
        if os.path.isfile(os.path.join(os.getcwd(), 'test.log')):
            os.remove(os.path.join(os.getcwd(), 'test.log'))

    def write_test_log(self):
        log = rtshell.simpkl_log.SimplePickleLog(filename='test.log', mode='w',
                meta=METADATA, verbose=VERBOSITY)
        for t, d in zip(TIMESTAMPS, DATA):
            log.write(t, d)
        log.close()

    def test_with(self):
        if VERBOSITY:
            print('===== with =====', file=sys.stderr)
        with rtshell.simpkl_log.SimplePickleLog(filename='test.log',
                mode='r', meta=METADATA, verbose=VERBOSITY) as log:
            for ii in range(10):
                entry = log.read()
                if not entry:
                    # End of log
                    self.assertEqual(log.pos, (10, TIMESTAMPS[-1]))
                else:
                    ind, ts, d = entry[0]
                    self.assertEqual(ind, ii)
                    self.assertEqual(ts, TIMESTAMPS[ii])
                    self.assertEqual(d, DATA[ii])
                    if not log.eof:
                        self.assertEqual(log.pos, (ii + 1, TIMESTAMPS[ii + 1]))
                    else:
                        self.assertEqual(log.pos, (ii + 1, TIMESTAMPS[-1]))
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)

    def test_iterator(self):
        if VERBOSITY:
            print('===== iterator =====', file=sys.stderr)
        log = rtshell.simpkl_log.SimplePickleLog(filename='test.log',
                mode='r', meta=METADATA, verbose=VERBOSITY)
        for (ii, entry) in enumerate(log):
            if not entry:
                # End of log
                self.assertEqual(lf.pos, (10, TIMESTAMPS[-1]))
            else:
                ind, ts, d = entry
                self.assertEqual(ind, ii)
                self.assertEqual(ts, TIMESTAMPS[ii])
                self.assertEqual(d, DATA[ii])
                if not log.eof:
                    self.assertEqual(log.pos, (ii + 1, TIMESTAMPS[ii + 1]))
                else:
                    self.assertEqual(log.pos, (ii + 1, TIMESTAMPS[-1]))
        log.close()
        if VERBOSITY:
            print('===== ===== =====', file=sys.stderr)


class TimestampTests(unittest.TestCase):
    def test_lt(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < \
                rtshell.ilog.EntryTS(sec=2, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < \
                rtshell.ilog.EntryTS(sec=2, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < \
                rtshell.ilog.EntryTS(sec=1, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) < \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) < \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) < \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < 2.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < 2.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < 1.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) < 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) < 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) < 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) < 1.000000001,
                False)

    def test_le(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= \
                rtshell.ilog.EntryTS(sec=2, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= \
                rtshell.ilog.EntryTS(sec=2, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= \
                rtshell.ilog.EntryTS(sec=1, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) <= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) <= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) <= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= 2.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= 2.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= 1.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) <= 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) <= 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) <= 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) <= 1.000000001,
                False)

    def test_eq(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == \
                rtshell.ilog.EntryTS(sec=2, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == \
                rtshell.ilog.EntryTS(sec=2, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == \
                rtshell.ilog.EntryTS(sec=1, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) == \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) == \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) == \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == 2.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == 2.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == 1.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) == 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) == 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) == 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) == 1.000000001,
                False)

    def test_ne(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != \
                rtshell.ilog.EntryTS(sec=2, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != \
                rtshell.ilog.EntryTS(sec=2, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != \
                rtshell.ilog.EntryTS(sec=1, nsec=2), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) != \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) != \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) != \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != 2.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != 2.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != 1.000000002,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) != 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) != 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) != 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) != 1.000000001, True)

    def test_gt(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > \
                rtshell.ilog.EntryTS(sec=2, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > \
                rtshell.ilog.EntryTS(sec=2, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > \
                rtshell.ilog.EntryTS(sec=1, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > \
                rtshell.ilog.EntryTS(sec=1, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) > \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) > \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) > \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > 2.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > 2.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > 1.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) > 1.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) > 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) > 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) > 1.000000001,
                True)

    def test_gt(self):
        # EntryTS type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= \
                rtshell.ilog.EntryTS(sec=2, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= \
                rtshell.ilog.EntryTS(sec=2, nsec=1), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= \
                rtshell.ilog.EntryTS(sec=1, nsec=2), False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) >= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) >= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) >= \
                rtshell.ilog.EntryTS(sec=1, nsec=1), True)
        # Float type
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= 2.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= 2.000000001,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= 1.000000002,
                False)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=1) >= 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=1, nsec=2) >= 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=1) >= 1.000000001,
                True)
        self.assertEqual(rtshell.ilog.EntryTS(sec=2, nsec=2) >= 1.000000001,
                True)

    def test_construction(self):
        ts = rtshell.ilog.EntryTS(sec=1, nsec=2)
        self.assertEqual(ts.sec, 1)
        self.assertEqual(ts.nsec, 2)
        ts = rtshell.ilog.EntryTS(time=1.000000002)
        self.assertEqual(ts.sec, 1)
        self.assertEqual(ts.nsec, 2)

    def test_to_float(self):
        ts = rtshell.ilog.EntryTS(sec=1, nsec=0)
        self.assertEqual(ts.float, 1.0)
        ts = rtshell.ilog.EntryTS(sec=1, nsec=2)
        self.assertEqual(ts.float, 1.000000002)
        ts = rtshell.ilog.EntryTS(sec=0, nsec=200)
        self.assertEqual(ts.float, 0.0000002)


def write_suite():
    return unittest.TestLoader().loadTestsFromTestCase(WriteTests)


def read_suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReadTests)


def other_suite():
    return unittest.TestLoader().loadTestsFromTestCase(OtherTests)


def suite():
    return unittest.TestSuite([write_suite(), read_suite(), other_suite()])


if __name__ == '__main__':
    unittest.main()

