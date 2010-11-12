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

Pickle-based log file.

'''


import os
import pickle

import ilogfile


###############################################################################
## Simple pickle-based log file object. Its support for the full log file
## interface is rudimentary and slow (although writing and simple reading
## should be fast enough).
##
## The simple pickle-based format is as follows (each entry is serialised):
## Port specification (in the metadata block)
## [Data entries: (Index, Time stamp, Data)]

class SimplePickleLog(ilogfile.LogFile):
    def __init__(self, filename='', *args, **kwargs):
        super(PickleLog, self).__init__(*args, **kwargs)
        self._fn = filename
        self._cur_pos = None
        self._start = None
        self._end = None
        self._next = None
        self._write_ind = 1

    def __str__(self):
        return 'PickleLog({0}, {1})'.format(self._fn, self._mode)

    def open(self):
        super(SimplePickleLog, self).open(self)
        if self._mode == 'r':
            flags = 'rb'
        elif self._mode == 'w':
            flags = 'wb'
        else:
            raise NotImplementedError
        self._file = open(self._fn, flags)
        self._init_log()

    def close(self):
        super(SimplePickleLog, self).close(self)
        self._file.close()

    def write(self, timestamp, data):
        val = (self._write_ind, timestamp, data)
        self._write(val)
        self._update_cur_pos(val)
        self._write_ind += 1

    def read(self, time_limit=None, number=None):
        if number is not None:
            res = []
            if self._next:
                res.append(self._next)
                self._update_cur_pos(self._next)
                self._next = None
                number -= 1
            try:
                for ii in range(number):
                    val = self._read()
                    res.append(val)
                    self._update_cur_pos(val)
            except ilogfile.EndOfLogError:
                pass
            return res
        elif time_limit is not None:
            res = []
            if self._next:
                if self._next[0] > time_limit:
                    # The time limit is before the next item - nothing to read
                    return []
                else:
                    res.append(self._next)
                    self._update_cur_pos(self._next)
                    # In case there is an immediate exception, clear next now
                    self._next = None
            try:
                self._next = self._read()
                self._update_cur_pos(self._next)
                while self._next[0] <= time_limit:
                    res.append(self._next)
                    self._update_cur_pos(self._next)
                    # In case there is an immediate exception, clear next now
                    self._next = None
                    self._next = self._read()
            except ilogfile.EndOfLogError:
                pass
            return res
        else:
            if self._next:
                res = [self._next]
                self._update_cur_pos(self._next)
                self._next = None
                return res
            else:
                try:
                    val = self._read()
                    self._update_cur_pos(val)
                    return [val]
                except ilogfile.EndOfLogError:
                    return []

    def rewind(self):
        super(SimplePickleLog, self).rewind(self)
        self._file.seek(0)
        self._next = None
        self._write_ind = 1

    def shift(self, timestamp=None, index=None):
        super(SimplePickleLog, self).shift_to(self)
        if index is not None:
            self._shift_to_index(index)
        elif timestamp is not None:
            self._shift_to_timestamp(timestamp)
        # Do nothing if neither is set

    def _backup_one(self):
        '''Reverses in the file one entry.

        This function is neither fast nor efficient. It involves stepping back
        one byte at a time to find the start of the previous entry.

        '''
        def backup():
            # Start by going back one byte
            self._file.seek(-1, os.SEEK_CUR)
            size = 1
            while True:
                try:
                    # Attempt to read and unpickle
                    self._next = self._read()
                    # Unpickle was a success
                    break
                except ilogfile.EndOfLogError:
                    # Read or unpickle failed, so move back one byte
                    self._file.seek(-1, os.SEEK_CUR)
                    size += 1
        # Back up two entries to get the new current position, then forward one
        backup()
        backup()
        self._cur_pos = (self._next[0], self._next[1])
        self.read()

    def _get_cur_pos(self):
        if self._cur_pos is None:
            self._next = self._read()
            self._cur_pos = (self._next[0], self._next[1])
        return self._cur_pos

    def _get_start(self):
        if self._start is not None:
            # Return the cached value
            return self._start
        # Save the current position
        current = self._file.tell()
        # Move to the start
        self._file.seek(0)
        # Skip the metadata block
        self._read()
        # Read the first entry
        index, timestamp, data = self._read()
        self._start = (index, timestamp)
        self._start, data = self._read()
        # Go back to the previous position
        self._file.seek(current)
        return self._start

    def _get_end(self):
        if self._end is not None:
            # Return the cached value
            return self._end
        # Save the current position and the current next
        current = self._file.tell()
        next = self._next
        cur_pos = self._cur_pos
        # Move to the end
        self._file.seek(-1, os.SEEK_END)
        # Move back one entry
        self._backup_one()
        # self._next now contains the final entry in the log
        self._end = (self._next[0], self._next[1])
        # Go back to the previous position
        self._file.seek(current)
        self._next = next
        self.cur_pos = cur_pos
        return self._end

    def _init_log(self):
        if self._mode == 'r':
            # Read out the metadata
            self._meta = self._read()
            # Grab the time of the first entry and make it the current time
            self._cur_time = self._get_start_time()
        else:
            # Write the metadata
            self._write(self._meta)

    def _read(self):
        '''Read a single entry from the file.'''
        try:
            data = pickle.load(self._file)
        except EOFError:
            self._eof = True
            raise ilogfile.EndOfLogError
        return data

    def _shift_to_index(self, ind):
        '''Shifts forward or backward in the file to find the index.'''
        if ind == cur[0]:
            return
        elif ind < cur[0]:
            # Rewind
            # TODO: Rewinding may be more efficient in many cases if done by
            # fast-forwarding from the start of the file rather than traversing
            # backwards.
            self._backup_one()
            while self._next[0] > ind:
                self._backup_one()
        else:
            # Fast-forward
            if self._next is None:
                self._next = self._read()
            while self._next[0] < ind:
                self._next = self._read()
            self._cur_pos = (self._next[0], self._next[1])

    def _shift_to_timestamp(self, ts):
        '''Shifts forward or backward in the file to find the timestamp.'''
        if ts == cur[1]:
            return
        elif ts < cur[1]:
            # Rewind
            self._backup_one()
            while self._next[1] > ts:
                self._backup_one()
        else:
            # Fast-forward
            if self._next is None:
                self._next = self._read()
            while self._next[0] < ind:
                self._next = self._read()
            self._cur_pos = (self._next[0], self._next[1])

    def _update_cur_pos(self, val):
        '''Updates the current pos from a data entry.'''
        self._cur_pos = (val[0], val[1])

    def _write(self, data):
        '''Pickle some data and write it to the file.'''
        pickle.dump(data, self._file, pickle.HIGHEST_PROTOCOL)

