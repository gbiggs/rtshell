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

Implementation of the command for controlling managers.

'''

from __future__ import print_function

import rtctree
import rtctree.exceptions
import rtctree.path
import rtctree.tree
import CosNaming
import omniORB
import optparse
import os
import os.path
import re
import OpenRTM_aist
import RTC
import RTM
import sys
import traceback

from rtshell import rts_exceptions
from rtshell import path
import rtshell


class DirectManager(object):
    def __init__(self, address):
        self._connect(self._fix_address(address))

    def _connect(self, address):
        if rtctree.ORB_ARGS_ENV_VAR in os.environ:
            orb_args = os.environ[ORB_ARGS_ENV_VAR].split(';')
        else:
            orb_args = []
        self._orb = omniORB.CORBA.ORB_init(orb_args)
        try:
            self._obj = self._orb.string_to_object(address)
        except omniORB.CORBA.ORB.InvalidName:
            raise rts_exceptions.BadMgrAddressError
        try:
            self._mgr = self._obj._narrow(RTM.Manager)
        except omniORB.CORBA.TRANSIENT as e:
            if e.args[0] == omniORB.TRANSIENT_ConnectFailed:
                raise rts_exceptions.BadMgrAddressError
            else:
                raise
        if omniORB.CORBA.is_nil(self._mgr):
            raise rts_exceptions.FailedToNarrowError

    def _fix_address(self, address):
        parts = address.split(':')
        if len(parts) == 3:
            # No port
            host, sep, id_ = parts[2].partition('/')
            if not id_:
                # No ID
                id_ = 'manager'
            parts[2] = '{0}:2810/{1}'.format(host, id_)
        elif len(parts) == 4:
            # Have a port
            port, sep, id_ = parts[3].partition('/')
            if not id_:
                # No ID
                id_ = 'manager'
                parts[3] = '{0}/{1}'.format(port, id_)
        else:
            raise rts_exceptions.BadMgrAddressError
        return ':'.join(parts)

    def load_module(self, path, init_func):
        try:
            if self._mgr.load_module(path, init_func) != RTC.RTC_OK:
                raise rtctree.exceptions.FailedToLoadModuleError(path)
        except omniORB.CORBA.UNKNOWN as e:
            if e.args[0] == UNKNOWN_UserException:
                raise rtctree.exceptions.FailedToLoadModuleError(path,
                        'CORBA User Exception')
            else:
                raise

    def unload_module(self, path):
        if self._mgr.unload_module(path) != RTC.RTC_OK:
            raise rtctree.exceptions.FailedToUnloadModuleError(path)

    def create_component(self, module_name):
        if not self._mgr.create_component(module_name):
            raise rtctree.exceptions.FailedToCreateComponentError(module_name)

    def delete_component(self, instance_name):
        if not self._mgr.delete_component(instance_name) != RTC.RTC_OK:
            raise rtctree.exceptions.FailedToDeleteComponentError(instance_name)


def get_manager(cmd_path, full_path, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotAManagerError(cmd_path)

    if not path[-1]:
        # There was a trailing slash - ignore it
        path = path[:-1]

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    object = tree.get_node(path)
    if not object:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not object.is_manager:
        raise rts_exceptions.NotAManagerError(cmd_path)
    return tree, object

def load_module(mgr, module_info):
    module_path, init_func = module_info
    mgr.load_module(module_path, init_func)


def unload_module(mgr, module_path):
    mgr.unload_module(module_path)


def create_component(mgr, module_name):
    mgr.create_component(module_name)


def delete_component(mgr, instance_name):
    mgr.delete_component(instance_name)


def main(argv=None, tree=None):
    def cmd_cb(option, opt, val, parser):
        if not hasattr(parser.values, 'cmds'):
            setattr(parser.values, 'cmds', [])
        if opt == '-l' or opt == '--load':
            # Check the module path is correct before executing any commands
            items = re.split(':([^/]+)', val)
            if len(items) != 3:
                raise optparse.OptionValueError('No initialisation function '
                    'specified.')
            parser.values.cmds.append((load_module, items[0:2]))
        elif opt == '-c' or opt == '--create':
            parser.values.cmds.append((create_component, val))
        elif opt == '-d' or opt == '--delete':
            parser.values.cmds.append((delete_component, val))
        elif opt == '-u' or opt == '--unload':
            parser.values.cmds.append((unload_module, val))

    usage = '''Usage: %prog [options] <path>
Create and remove components with a manager.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--create', action='callback', callback=cmd_cb,
            type='string', help='Create a new component instance from the '
            'specified loaded module. Properties of the new component an be '
            'specified after the module name prefixed with a question mark. '
            'e.g. ConsoleIn?instance_name=bleg&another_param=value')
    parser.add_option('-d', '--delete', action='callback', callback=cmd_cb,
            type='string', help='Shut down and delete the specified component '
            'instance.')
    parser.add_option('-l', '--load', action='callback', callback=cmd_cb,
            type='string', help='Load the module into the manager. An '
            'initialisation function must be specified after the module path '
            'separated by a ":".')
    parser.add_option('-u', '--unload', action='callback', callback=cmd_cb,
            type='string', help='Unload the module from the manager.')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    options, args = parser.parse_args()

    if len(args) != 1:
        print('{0}: No manager specified.'.format(
                os.path.basename(sys.argv[0])), file=sys.stderr)
        return 1

    try:
        if args[0].startswith('corbaloc::'):
            # Direct connection to manager
            mgr = DirectManager(args[0])
        else:
            # Access via the tree
            full_path = path.cmd_path_to_full_path(args[0])
            tree, mgr = get_manager(args[0], full_path, tree)

        if not hasattr(options, 'cmds'):
            print('{0}: No commands specified.'.format(
                    os.path.basename(sys.argv[0])), file=sys.stderr)
            return 1

        for c in options.cmds:
            c[0](mgr, c[1])
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), e),
                file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

