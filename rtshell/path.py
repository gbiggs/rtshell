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

Functions for dealing with input paths.

'''


import os


ENV_VAR='RTCSH_CWD'


def cmd_path_to_full_path(cmd_path):
    '''Given a path from the user, returns a suitable full path based on the
    value of the environment variable specified in ENV_VAR.

    '''
    if cmd_path.startswith('/'):
        return cmd_path
    if ENV_VAR in os.environ and os.environ[ENV_VAR]:
        if os.environ[ENV_VAR].endswith('/') or cmd_path.startswith('/'):
            return os.environ[ENV_VAR] + cmd_path
        else:
            return os.environ[ENV_VAR] + '/' + cmd_path
    # If ENV_VAR is not set, assume the current working dir is the root dir
    return '/' + cmd_path


# vim: tw=79

