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

Implementation of the command to move a component from the error state to the
inactive state.

'''


from rtshell import state_control_base


def reset_action(object, ec_index):
    object.reset_in_ec(ec_index)


def main(argv=None, tree=None):
    return state_control_base.base_main('Reset a component.', reset_action,
            argv)


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

