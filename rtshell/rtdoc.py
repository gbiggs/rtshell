#!/usr/bin/env python2
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2015
    Yosuke Matsusaka and Geoffrey Biggs
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

Implementation of the command to display component documentation.

'''

from __future__ import print_function

import docutils.core
import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def escape(s):
    return s.replace('"', "'")


def section(s, level=0):
    result = []
    if level == 0:
        result.append(s)
        result.append('=' * len(s))
    elif level == 1:
        result.append(s)
        result.append('-' * len(s))
    return result


def get_ports_docs(comp):
    result = []
    result.append('.. csv-table:: Ports')
    result.append('   :header: "Name", "Type", "DataType", "Description"')
    result.append('   :widths: 8, 8, 8, 26')
    result.append('   ')
    for p in comp.ports:
        if p.porttype == 'DataInPort' or p.porttype == 'DataOutPort':
            datatype = p.properties['dataport.data_type']
        else:
            datatype = ''
        if 'description' in p.properties:
            description = p.properties['description']
        else:
            description = ''
        result.append('   "{0}", "{1}", "{2}", "{3}"'.format(p.name,
            p.porttype, datatype, escape(description)))
    return result


def get_config_docs(comp):
    result = []
    result.append('.. csv-table:: Configuration parameters')
    result.append('   :header: "Name", "Description"')
    result.append('   :widths: 12, 38')
    result.append('   ')

    desc_set = None
    if '__description__' in comp.conf_sets:
        desc_set = comp.conf_sets['__description__']
    for n in comp.conf_sets['default'].data:
        if desc_set and desc_set.has_param(n):
            description = desc_set.data[n]
        else:
            description = ''
        result.append('   "{0}", "{1}"'.format(n, escape(description)))
    return result


from rtshell.rtstodot import port_name as dot_port_name
from rtshell.rtstodot import escape as dot_escape

def make_comp_graph(comp):
    result = []
    result.append('.. digraph:: comp')
    result.append('')
    result.append('   rankdir=LR;')
    result.append('   {0} [shape=Mrecord, label="{1}"];'.format(dot_escape(comp.type_name), comp.type_name))
    for p in comp.ports:
        if p.porttype == 'DataInPort':
            pname = dot_port_name(p.name)
            result.append('   {0} [shape=plaintext, label="{1}"];'.format(dot_escape(pname), pname))
            result.append('   {0} -> {1};'.format(dot_escape(pname), dot_escape(comp.type_name)))
        elif p.porttype == 'DataOutPort':
            pname = dot_port_name(p.name)
            result.append('   {0} [shape=plaintext, label="{1}"];'.format(dot_escape(pname), pname))
            result.append('   {0} -> {1};'.format(dot_escape(comp.type_name), dot_escape(pname)))
    return result


def get_section_title(sec):
    if sec == 'intro':
        return 'Introduction'
    elif sec == 'reqs':
        return 'Pre-requisites'
    elif sec == 'install':
        return 'Installation'
    elif sec == 'usage':
        return 'Usage'
    elif sec == 'misc':
        return 'Miscellaneous'
    elif sec == 'changelog':
        return 'Changelog'
    else:
        return sec


def do_section(result, comp, doc_set, sec, options):
    if sec == 'ports' and comp.ports:
        result += section('Ports', 1)
        result += get_ports_docs(comp)
        result.append('')
        if options.graph == True:
            result += make_comp_graph(comp)
            result.append('')
    elif (sec == 'config' and
            'default' in comp.conf_sets and comp.conf_sets['default'].data):
        result += section('Configuration parameters', 1)
        result += get_config_docs(comp)
        result.append('')
    elif doc_set and doc_set.has_param(sec):
        title = get_section_title(sec)
        body = doc_set.data[sec]
        result += section(title, 1)
        result.append(doc_set.data[sec])
        result.append('')


def get_comp_docs(comp, tree, options):
    result = []
    result += section(comp.type_name, 0)
    result.append(comp.description)
    result.append('')

    result.append(':Vendor: {0}'.format(comp.vendor))
    result.append(':Version: {0}'.format(comp.version))
    result.append(':Category: {0}'.format(comp.category))

    doc_set = None
    order = ['intro', 'reqs', 'install', 'usage', 'ports', 'config', 'misc',
            'changelog']
    sections = ['ports', 'config']
    if '__doc__' in comp.conf_sets:
        doc_set = comp.conf_sets['__doc__']
        if doc_set.has_param('__order__') and doc_set.data['__order__']:
            order = doc_set.data['__order__'].split(',')
        sections += [k for k in list(doc_set.data.keys()) if not k.startswith('__')]

    if doc_set:
        if doc_set.has_param('__license__'):
            result.append(':License: {0}'.format(
                comp.conf_sets['__doc__'].data['__license__']))
        if doc_set.has_param('__contact__'):
            result.append(':Contact: {0}'.format(
                comp.conf_sets['__doc__'].data['__contact__']))
        if doc_set.has_param('__url__'):
            result.append(':URL: {0}'.format(
                comp.conf_sets['__doc__'].data['__url__']))
    result.append('')

    # Add sections specified in the ordering first
    for s in order:
        if s not in sections:
            if doc_set:
                print('{0}: Unknown section in order: {1}'.format(
                    os.path.basename(sys.argv[0]), s), file=sys.stderr)
            continue
        do_section(result, comp, doc_set, s, options)

    # Add any sections that were not in the ordering last
    for s in [s for s in sections if s not in order]:
        do_section(result, comp, doc_set, s, options)

    return result


def get_docs(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if not path[-1]:
        # There was a trailing slash
        raise rts_exceptions.NotAComponentError(cmd_path)
    if port:
        raise rts_exceptions.NotAComponentError(cmd_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path)

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)

    if object.is_component:
        return get_comp_docs(object, tree, options)
    elif object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    else:
        raise rts_exceptions.NotAComponentError(cmd_path)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Display component documentation.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-f', '--format', dest='format', type='choice',
            choices=('rst', 'html', 'latex'), default='html',
            help='Output format (one of "rst", "html" or "latex"). '
            '[Default: %default]')
    parser.add_option('-g', '--graph', dest='graph', action='store_true',
            default=False,
            help='Draw component graph. [Default: %default]')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    if not args:
        # If no path given then can't do anything.
        print('{0}: No component specified.'.format(os.path.basename(sys.argv[0])),
                file=sys.stderr)
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        docs = '\n'.join(get_docs(cmd_path, full_path, options, tree=tree))
        if options.format == 'rst':
            print(docs)
        else:
            print(docutils.core.publish_string(docs,
                writer_name=options.format))
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

