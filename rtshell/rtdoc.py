#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Yosuke Matsusaka and Geoffrey Biggs
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of the command to display component document.

'''


import optparse
import os
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import rtctree.utils
import SDOPackage
import sys
import traceback

import path
import rts_exceptions
import rtshell

from docutils.core import publish_string


def format_ports(ports, comp):
    result = []
    result.append('.. csv-table:: Ports')
    result.append('   :header: "Name", "Type", "DataType", "Description"')
    result.append('   ')
    for p in ports:
        datatype = p.properties['dataport.data_type']
        try:
            description = p.properties['dataport.description']
        except KeyError:
            description = ''
        result.append('   "{0}", "{1}", "{2}", "{3}"'.format(p.name, p.porttype, datatype, description))
    return result


def format_properties(props, comp):
    result = []
    result.append('.. csv-table:: Configration parameters')
    result.append('   :header: "Name", "Default"')
    result.append('   ')
    for n, v in props.iteritems():
        result.append('   "{0}", "{1}"'.format(n, v))
    return result


def format_component(object, tree):
    result = []
    result.append(object.name)
    result.append('=' * len(object.name))
    result.append(object.description)

    result.append('{0}: {1}'.format('develped by', object.vendor))
    result.append('{0}: {1}'.format('version', object.version))
    result.append('')

    result += format_ports(object.ports, object)
    result.append('')

    result += format_properties(object.active_conf_set.data, object)
    result.append('')

    return result


def cat_target(cmd_path, full_path, options, tree=None):
    result = []
    path, port = rtctree.path.parse_path(full_path)
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]
    else:
        trailing_slash = False

    if not tree:
        tree = rtctree.tree.create_rtctree(paths=path)

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)
    if port:
        pass
    else:
        if object.is_component:
            if trailing_slash:
                raise rts_exceptions.NoSuchObjectError(cmd_path)
            result += format_component(object, tree)
        elif object.is_manager:
            pass
        elif object.is_zombie:
            raise rts_exceptions.ZombieObjectError(cmd_path)
        else:
            raise rts_exceptions.NoSuchObjectError(cmd_path)
    return result


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
Display document about a component in specified (rst, html or latex) format.
''' + rtshell.RTSH_PATH_USAGE
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-f', '--format', dest='format', type='choice',
            choices=('rst', 'html', 'latex'), default='html',
            help='Output format (one of "rst", "html" or "latex"). [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: Cannot cat a directory.'.format(sys.argv[0])
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        result = cat_target(cmd_path, full_path, options, tree=tree)
        if options.format == 'rst':
            print '\n'.join(result)
        else:
            print publish_string('\n'.join(result), writer_name=options.format)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1
    return 0


# vim: tw=79

