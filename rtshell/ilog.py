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

Log interface.

'''


import sys


###############################################################################
## Log exceptions.

class EndOfLogError(EOFError):
    '''The end of the log has been reached while reading.'''
    pass


class InvalidIndexError(EOFError):
    '''An invalid index was requested.'''
    pass


###############################################################################
## Log interface. All loggers must conform to this.

class Log(object):
    def __init__(self, mode='r', meta=None, verbose=False, *args, **kwargs):
        '''Base constructor.

        The log will be opened on construction. It should be closed manually,
        as Python does not guarantee that __del__() will be called.

        @param mode Permissions. Specificy 'r' for read, 'w' for write or 'rw'
                    for read/write. Not all logs support all permissions.
                    Read/write permissions are particularly uncommon.
        @param meta A block of data to write into the log. Implementations
                    are free to deal with this any way they wish, as long as it
                    can be retrieved in read mode. However, there is no
                    requirement that it can be changed after opening the log
                    for writing. Users should set it before opening the log.
        @param verbose Print verbose output to stderr.

        '''
        super(Log, self).__init__()
        self._mode = mode
        self._meta = meta
        self._vb = verbose
        self.open()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == None:
            self.close(finalise=True)
        else:
            self.close(finalise=False)
        return False

    def __iter__(self):
        return self

    def next(self):
        d = self.read()
        if not d:
            raise StopIteration
        return d[0]

    def __str__(self):
        return 'Log interface object.'

    @property
    def end(self):
        '''The position of the final entry in the log.

        A tuple of (index, timestamp).

        '''
        return self._get_end()

    @property
    def eof(self):
        '''True if the log has reached the end.'''
        return self._eof()

    @property
    def metadata(self):
        '''Return the metadata from the log (if any).'''
        return self._meta

    @metadata.setter
    def metadata(self, metadata):
        self._meta = metadata

    @property
    def mode(self):
        '''The mode of the log.'''
        return self._mode

    @property
    def name(self):
        '''The name of the log.'''
        return self._name

    @property
    def pos(self):
        '''The current position in the log.

        A tuple of (index, timestamp).

        This points at the current position - i.e. the entry most recently
        read.

        '''
        return self._get_cur_pos()

    @property
    def start(self):
        '''The position of the first entry in the log.

        A tuple of (index, timestamp).

        '''
        return self._get_start()

    def open(self):
        '''Opens the log.'''
        self._open()

    def finalise(self):
        '''Prepare the log to be closed.

        Any cleaning up that needs to be done before closing the log should
        be done here.

        This function is called just before closing the log by @ref close.
        If using the context manager statement (the 'with' statement), it will
        be called automatically, unless an exception has occured.

        It is not required for objects implementing the Log interface to
        implement this function.

        '''
        self._finalise()

    def close(self, finalise=True):
        '''Closes the log.

        @param finalise Whether the log should be finalised before closing.
                        Defaults to True.

        '''
        if finalise:
            self.finalise()
        self._close()

    def write(self, timestamp, data):
        '''Writes an entry to the log.

        The timestamp is necessary to allow reading back data at the
        same rate as it was recorded. It must be an object that
        supports comparisons using <, <=, =, >= and >.

        '''
        raise NotImplementedError

    def read(self, timestamp=None, number=None):
        '''Read entries from the log.

        If a time limit is given, all entries until that time limit is
        reached will be read.

        If a number is given, that number of entries will be returned.
        This option overrides the time limit option.

        If EOF is hit before the requested entries are read, what was
        read will be returned and @ref eof will return True.

        If neither option is given, the next value will be returned.

        Returns a list of tuples, [(index, timestamp, data), ...].

        '''
        raise NotImplementedError

    def rewind(self):
        '''Rewind the log to the first entry.'''
        raise NotImplementedError

    def seek(self, timestamp=None, index=None):
        '''Rewind or fast-forward the log.

        If the timestamp or index is earlier than the current position, the log
        will be rewound. If it is later, the log will be fast-forwarded.

        When the log is rewound, it will go back to the first entry before
        the given timestamp or index. If an entry exactly matches the given
        timestamp or index, the log position will be at that entry, meaning
        that the next value read will be that entry.

        When a log is fast-forwarded, it will go to the first entry after the
        given timestamp or index. If an entry exactly matches the given
        timestamp or index, the log position will be at that entry, meaning
        that the next value read will be that entry.

        '''
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError

    def _finalise(self):
        pass

    def _get_cur_pos(self):
        '''Get the current position in the log.

        Should be implemented by implementation objects. Called by the
        @ref position property.

        '''
        raise NotImplementedError

    def _get_start(self):
        '''Get the position of the first entry in the log.

        Should be implemented by implementation objects. Called by the
        @ref start property.

        '''
        raise NotImplementedError

    def _get_end(self):
        '''Get the position of the last entry in the log.

        Should be implemented by implementation objects. Called by the
        @ref end property.

        '''
        raise NotImplementedError

    def _open(self):
        raise NotImplementedError

    def _vb_print(self, string):
        '''Print verbose information when self._vb is True.'''
        if self._vb:
            print >>sys.stderr, string

