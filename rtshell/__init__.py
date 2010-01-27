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

File: __init__.py

Commands for managing RT Components and RTM-based systems from a shell.

'''

__version__ = '$Revision: $'
# $Source$


RTSH_PATH_USAGE =\
'''A path is the address of object. Name servers and subcontexts on name
servers are considered directories. Managers and RT Components are considered
objects. As with the POSIX 'cat' command, the path specified as an argument to
this command is appended to the current rtcsh working directory, which is
stored in the RTCSH_CWD environment variable and changeable using the rtcd
command.

The name servers that are contacted will depend on the contents of the
RTCSH_NAMESERVERS environment variable.

For example, '/localhost/comp0.rtc' refers to the component named 'comp0.rtc'
registered on the name server at 'localhost'. '/localhost/manager/comp0.rtc'
refers to the component 'comp0.rtc' in the directory 'manager' on the
'localhost' name server. 'comp0.rtc' refers to that component in the current
directory.'''
RTSH_VERSION = '1.0.0'


# vim: tw=79

