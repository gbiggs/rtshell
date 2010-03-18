#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: rtact.py

Implementation of the command to move a component to the activated state.

'''

# $Source$


import sys

from rtcshell.state_control_base import base_main


def activate_action(object, ec_index):
    object.activate_in_ec(ec_index)
    return 0


def main(argv=None, tree=None):
    return base_main('Activate a component.', activate_action, argv)


# vim: tw=79

