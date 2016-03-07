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

rtstart library.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.component
import rtctree.path
import rtctree.tree
import rtsprofile.rts_profile
import sys
import traceback

from rtshell import actions
from rtshell import option_store
from rtshell import plan
from rtshell import rts_exceptions
import rtshell


def check_required_component_actions(rtsprofile):
    checks = []
    # First perform a sanity check of the system.
    # All required components must be present
    for comp in [c for c in rtsprofile.components if c.is_required]:
        checks.append(actions.CheckForRequiredCompAct('/' + comp.path_uri,
            comp.id, comp.instance_name,
            callbacks=[actions.RequiredActionCB()]))
    return checks


def activate_actions(rtsprofile):
    checks = check_required_component_actions(rtsprofile)

    activates = []
    for comp in [c for c in rtsprofile.components if c.is_required]:
        for ec in comp.execution_contexts:
            activates.append(actions.ActivateCompAct('/' + comp.path_uri,
                comp.id, comp.instance_name, ec.id,
                callbacks=[actions.RequiredActionCB()]))

    for comp in [c for c in rtsprofile.components if not c.is_required]:
        for ec in comp.execution_contexts:
            activates.append(actions.ActivateCompAct('/' + comp.path_uri,
                comp.id, comp.instance_name, ec.id))

    return checks, activates


def start(profile=None, xml=True, dry_run=False, tree=None):
    # Load the profile
    if profile:
        # Read from a file
        with open(profile) as f:
            if xml:
                rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=f)
            else:
                rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=f)
    else:
        # Read from standard input
        lines = sys.stdin.read()
        if xml:
            rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=lines)
        else:
            rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=lines)

    # Build a list of actions to perform that will start the system
    checks, activates = activate_actions(rtsp)
    p = plan.Plan()
    p.make(rtsp, activates, rtsp.activation,
            rtctree.component.Component.ACTIVE)
    if dry_run:
        for a in checks:
            print(a)
        print(p)
    else:
        if not tree:
            # Load the RTC Tree, using the paths from the profile
            tree = rtctree.tree.RTCTree(paths=[rtctree.path.parse_path(
                '/' + c.path_uri)[0] for c in rtsp.components])
        try:
            for a in checks:
                a(tree)
            p.execute(tree)
        except rts_exceptions.RequiredActionFailedError:
            p.cancel()
            raise


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [RTSProfile file]
Start an RT system using an RTSProfile.'''
    parser = optparse.OptionParser(usage=usage, version=rtshell.RTSH_VERSION)
    parser.add_option('--dry-run', dest='dry_run', action='store_true',
            default=False, help="Print what will be done but don't actually "
            "do anything. [Default: %default]")
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-x', '--xml', dest='xml', action='store_true',
            default=True, help='Use XML input format. [Default: True]')
    parser.add_option('-y', '--yaml', dest='xml', action='store_false',
            help='Use YAML input format. [Default: False]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1
    option_store.OptionStore().verbose = options.verbose

    if not args:
        profile = None
    elif len(args) == 1:
        profile = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1

    try:
        start(profile=profile, xml=options.xml, dry_run=options.dry_run,
                tree=tree)
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

