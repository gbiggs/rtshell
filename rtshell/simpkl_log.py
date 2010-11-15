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

Pickle-based log.

'''


import os
import pickle

import ilog


###############################################################################
## Simple pickle-based log object. Its support for the full log interface
## is rudimentary and slow (although writing and simple reading should be fast
## enough).
##
## The simple pickle-based format is as follows (each entry is serialised):
## Port specification (in the metadata block)
## [Data entries: (Index, Time stamp, Data)]

class SimplePickleLog(ilog.Log):
    def __init__(self, filename='', *args, **kwargs):
        self._is_open = False
        self._fn = filename
        self._cur_pos = None
        self._start = None
        self._end = None
        self._next = None
        self._write_ind = 1
        super(SimplePickleLog, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'PickleLog({0}, {1})'.format(self._fn, self._mode)

    def open(self):
        if self._is_open:
            return
        super(SimplePickleLog, self).open()
        if self._mode == 'r':
            flags = 'rb'
        elif self._mode == 'w':
            flags = 'wb'
        else:
            raise NotImplementedError
        self._file = open(self._fn, flags)
        self._init_log()
        self._is_open = True
        self._vb_print('Opened file {0} in mode {1}.'.format(self._fn,
            self._mode))

    def close(self):
        if not self._is_open:
            return
        super(SimplePickleLog, self).close()
        self._file.close()
        self._is_open = False
        self._vb_print('Closed file.')

    def write(self, timestamp, data):
        val = (self._write_ind, timestamp, data)
        self._write(val)
        self._update_cur_pos(val)
        self._write_ind += 1
        self._vb_print('Wrote entry at ({0}, {1}).'.format(val[0], val[1]))

    def read(self, time_limit=None, number=None):
        if number is not None:
            self._vb_print('Reading {0} entries.'.format(number))
            res = []
            if self._next:
                self._vb_print('Starting with _next.')
                res.append(self._next)
                self._update_cur_pos(self._next)
                self._next = None
                number -= 1
            try:
                for ii in range(number):
                    val = self._read()
                    res.append(val)
                    self._update_cur_pos(val)
                    self._vb_print('Read entry {0} of {1}, current position ' \
                            'is {2}.'.format(ii, number, self._cur_pos))
            except ilog.EndOfLogError:
                self._vb_print('End of log.')
                pass
            return res
        elif time_limit is not None:
            self._vb_print('Reading until time stamp {0}.'.format(time_limit))
            res = []
            if self._next:
                self._vb_print('Starting with _next.')
                if self._next[0] > time_limit:
                    # The time limit is before the next item - nothing to read
                    self._vb_print('_next is beyond the time limit.')
                    return []
                else:
                    res.append(self._next)
                    self._update_cur_pos(self._next)
                    # In case there is an immediate exception, clear next now
                    self._vb_print('Used _next at position ({0}, {1}), ' \
                            'current position is {2}.'.format(self._next[0],
                                self._next[1], self._cur_pos))
                    self._next = None
            try:
                self._next = self._read()
                while self._next[0] <= time_limit:
                    res.append(self._next)
                    self._update_cur_pos(self._next)
                    self._vb_print('Read entry, current position is {0}.'.format(
                            self._cur_pos))
                    # In case there is an immediate exception, clear next now
                    self._next = None
                    self._next = self._read()
                self._vb_print('Finished reading; current position is ' \
                        '{0}.'.format(self._cur_pos))
            except ilog.EndOfLogError:
                self._vb_print('End of log.')
                pass
            return res
        else:
            self._vb_print('Reading a single entry.')
            if self._next:
                self._vb_print('Using _next.')
                res = [self._next]
                self._update_cur_pos(self._next)
                self._vb_print('Current position is {0}'.format(self._cur_pos))
                self._next = None
                return res
            else:
                try:
                    val = self._read()
                    self._update_cur_pos(val)
                    self._vb_print('Read entry, current position is ' \
                            '{0}.'.format(self._cur_pos))
                    return [val]
                except ilog.EndOfLogError:
                    self._vb_print('End of log.')
                    return []

    def rewind(self):
        self._vb_print('Rewinding log from position {0}.'.format(
                self._cur_pos))
        super(SimplePickleLog, self).rewind()
        if self._mode == 'r':
            self._file.seek(0)
        else:
            self._file.truncate()
        self._next = None
        self._write_ind = 1
        self._init_log()

    def shift(self, timestamp=None, index=None):
        self._vb_print('Shifting log from position {0}.'.format(self._cur_pos))
        super(SimplePickleLog, self).shift_to()
        if index is not None:
            self._shift_to_index(index)
        elif timestamp is not None:
            self._shift_to_timestamp(timestamp)
        # Do nothing if neither is set
        self._vb_print('New current position: {0}.'.format(self._cur_pos))

    def _backup_one(self):
        '''Reverses in the log one entry.

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
                except ilog.EndOfLogError:
                    # Read or unpickle failed, so move back one byte
                    self._file.seek(-1, os.SEEK_CUR)
                    size += 1
        self._vb_print('Backing up one entry from {0}.'.format(self._cur_pos))
        # Back up two entries to get the new current position, then forward one
        backup()
        backup()
        self._cur_pos = (self._next[0], self._next[1])
        # This effectively moves the next entry to read forward one
        self._next = None
        self._vb_print('New current position: {0}.'.format(self._cur_pos))

    def _get_cur_pos(self):
        if self._cur_pos is None:
            if self._next is None:
                self._next = self._read()
            self._cur_pos = (self._next[0], self._next[1])
        self._vb_print('Current position: {0}'.format(self._cur_pos))
        return self._cur_pos

    def _get_start(self):
        if self._start is not None:
            # Return the cached value
            self._vb_print('Cached start position: {0}'.format(self._start))
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
        # Go back to the previous position
        self._file.seek(current)
        self._vb_print('Measured start position: {0}'.format(self._start))
        return self._start

    def _get_end(self):
        if self._end is not None:
            # Return the cached value
            self._vb_print('Cached end position: {0}'.format(self._start))
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
        self._vb_print('Measured end position: {0}'.format(self._start))
        return self._end

    def _init_log(self):
        if self._mode == 'r':
            self._vb_print('Initialising log for reading.')
            # Read out the metadata
            self._meta = self._read()
            # Grab the position of the first entry and make it the current
            self._cur_pos = self._get_start()
            self._start = self._cur_pos
            self._end = None
            self._next = None
        else:
            self._vb_print('Initialising log for writing.')
            # Write the metadata
            self._write(self._meta)
            self._write_ind = 1

    def _read(self):
        '''Read a single entry from the log.'''
        self._vb_print('Reading one data block.')
        try:
            data = pickle.load(self._file)
        except EOFError:
            self._vb_print('End of log reached.')
            self._eof = True
            raise ilog.EndOfLogError
        return data

    def _shift_to_index(self, ind):
        '''Shifts forward or backward in the log to find the given index.'''
        if ind == cur[0]:
            self._vb_print('Shift by index: already at destination.')
            return
        elif ind < cur[0]:
            # Rewind
            # TODO: Rewinding may be more efficient in many cases if done by
            # fast-forwarding from the start of the file rather than traversing
            # backwards.
            self._vb_print('Rewinding to index {0}.'.format(ind))
            self._backup_one()
            while self._next[0] > ind:
                self._backup_one()
        else:
            # Fast-forward
            self._vb_print('Fast-forwarding to index {0}.'.format(ind))
            if self._next is None:
                self._next = self._read()
            while self._next[0] < ind:
                self._next = self._read()
            self._update_cur_pos(self._next)
        self._vb_print('New current position is {0}.'.format(self._cur_pos))

    def _shift_to_timestamp(self, ts):
        '''Shifts forward or backward in the log to find the given timestamp.'''
        if ts == cur[1]:
            self._vb_print('Shift by timestamp: already at destination.')
            return
        elif ts < cur[1]:
            # Rewind
            self._vb_print('Rewinding to timestamp {0}.'.format(ts))
            self._backup_one()
            while self._next[1] > ts:
                self._backup_one()
        else:
            self._vb_print('Fast-forwarding to timestamp {0}.'.format(ts))
            # Fast-forward
            if self._next is None:
                self._next = self._read()
            while self._next[0] < ind:
                self._next = self._read()
            self._update_cur_pos(self._next)
        self._vb_print('New current position is {0}.'.format(self._cur_pos))

    def _update_cur_pos(self, val):
        '''Updates the current pos from a data entry.'''
        self._cur_pos = (val[0], val[1])

    def _write(self, data):
        '''Pickle some data and write it to the file.'''
        self._vb_print('Writing one data block.')
        pickle.dump(data, self._file, pickle.HIGHEST_PROTOCOL)

