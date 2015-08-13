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

Text-based log.

'''


import copy
import os

from rtshell import ilog


###############################################################################
## Text-based log object. It only supports writing log files. It relies on
## the data types having suitable __repr__ methods.

class TextLog(ilog.Log):
    def __init__(self, filename='', *args, **kwargs):
        self._is_open = False
        self._fn = filename
        super(TextLog, self).__init__(*args, **kwargs)

    def __str__(self):
        if self._is_open:
            return 'TextLog({0}, {1}) at position {2}.'.format(self._fn,
                    self._mode, self._file.tell())
        else:
            return 'TextLog({0}, {1}).'.format(self._fn, self._mode)

    def write(self, timestamp, data):
        pos = self._file.tell()
        self._file.write('{0}\t{1}\n'.format(timestamp, data))
        self._vb_print('Wrote entry at {0}.'.format(pos))

    def _close(self):
        if not self._is_open:
            return
        self._file.close()
        self._is_open = False
        self._vb_print('Closed file.')

    def _get_cur_pos(self):
        if self._is_open:
            self._vb_print('Current position: {0}'.format(self._file.tell()))
            return self._file.tell()
        else:
            self._vb_print('Current position: file closed.')
            return 0

    def _open(self):
        if self._is_open:
            return
        if self._mode == 'w':
            flags = 'w'
        else:
            raise NotImplementedError
        self._file = open(self._fn, flags)
        self._is_open = True
        self._vb_print('Opened file {0} in mode {1}.'.format(self._fn,
            self._mode))

