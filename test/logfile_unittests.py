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

Unit tests for the log file classes

'''


import os
import os.path
import unittest

import rtshell.simpkl_log


# Test writing a complete file (write 10 entries or so)
# Test reading them all back, in order
# Test backing up
# Test backing up at the start of the file
# Test backing up at the end of the file
# Test iterator (for entry in log:)
# Test with statement


METADATA=[1, 'lot', 'of', ('meta', 'data')]
TIMESTAMPS=[0.2, 0.5, 1, 1.3, 1.7, 2.001, 3.2, 3.3, 3.4, 5.3]
DATA=['Val1', 'Value2', 'Entry 3', 'Data block 4', 'Value 5', 'Entry6',
        'Data 7', 'Val8', 'Entry 9', 'Val 10']

log_class=None


class WriteBase(unittest.TestCase):
    def setUp(self):
        self.log = log_class(filename='test.log', mode='w',
                meta=METADATA, verbose=True)

    def tearDown(self):
        self.log.finalise()
        self.log.close()
        if os.path.isfile(os.path.join(os.getcwd(), 'test.log')):
            os.remove(os.path.join(os.getcwd(), 'test.log'))


class ReadBase(unittest.TestCase):
    def setUp(self):
        self.log = log_class(filename='test.log', mode='r',
                meta=METADATA, verbose=True)
        self.write_test_log()

    def tearDown(self):
        self.log.finalise()
        self.log.close()
        if os.path.isfile(os.path.join(os.getcwd(), 'test.log')):
            os.remove(os.path.join(os.getcwd(), 'test.log'))

    def write_test_log(self):
        for t, d in zip(TIMESTAMPS, DATA):
            self.log.write(t, d)


class WriteTests(WriteBase):
    pass


class ReadTests(ReadBase):
    pass


class OtherTests(unittest.TestCase):
    def make_log(self):
        self.log = log_class(filename='test.log', mode='r',
                meta=METADATA, verbose=True)
        for t, d in zip(TIMESTAMPS, DATA):
            self.log.write(t, d)
        self.log.finalise()
        self.log.close()

    def test_with(self):
        pass

    def test_iterator(self):
        pass


def write_suite():
    return unittest.TestLoader().loadTestsFromTestCase(WriteTests)


def read_suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReadTests)


def other_suite():
    return unittest.TestLoader().loadTestsFromTestCase(OtherTests)

def suite():
    return unittest.TestSuite([write_suite(), read_suite(), other_suite()])

if __name__ == '__main__':
    print 'rtshell.simpkl_log.SimplePickleLog'
    log_class = rtshell.simpkl_log.SimplePickleLog
    unittest.main()

