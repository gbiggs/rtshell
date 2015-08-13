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

Pickle-based log.

'''


import copy
import os
import pickle
import traceback

from rtshell import ilog


###############################################################################
## Current position pointer

class CurPos(object):
    def __init__(self, index=0, timestamp=0, prev_pos=0, cache=0, file_pos=0):
        super(CurPos, self).__init__()
        self.index = index
        self.ts = timestamp
        self.prev = prev_pos
        self.cache = cache
        self.fp = file_pos

    def __str__(self):
        return 'Index: {0}, timestamp: {1}, previous position: {2}, cache '\
                'position: {3}, file position: {4}'.format(self.index, self.ts,
                        self.prev, self.cache, self.fp)


###############################################################################
## Simple pickle-based log object. Its support for the full log interface
## is rudimentary and slow (although writing and simple reading should be fast
## enough).
##
## The simple pickle-based format is as follows (each entry is serialised):
## Port specification (in the metadata block)
## [Data entries: (Index, Time stamp, Data)]

class SimplePickleLog(ilog.Log):
    # Indices in data entries for bits of data
    INDEX = 0
    TS = 1
    DATA = 2
    FP = 3
    PREV = 4
    # Spare space at the start for pointers
    BUFFER_SIZE = 256

    def __init__(self, filename='', *args, **kwargs):
        self._is_open = False
        self._fn = filename
        self._cur_pos = CurPos()
        self._start = None
        self._end = None
        self._next = None
        self._write_ind = 0
        self._prev_pos = 0
        super(SimplePickleLog, self).__init__(*args, **kwargs)

    def __str__(self):
        return 'SimplePickleLog({0}, {1}) at position {2}.'.format(self._fn,
                self._mode, self._cur_pos)

    def write(self, timestamp, data):
        val = (self._write_ind, timestamp, data, self._file.tell(), self._prev_pos)
        # Track the start of the last entry for later writing at the file start
        self._cur_pos.ts = timestamp
        self._end = copy.copy(self._cur_pos)
        # Record the new "previous" position before writing
        self._prev_pos = self._file.tell()
        self._write(val)
        # Update the current position to after the new final record
        self._cur_pos.index = val[self.INDEX] + 1
        self._cur_pos.ts = -1
        self._cur_pos.prev = self._prev_pos
        self._cur_pos.cache = self._prev_pos
        self._cur_pos.fp = self._file.tell()
        self._write_ind += 1
        self._vb_print('Wrote entry at ({0}, {1}, {2}, {3}).'.format(
            val[self.INDEX], val[self.TS], val[self.FP], val[self.PREV]))

    def read(self, timestamp=None, number=None):
        if number is not None:
            return self._read_number(number)
        elif timestamp is not None:
            return self._read_to_timestamp(timestamp)
        else:
            return self._read_single_entry()

    def rewind(self):
        self._vb_print('Rewinding log from position {0}.'.format(
                self._cur_pos))
        if self._mode == 'r':
            self._file.seek(0)
        else:
            self._file.truncate()
        self._write_ind = 0
        self._init_log()

    def seek(self, timestamp=None, index=None):
        self._vb_print('Seeking log from position {0}.'.format(self._cur_pos))
        if index is not None:
            self._seek_to_index(index)
        elif timestamp is not None:
            self._seek_to_timestamp(timestamp)
        # Do nothing if neither is set
        self._vb_print('New current position: {0}.'.format(self._cur_pos))

    def _backup_one(self):
        '''Reverses in the log one entry.'''
        self._vb_print('Backing up one entry from {0}.'.format(self._cur_pos))
        if self._cur_pos.index == 0:
            # Already at the start
            self._vb_print('Backup already at start.')
            return
        else:
            self._next = None
            target = self._cur_pos.prev
            # Move back in the file one entry
            self._file.seek(target)
            # Update the next pointer
            self._next = self._read()
            self._update_cur_pos(self._next)
        self._vb_print('New current position: {0}.'.format(self._cur_pos))

    def _close(self):
        if not self._is_open:
            return
        if self._mode == 'w':
            # Go back to the beginning and write the end position
            self._file.seek(0)
            self._file.seek(self._buf_start) # Skip the meta data
            self._write(self._end)
            self._vb_print('Wrote end pointer: {0}'.format(self._end))
            self._file.close()
            self._is_open = False
            self._start = None
            self._end = None
            self._vb_print('Closed file.')

    def _eof(self):
        return self._next is None

    def _get_cur_pos(self):
        self._vb_print('Current position: {0}'.format(self._cur_pos))
        return self._cur_pos.index, self._cur_pos.ts

    def _get_start(self):
        if self._start is None:
            self._set_start()
        self._vb_print('Start position: {0}'.format(self._start))
        return (self._start.index, self._start.ts)

    def _get_end(self):
        self._vb_print('End position: {0}'.format(self._end))
        return (self._end.index, self._end.ts)

    def _init_log(self):
        if self._mode == 'r':
            self._vb_print('Initialising log for reading.')
            # Read out the metadata
            self._meta = self._read()
            pos = self._file.tell()
            # Read the end marker
            self._end = self._read()
            # Skip to the start of the data
            self._file.seek(pos + self.BUFFER_SIZE)
            self._vb_print('Read end position: {0}'.format(self._end))
            # Grab the position of the first entry and make it the current
            self._set_start()
            self._cur_pos = copy.copy(self._start)
            # Get the first entry
            self._next = self._read()
        else:
            self._vb_print('Initialising log for writing.')
            # Write the metadata
            self._write(self._meta)
            self._vb_print('Wrote meta data of length {0}'.format(
                self._file.tell()))
            self._buf_start = self._file.tell()
            # Put some blank space to write the end marker
            self._file.write(''.ljust(self.BUFFER_SIZE))
            self._vb_print('Wrote buffer of length {0} at position {1}'.format(
                self.BUFFER_SIZE, self._buf_start))
            self._write_ind = 0
            self._prev_pos = 0
            self._cur_pos = CurPos(file_pos=self._file.tell())
            self._vb_print('First entry will be written at {0}'.format(
                self._cur_pos))

    def _open(self):
        if self._is_open:
            return
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

    def _read(self):
        '''Read a single entry from the log.'''
        self._vb_print('Reading one data block at {0}.'.format(
            self._file.tell()))
        try:
            data = pickle.load(self._file)
        except EOFError:
            self._vb_print('End of log reached.')
            raise ilog.EndOfLogError
        return data

    def _read_number(self, number):
        self._vb_print('Reading {0} entries.'.format(number))
        res = []
        if number < 0:
            raise ValueError
        if not self._next:
            self._vb_print('End of log before reading.')
            return []
        try:
            for ii in range(number):
                res.append((self._next[self.INDEX], self._next[self.TS],
                    self._next[self.DATA]))
                self._next = self._read()
                if not self._next:
                    self._set_eof_pos()
                    self._vb_print('End of log during reading, current '\
                            'position is {1}.'.format(self._cur_pos))
                    break
                self._update_cur_pos(self._next)
                self._vb_print('Read entry {0} of {1}, current position '\
                        'is {2}.'.format(ii + 1, number, self._cur_pos))
        except ilog.EndOfLogError:
            self._set_eof_pos()
            self._next = None
            self._vb_print('End of log while reading, current '\
                    'position is {0}.'.format(self._cur_pos))
        self._vb_print('Finished reading; current position is ' \
                '{0}.'.format(self._cur_pos))
        return res

    def _read_to_timestamp(self, timestamp):
        self._vb_print('Reading until time stamp {0}.'.format(timestamp))
        res = []
        if timestamp < 0:
            raise ValueError
        if not self._next:
            self._vb_print('End of log before reading.')
            return []
        if self._cur_pos.ts > timestamp:
            # The time limit is before the next item - nothing to read
            self._vb_print('Current position is beyond the time limit.')
            return []
        try:
            while self._next[self.TS] <= timestamp:
                res.append((self._next[self.INDEX], self._next[self.TS],
                    self._next[self.DATA]))
                self._next = self._read()
                if not self._next:
                    self._set_eof_pos()
                    self._vb_print('End of log during reading, current '\
                            'position is {1}.'.format(self._cur_pos))
                    break
                self._update_cur_pos(self._next)
                self._vb_print('Read entry at time index {0}, current '\
                        'position is {1}.'.format(res[-1][1], self._cur_pos))
        except ilog.EndOfLogError:
            self._set_eof_pos()
            self._next = None
            self._vb_print('End of log while reading, current '\
                    'position is {0}.'.format(self._cur_pos))
        self._vb_print('Finished reading; current position is ' \
                '{0}.'.format(self._cur_pos))
        return res

    def _read_single_entry(self):
        self._vb_print('Reading a single entry.')
        if not self._next:
            self._vb_print('End of log before reading.')
            return []
        else:
            res = [(self._next[self.INDEX], self._next[self.TS],
                self._next[self.DATA])]
            try:
                self._next = self._read()
            except ilog.EndOfLogError:
                self._next = None
            if not self._next:
                self._set_eof_pos()
                self._vb_print('End of log during reading, current '\
                        'position is {0}.'.format(self._cur_pos))
            else:
                self._update_cur_pos(self._next)
                self._vb_print('Read entry, current position is ' \
                        '{0}.'.format(self._cur_pos))
            self._vb_print('Cached next entry is {0}'.format(self._next))
            return res

    def _seek_to_index(self, ind):
        '''Seeks forward or backward in the log to find the given index.'''
        if ind == self._cur_pos.index:
            self._vb_print('Seek by index: already at destination.')
            return
        if ind < 0:
            raise ilog.InvalidIndexError
        elif ind < self._cur_pos.index:
            # Rewind
            # TODO: Rewinding may be more efficient in many cases if done by
            # fast-forwarding from the start of the file rather than traversing
            # backwards.
            self._vb_print('Rewinding to index {0}.'.format(ind))
            while self._cur_pos.index > ind and self._cur_pos.index > 0:
                self._backup_one()
        else:
            # Fast-forward
            self._vb_print('Fast-forwarding to index {0}.'.format(ind))
            while self._cur_pos.index < ind:
                if not self.read():
                    break # EOF
        self._vb_print('New current position is {0}.'.format(self._cur_pos))

    def _seek_to_timestamp(self, ts):
        '''Seeks forward or backward in the log to find the given timestamp.'''
        if ts == self._cur_pos.ts and not self.eof:
            self._vb_print('Seek by timestamp: already at destination.')
            return
        elif ts < self._cur_pos.ts or self.eof:
            # Rewind
            self._vb_print('Rewinding to timestamp {0}.'.format(ts))
            while (self._cur_pos.ts > ts and self._cur_pos.index > 0) or \
                    self.eof:
                self._backup_one()
            # Need to move one forward again, unless have hit the beginning
            if self._cur_pos.ts < ts:
                self.read()
        else:
            self._vb_print('Fast-forwarding to timestamp {0}.'.format(ts))
            # Fast-forward
            while self._cur_pos.ts < ts:
                if not self.read():
                    break # EOF
        self._vb_print('New current position is {0}.'.format(self._cur_pos))

    def _set_eof_pos(self):
        '''Sets the current position to the end-of-file value.'''
        self._vb_print('Setting EOF at file position {0}, prev cur pos '\
                '{1}'.format(self._file.tell(), self._cur_pos))
        self._cur_pos.index += 1 # The "next" index
        # Don't touch the time stamp (indicates the end time of the file)
        self._cur_pos.prev = self._cur_pos.cache # This is the final entry
        self._cur_pos.cache = 0 # No valid entry at current file position
        self._cur_pos.fp = self._file.tell() # This is the end of the file

    def _set_start(self):
        # Save the current position
        current = self._file.tell()
        # Move to the start
        self._file.seek(0)
        # Skip the metadata block
        self._read()
        # Skip the buffer
        self._file.seek(self.BUFFER_SIZE, os.SEEK_CUR)
        # Read the first entry
        pos = self._file.tell()
        entry = self._read()
        self._start = CurPos(entry[self.INDEX], entry[self.TS],
                entry[self.PREV], pos, self._file.tell())
        self._file.seek(current)
        self._vb_print('Measured start position: {0}'.format(self._start))

    def _update_cur_pos(self, val):
        '''Updates the current pos from a data entry.'''
        self._cur_pos.index = val[self.INDEX]
        self._cur_pos.ts = val[self.TS]
        self._cur_pos.prev = val[self.PREV]
        self._cur_pos.cache = self._cur_pos.fp
        self._cur_pos.fp = self._file.tell()

    def _write(self, data):
        '''Pickle some data and write it to the file.'''
        self._vb_print('Writing one data block.')
        pickle.dump(data, self._file, pickle.HIGHEST_PROTOCOL)

