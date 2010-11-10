#!/usr/bin/env python

#-----------------------------------------------------------------------------
# rtstodot
#
# A utility script to visualize RTSProfile using graphviz.
#      copyright Yosuke Matsusaka <yosuke.matsusaka@aist.go.jp> 2010
#-----------------------------------------------------------------------------

# Usage:
#  -Visualize current configuration to screen
#   % rtcryo -o - | rtstodot - | dot -T xlib
#  -Output in eps [paste in latex paper]
#   % rtstodot rtsystem.xml | dot -T eps > rtsystem.eps

# History
# 2010/10/05 First version
# 2010/10/10 Adapt to RTC port naming convention

import sys, codecs
from rtsprofile import rts_profile

def usage():
    print "Usage: %s [RTSProfile]" % sys.argv[0]
    print "Examples:"
    print " -Visualize current configuration to screen"
    print "  % rtcryo -o - | rtstodot - | dot -T xlib"
    print " -Output in eps format [can be used in latex paper]"
    print "  % rtstodot rtsystem.xml | dot -T eps > rtsystem.eps"

def port_name(s):
    return s.split('.')[-1]

def escape(s):
    return s.replace('.', '_dot_').replace('/', '_slash_')

def main():
    if (len(sys.argv) != 2):
        usage()
        quit()

    fname = sys.argv[1]
    p = rts_profile.RtsProfile()
    if fname == '-':
        p.parse_from_xml(sys.stdin.read())
    else:
        p.parse_from_xml(open(fname).read())

    print 'digraph rtsprofile {'
    print '  rankdir=LR;'
    print '  node [shape=Mrecord];'

    # use connection info to estimate port direction
    isinport = {}
    isoutport = {}
    for dp in p.data_port_connectors:
        s = dp.source_data_port
        isoutport[(s.instance_name, s.port_name)] = True
        t = dp.target_data_port
        isinport[(t.instance_name, t.port_name)] = True
    for sp in p.service_port_connectors:
        s = sp.source_service_port
        isoutport[(s.instance_name, s.port_name)] = True
        t = sp.target_service_port
        isinport[(t.instance_name, t.port_name)] = True

    # draw components
    for c in p.components:
        inports = []
        outports = []
        for dp in c.data_ports:
            if isinport.has_key((c.instance_name, dp.name)):
                inports.append(port_name(dp.name))
            if isoutport.has_key((c.instance_name, dp.name)):
                outports.append(port_name(dp.name))
        for sp in c.service_ports:
            if isinport.has_key((c.instance_name, sp.name)):
                inports.append(port_name(sp.name))
            if isoutport.has_key((c.instance_name, sp.name)):
                outports.append(port_name(sp.name))
        inportstr = '|'.join(['<%s>%s' % (n,n) for n in inports])
        outportstr = '|'.join(['<%s>%s' % (n,n) for n in outports])
        labelstr = '{{%s}|%s|{%s}}' % (inportstr, c.instance_name, outportstr)
        print '  %s [label="%s"];' % (escape(c.instance_name), labelstr)

    # draw connections
    for dp in p.data_port_connectors:
        s = dp.source_data_port
        t = dp.target_data_port
        print '  %s:%s -> %s:%s;' % (escape(s.instance_name), port_name(s.port_name), escape(t.instance_name), port_name(t.port_name))
    for sp in p.service_port_connectors:
        s = sp.source_service_port
        t = sp.target_service_port
        print '  %s:%s -> %s:%s [arrowhead="odot"];' % (escape(s.instance_name), port_name(s.port_name), escape(t.instance_name), port_name(t.port_name))

    print '}'

if __name__ == '__main__':
    sys.exit(main())
