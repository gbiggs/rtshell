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

Log file interface.

'''


###############################################################################
## Log file exceptions.

class EndOfLogError(EOFError):
    '''The end of the log file has been reached while reading.'''
    pass


###############################################################################
## Log file interface. All loggers must conform to this.

class LogFile(object):
    def __init__(self, mode='r', meta=None, verbose=False, *args, **kwargs):
        '''Base constructor.

        @param filename The name of the log file.
        @param mode Permissions. Specificy 'r' for read, 'w' for write or 'rw'
                    for read/write. Not all log files support all permissions.
                    Read/write permissions are particularly uncommon.
        @param meta A block of data to write into the log file. Implementations
                    are free to deal with this any way they wish, as long as it
                    can be retrieved in read mode. However, there is no
                    requirement that it can be changed after opening the log
                    for writing. Users should set it before opening the log.
        @param verbose Print verbose output to stderr.

        '''
        super(LogFile, self).__init__(self)
        self._mode = mode
        self._meta = meta
        self._vb = verbose
        self._eof = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == None:
            self._finalise()
        self.close()
        return False

    def __iter__(self):
        return self

    def __next__(self):
        res = self.read()
        if not res:
            raise StopIteration
        return res

    def __str__(self):
        return 'Log file interface object.'

    @property
    def end(self):
        '''The position of the final entry in the log file.

        A tuple of (index, timestamp).

        '''
        return self._get_end()

    @property
    def eof(self):
        '''True if the log file has reached the end.'''
        return self._eof

    @property
    def metadata(self):
        '''Return the metadata from the log file (if any).'''
        return self._meta

    @metadata.setter
    def metadata(self, metadata):
        self._meta = metadata

    @property
    def mode(self):
        '''The mode of the log file.'''
        return self._mode

    @property
    def name(self):
        '''The name of the log file.'''
        return self._name

    @property
    def position(self):
        '''The current position in the log file.

        A tuple of (index, timestamp).

        This points at the current position - i.e. the entry most recently
        read.

        '''
        return self._get_cur_pos()

    @property
    def start(self):
        '''The position of the first entry in the log file.

        A tuple of (index, timestamp).

        '''
        return self._get_start()

    def open(self):
        '''Opens the log file.'''
        pass

    def finalise(self):
        '''Prepare the log file to be closed.

        Any cleaning up that needs to be done before closing the log file should
        be done here.

        This function is meant to be called just before closing the log file.
        If using the context manager statement (the 'with' statement), it will
        be called automatically before @ref close is called, unless an exception
        has occured.

        It is not required for objects implementing the LogFile interface to
        implement this function.

        '''
        pass

    def close(self):
        '''Closes the log file.

        '''
        pass

    def write(self, timestamp, data):
        '''Writes an entry to the log file.

        The timestamp is necessary to allow reading back data at the
        same rate as it was recorded. It must be an object that
        supports comparisons using <, <=, =, >= and >.

        '''
        raise NotImplementedError

    def read(self, time_limit=None, number=None):
        '''Read entries from the log file.

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
        '''Rewind the log file to the first entry.'''
        self._eof = False

    def shift(self, timestamp=None, index=None):
        '''Rewind or fast-forward the log file.

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
        self._eof = False

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

